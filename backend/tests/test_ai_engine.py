"""Unit tests for the AI engine."""

import pytest

from src.ai_engine import PathogenAIEngine, analyze_sequence_with_ai


def test_engine_initializes():
    engine = PathogenAIEngine()
    assert engine.model is not None
    assert engine.feature_names is None


def test_train_baseline():
    engine = PathogenAIEngine()
    result = engine.train_baseline()
    assert result["status"] == "trained"
    assert result["training_samples"] >= 100
    assert len(result["classes"]) >= 2
    assert "Benign Strain" in result["classes"]


def test_kmer_extraction_length():
    engine = PathogenAIEngine()
    features = engine._extract_k_mers("ACGTACGTACGT", k=3)
    assert len(features) == 64


def test_kmer_short_sequence():
    engine = PathogenAIEngine()
    features = engine._extract_k_mers("AC", k=3)
    assert len(features) == 64
    assert all(f == 0.0 for f in features)


def test_homopolymer_metrics():
    engine = PathogenAIEngine()
    runs, run_len = engine._homopolymer_metrics("AAAAACGTAAAA")
    assert runs >= 2
    assert run_len >= 8


def test_tandem_repeat_units():
    engine = PathogenAIEngine()
    units = engine._tandem_repeat_units("CAGCAGCAGCAGCAG")
    assert units >= 3


def test_risk_score_range():
    engine = PathogenAIEngine()
    score = engine.compute_risk_score("ATCGATCGATCGATCG")
    assert 0 <= score["risk_score"] <= 100
    for key in ("gc_content", "gc_deviation", "homopolymer_runs", "repetitiveness"):
        assert key in score


def test_high_complexity_sequence_low_risk():
    engine = PathogenAIEngine()
    benign = engine.compute_risk_score("ATCGATCGATCGATCGATCGATCGATCGATCG")
    risky = engine.compute_risk_score("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    assert risky["risk_score"] > benign["risk_score"]


def test_predict_sequence():
    engine = PathogenAIEngine()
    engine.train_baseline()
    result = engine.predict_sequence("ACGTACGTACGTACGTACGT")
    assert "predicted_class" in result
    assert 0 <= result["confidence_percent"] <= 100
    assert result["final_score"] >= 0


def test_model_save_load(tmp_path, monkeypatch):
    import os
    import src.ai_engine as ai_mod
    monkeypatch.setattr(ai_mod, "MODEL_PATH", str(tmp_path / "test_model.joblib"))
    engine = PathogenAIEngine()
    engine.train_baseline()
    assert engine.save_model() is True
    loaded = ai_mod._load_model()
    assert loaded is not None
    pred = loaded.predict_sequence("ACGTACGTACGT")
    assert "predicted_class" in pred