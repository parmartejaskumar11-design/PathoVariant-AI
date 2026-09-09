"""Integration tests for the FastAPI application."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "healthy"
    assert body["engine_state"] in ("loaded_from_disk", "trained_in_memory")


def test_model_info():
    r = client.get("/api/model-info")
    assert r.status_code == 200
    assert r.json()["feature_vector_length"] == 64


def test_analyze_with_valid_fasta():
    content = b">seq1\nATCGATCGATCGGGGCCCC\n"
    r = client.post("/api/analyze", files={"file": ("a.fasta", content, "text/plain")})
    assert r.status_code == 200
    body = r.json()
    assert body["sequence_metadata"]["total_sequences"] == 1
    assert body["records"][0]["id"] == "seq1"
    assert body["records"][0]["predicted_class"] in (
        "High-Risk Variant",
        "Moderate Risk",
        "Benign Strain",
    )
    assert "heuristic_details" in body["records"][0]


def test_analyze_empty_file():
    r = client.post("/api/analyze", files={"file": ("a.fasta", b"", "text/plain")})
    assert r.status_code == 400


def test_analyze_invalid_utf8():
    r = client.post("/api/analyze", files={"file": ("a.fasta", b"\xff\xfe\x00", "text/plain")})
    assert r.status_code == 400


def test_header_only_fasta_returns_400():
    content = b">just_a_header\n"
    r = client.post("/api/analyze", files={"file": ("a.fasta", content, "text/plain")})
    assert r.status_code == 400


def test_analyze_batch_two_files():
    content = b">a\nACGTACGTACGTACGTACGT\n"
    r = client.post(
        "/api/analyze-batch",
        files=[
            ("files", ("one.fasta", content, "text/plain")),
            ("files", ("two.fasta", b">b\nACGTACGTACGTACGTACGT\n", "text/plain")),
        ],
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total_files"] == 2
    assert body["grand_total_sequences"] == 2
    assert len(body["per_file"]) == 2


def test_removed_features_return_404():
    assert client.post("/api/variant-call").status_code == 404
    assert client.post("/api/amr").status_code == 404
    assert client.post("/api/phylogeny").status_code == 404
    assert client.post("/api/ncbi/search").status_code == 404
    assert client.get("/api/reference/SARS-CoV-2").status_code == 404