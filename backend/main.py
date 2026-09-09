"""FastAPI entry point for PathoVariant-AI backend.

Single-feature app: AI-powered pathogen sequence analysis (single file + batch).
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import time

from src.parser import parse_fasta_file
from src.ai_engine import PathogenAIEngine, analyze_sequence_with_ai, _load_model

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

# Simple in-memory rate limiter: {client_ip: [timestamps]}
_RATE_LIMIT_COUNT = 30
_RATE_LIMIT_WINDOW_SECONDS = 60
_rate_limits: Dict[str, List[float]] = {}


def _check_rate_limit(client_ip: str) -> None:
    """Enforce a per-IP token bucket for the analyze endpoints."""
    now = time.time()
    timestamps = _rate_limits.get(client_ip, [])
    timestamps = [t for t in timestamps if now - t < _RATE_LIMIT_WINDOW_SECONDS]
    if len(timestamps) >= _RATE_LIMIT_COUNT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait before retrying.")
    timestamps.append(now)
    _rate_limits[client_ip] = timestamps


app = FastAPI(
    title="PathoVariant-AI API",
    description="Autonomous Pathogen Mutation & AI Functional Impact Analyzer",
    version="3.0.0",
)

# Enable CORS for production & frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI engine: load persisted model if available, otherwise train fresh.
ai_engine = _load_model()
engine_loaded_from_disk = ai_engine is not None
if ai_engine is None:
    ai_engine = PathogenAIEngine()

# Warm the model (no-op if already trained & persisted).
_training_result = ai_engine.train_baseline()


# ===================== Helpers =====================

def _decode_upload(contents: bytes) -> str:
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 50 MB size limit")
    try:
        return contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not valid UTF-8 text")


# ===================== Endpoints =====================

@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "PathoVariant-AI API is running",
        "engine_state": "loaded_from_disk" if engine_loaded_from_disk else "trained_in_memory",
        "model_path": os.path.join("data", "pathogen_model.joblib"),
        "training_samples": _training_result.get("training_samples", 0),
    }


@app.get("/api/model-info")
async def model_info() -> Dict[str, Any]:
    """Report the current AI model configuration."""
    return {
        "engine_loaded_from_disk": engine_loaded_from_disk,
        "n_estimators": ai_engine.n_estimators,
        "feature_vector_length": len(ai_engine.feature_names) if ai_engine.feature_names else 64,
        "classes": ai_engine.model.classes_.tolist() if ai_engine.model is not None else [],
        "training_samples": _training_result.get("training_samples", 0),
    }


@app.post("/api/analyze")
async def analyze_fasta_upload(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
    """Analyze an uploaded FASTA file with sequence metadata and AI classification."""
    _check_rate_limit(request.client.host if request.client else "unknown")
    try:
        contents = await file.read()
        uploaded_content = _decode_upload(contents)
        if not uploaded_content.strip():
            raise HTTPException(status_code=400, detail="No file content provided")

        parse_result = parse_fasta_file(uploaded_content)
        if "error" in parse_result:
            raise HTTPException(status_code=400, detail=parse_result["error"])
        if parse_result.get("total_length", 0) == 0:
            raise HTTPException(status_code=400, detail="No sequence data found in the uploaded file")

        records = parse_result.get("records", [])
        total_sequences = parse_result.get("total_sequences", 0)
        overall_gc = parse_result.get("gc_content", 0.0)
        total_length = parse_result.get("total_length", 0)

        classifications = [
            analyze_sequence_with_ai(rec.get("sequence", ""), ai_engine) if rec.get("sequence") else None
            for rec in records
        ]

        # Enrich each record with classification and per-sequence metadata
        detailed_records: List[Dict[str, Any]] = []
        high_risk = moderate_risk = benign = 0
        for i, record in enumerate(records):
            seq_str = record.get("sequence", "")
            cls_result = classifications[i] if i < len(classifications) else None
            cls_result = cls_result if cls_result else {}

            predicted = cls_result.get("predicted_class", "Unknown")
            confidence = cls_result.get("confidence_percent", 0.0)
            if predicted == "High-Risk Variant":
                high_risk += 1
            elif predicted == "Moderate Risk":
                moderate_risk += 1
            else:
                benign += 1

            detail = {
                "id": record.get("id", "unknown"),
                "sequence": seq_str[:50] + "..." if len(seq_str) > 50 else seq_str,
                "full_sequence": seq_str,
                "length": record.get("length", 0),
                "gc_content": record.get("gc_content", 0.0),
                "sequence_type": record.get("sequence_type", "nucleotide"),
                "protein_translation": record.get("protein_translation", ""),
                "base_counts": record.get("base_counts", {}),
                "base_composition": record.get("base_composition", {}),
                "predicted_class": predicted,
                "confidence_percent": confidence,
                "heuristic_score": cls_result.get("final_score", 0.0),
                "heuristic_details": {
                    "gc_deviation": cls_result.get("heuristic", {}).get("gc_deviation", 0.0),
                    "homopolymer_fraction": cls_result.get("heuristic", {}).get("homopolymer_fraction", 0.0),
                    "tandem_repeat_units": cls_result.get("heuristic", {}).get("tandem_repeat_units", 0),
                    "repetitiveness": cls_result.get("heuristic", {}).get("repetitiveness", 0.0),
                },
                "all_probabilities": cls_result.get("all_probabilities", {}),
            }
            detailed_records.append(detail)

        total_a = sum(r.get("base_counts", {}).get("A", 0) for r in records)
        total_t = sum(r.get("base_counts", {}).get("T", 0) for r in records)
        total_g = sum(r.get("base_counts", {}).get("G", 0) for r in records)
        total_c = sum(r.get("base_counts", {}).get("C", 0) for r in records)

        overall_base_composition = {}
        if total_length > 0:
            overall_base_composition = {
                "A": round(total_a / total_length * 100, 2),
                "T": round(total_t / total_length * 100, 2),
                "G": round(total_g / total_length * 100, 2),
                "C": round(total_c / total_length * 100, 2),
            }

        response: Dict[str, Any] = {
            "sequence_metadata": {
                "total_sequences": total_sequences,
                "total_bases": total_length,
                "average_gc_content": round(overall_gc / total_sequences if total_sequences > 0 else 0.0, 2),
                "overall_gc_content": round(overall_gc, 2),
                "base_composition": overall_base_composition,
                "base_counts": {"A": total_a, "T": total_t, "G": total_g, "C": total_c},
            },
            "ai_classifications": {
                "total_classified": len(classifications),
                "high_risk_detections": high_risk,
                "moderate_risk_detections": moderate_risk,
                "benign_count": benign,
                "classification_rate": round(high_risk / total_sequences * 100, 2) if total_sequences > 0 else 0.0,
            },
            "records": detailed_records,
        }
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@app.post("/api/analyze-batch")
async def analyze_batch_endpoint(request: Request, files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    """Analyze multiple FASTA files in a single request.

    Each file is parsed and classified independently; results are grouped
    per file with an overall summary across all uploaded datasets.
    """
    _check_rate_limit(request.client.host if request.client else "unknown")
    if len(files) > 20:
        raise HTTPException(status_code=413, detail="Maximum of 20 files per batch request")

    per_file: List[Dict[str, Any]] = []
    grand_total = 0
    grand_high = 0
    grand_moderate = 0
    grand_benign = 0

    for upload in files:
        contents = await upload.read()
        try:
            uploaded_content = _decode_upload(contents)
        except HTTPException as e:
            per_file.append({"filename": upload.filename, "error": e.detail, "records": []})
            continue

        parse_result = parse_fasta_file(uploaded_content)
        if "error" in parse_result:
            per_file.append({"filename": upload.filename, "error": parse_result["error"], "records": []})
            continue

        records = parse_result.get("records", [])
        file_records = []
        high = moderate = benign = 0
        for rec in records:
            seq_str = rec.get("sequence", "")
            cls_result = analyze_sequence_with_ai(seq_str, ai_engine) if seq_str else None
            predicted = cls_result.get("predicted_class", "Unknown") if cls_result else "Unknown"
            if predicted == "High-Risk Variant":
                high += 1
            elif predicted == "Moderate Risk":
                moderate += 1
            else:
                benign += 1
            file_records.append(
                {
                    "id": rec.get("id", "unknown"),
                    "length": rec.get("length", 0),
                    "gc_content": rec.get("gc_content", 0.0),
                    "predicted_class": predicted,
                    "confidence_percent": cls_result.get("confidence_percent", 0.0) if cls_result else 0.0,
                }
            )

        grand_total += len(records)
        grand_high += high
        grand_moderate += moderate
        grand_benign += benign
        per_file.append(
            {
                "filename": upload.filename,
                "total_sequences": len(records),
                "high_risk": high,
                "moderate_risk": moderate,
                "benign": benign,
                "records": file_records,
            }
        )

    return {
        "total_files": len(files),
        "grand_total_sequences": grand_total,
        "grand_summary": {
            "high_risk": grand_high,
            "moderate_risk": grand_moderate,
            "benign": grand_benign,
        },
        "per_file": per_file,
    }