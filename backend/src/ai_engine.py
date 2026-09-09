"""K-mer feature extraction and RandomForestClassifier for pathogen sequence classification."""

import numpy as np
import math
import os
import random
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
MODEL_PATH = os.path.join(MODEL_DIR, "pathogen_model.joblib")


def _load_model() -> Optional["PathogenAIEngine"]:
    """Load a persisted trained model if one exists."""
    if os.path.exists(MODEL_PATH):
        try:
            import joblib
            return joblib.load(MODEL_PATH)
        except Exception:
            return None
    return None


class PathogenAIEngine:
    """AI engine for pathogen mutation classification.

    Uses a hybrid approach:
      1. A transparent, biology-informed risk score based on GC balance,
         homopolymer runs, tandem repeats, and k-mer repetitiveness.
      2. A RandomForest ensemble trained on synthetic baseline data,
         blended (20%) with the heuristic score for robustness.

    Sequences are classified into:
      - Benign Strain       (low risk)
      - Moderate Risk       (surveillance warranted)
      - High-Risk Variant   (pathogenic mutation signals)
    """

    _CLASS_CENTERS: Dict[str, float] = {
        "Benign Strain": 17.0,
        "Moderate Risk": 47.5,
        "High-Risk Variant": 80.0,
    }

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = None
        self.feature_names = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        from sklearn.ensemble import RandomForestClassifier
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            class_weight="balanced",
        )

    # ============= Feature Extraction =============

    def _extract_k_mers(self, sequence: str, k: int = 3) -> List[float]:
        """Extract normalized k-mer frequency features (length 4^k)."""
        sequence = sequence.upper()
        valid_chars = set("ACGT")
        kmer_counts: Counter = Counter()
        seq_len: int = len(sequence)
        if seq_len < k:
            return [0.0] * (4 ** k)
        for i in range(seq_len - k + 1):
            kmer = sequence[i : i + k]
            if all(c in valid_chars for c in kmer):
                kmer_counts[kmer] += 1
        total_kmers: int = sum(kmer_counts.values())
        feature_vector: List[float] = []

        bases = ["A", "C", "G", "T"]
        for base1 in bases:
            for base2 in bases:
                for base3 in bases:
                    kmer = (base1 + base2 + base3)[:k]
                    freq = kmer_counts.get(kmer, 0) / total_kmers if total_kmers > 0 else 0.0
                    feature_vector.append(freq)
        return feature_vector

    def _homopolymer_metrics(self, seq: str) -> Tuple[int, int]:
        """Return (number_of_runs>=4, total_length_of_runs)."""
        runs = 0
        run_length = 0
        cur = 1
        for i in range(1, len(seq)):
            if seq[i] == seq[i - 1] and seq[i] in "ACGT":
                cur += 1
            else:
                if cur >= 4:
                    runs += 1
                    run_length += cur
                cur = 1
        if cur >= 4:
            runs += 1
            run_length += cur
        return runs, run_length

    def _tandem_repeat_units(self, seq: str) -> int:
        """Count extra tandem trinucleotide repeat units (e.g. CAGCAGCAG).

        Only counts an extra copy beyond 2, so a CAGCAGCAG repeat
        (3 copies) contributes 1 extra unit.
        """
        n = len(seq)
        extra = 0
        i = 0
        while i <= n - 9:
            unit = seq[i : i + 3]
            if len(set(unit)) < 2:
                i += 1
                continue
            length = 3
            while i + length + 3 <= n and seq[i + length : i + length + 3] == unit:
                length += 3
            copies = length // 3
            if copies >= 3:
                extra += copies - 2
                i += length
            else:
                i += 1
        return extra

    def compute_risk_score(self, sequence: str) -> Dict[str, float]:
        """Compute a transparent biological risk score in 0-100.

        Returns dict with the overall score plus interpretable subscores.
        """
        seq = sequence.upper()
        seq_len = max(len(seq), 1)

        # 1. GC deviation (0..1) - highly skewed composition is unusual
        gc = (seq.count("G") + seq.count("C")) / seq_len * 100
        gc_dev = min(1.0, abs(gc - 50.0) / 50.0)

        # 2. Homopolymer runs (0..1) - slippage / frameshift risk
        homopoly_runs, homopoly_len = self._homopolymer_metrics(seq)
        homopoly_frac = min(1.0, homopoly_len / seq_len)

        # 3. Tandem trinucleotide repeats (0..1)
        tandem_frac = min(1.0, self._tandem_repeat_units(seq) * 3 / seq_len)

        # 4. K-mer repetitiveness (0..1) - fraction of positions whose 4-mer
        #    appears 3+ times. Random DNA rarely has repeated 4-mers (>0.05);
        #    periodic / low-complexity DNA is covered almost entirely.
        kmer_counts: Counter = Counter()
        kmer_list: List[str] = []
        for i in range(len(seq) - 3):
            four = seq[i : i + 4]
            if all(c in "ACGT" for c in four):
                kmer_counts[four] += 1
                kmer_list.append(four)
        total_kmers = len(kmer_list)
        if total_kmers > 0:
            covered = sum(1 for k in kmer_list if kmer_counts[k] >= 3)
            repetitiveness = max(0.0, min(1.0, covered / total_kmers))
        else:
            repetitiveness = 1.0

        # Peak-and-context model: the single strongest anomaly signals risk,
        # with GC skew and repetitiveness adding situational context.
        peak = max(homopoly_frac, tandem_frac, 0.5 * repetitiveness)
        context = min(0.35, 0.25 * (gc_dev + repetitiveness))
        score = min(100.0, 100.0 * min(1.0, 0.8 * peak + context))

        return {
            "risk_score": round(score, 2),
            "gc_content": round(gc, 2),
            "gc_deviation": round(gc_dev, 3),
            "homopolymer_runs": homopoly_runs,
            "homopolymer_fraction": round(homopoly_frac, 3),
            "tandem_repeat_units": self._tandem_repeat_units(seq),
            "repetitiveness": round(repetitiveness, 3),
        }

    # ============= Training =============

    def _generate_synthetic_sequences(self, target_count: int = 150) -> List[Tuple[str, str]]:
        """Generate biologically-plausible training sequences.

        Benign: balanced GC, no homopolymers / repeats (true random DNA).
        High-risk: skewed GC, homopolymer runs and tandem repeats present.
        """
        random.seed(self.random_state)
        samples: List[Tuple[str, str]] = []
        rng = random.Random(self.random_state)

        def make_random(gc_target: float, length: int) -> str:
            bases = "G" if gc_target >= 50 else "A"
            gc_w = gc_target / 100.0
            return "".join(
                rng.choice("GC") if rng.random() < gc_w else rng.choice("AT")
                for _ in range(length)
            )

        for _ in range(target_count):
            length = rng.randint(80, 200)
            gc_target = rng.uniform(42, 58)
            samples.append((make_random(gc_target, length), "Benign Strain"))

            length = rng.randint(80, 200)
            gc_skew = rng.choice([rng.uniform(15, 28), rng.uniform(72, 85)])
            seq = list(make_random(gc_skew, length))
            # inject homopolymer runs
            for _ in range(rng.randint(1, 3)):
                b = rng.choice("ACGT")
                pos = rng.randint(0, len(seq) - 1)
                run = rng.randint(4, 8)
                for j in range(pos, min(pos + run, len(seq))):
                    seq[j] = b
            # inject tandem repeat block
            unit = rng.choice(["CAG", "GAC", "TGG", "AGC", "TTA"])
            pos = rng.randint(0, max(len(seq) - 30, 1))
            for idx, b in enumerate(list(unit * 8)):
                if pos + idx < len(seq):
                    seq[pos + idx] = b
            samples.append(("".join(seq), "High-Risk Variant"))

        return samples

    def train_baseline(self, training_sequences: List[str] = None) -> Dict[str, Any]:
        """Train the RandomForest on labeled sequence data.

        Uses real training data when available (from data/training/ in FASTA
        with labels in the header), otherwise falls back to synthetic data.
        """
        trained = self._load_real_training_data()
        if not trained:
            trained = self._generate_synthetic_sequences(150)
        if training_sequences:
            trained.extend(self._label_raw_sequences(training_sequences))

        X: List[List[float]] = []
        y: List[str] = []
        for seq, label in trained:
            features = self._extract_k_mers(seq, k=3)
            X.append(features)
            y.append(label)
        self.feature_names = [f"kmer_{i}" for i in range(len(X[0]))]
        self.model.fit(X, y)
        self.save_model()
        return {
            "training_samples": len(y),
            "features_used": len(X[0]),
            "classes": self.model.classes_.tolist(),
            "status": "trained",
            "source": "real+baseline" if trained else "synthetic",
        }

    def _label_raw_sequences(self, sequences: List[str]) -> List[Tuple[str, str]]:
        """Guess labels for raw sequences: extreme GC skew or homopolymers = high risk."""
        labeled: List[Tuple[str, str]] = []
        for seq in sequences:
            gc = (seq.count("G") + seq.count("C")) / max(len(seq), 1) * 100
            runs, run_len = self._homopolymer_metrics(seq)
            if (gc < 25 or gc > 75) or runs >= 2 or run_len / max(len(seq), 1) > 0.1:
                labeled.append((seq, "High-Risk Variant"))
            else:
                labeled.append((seq, "Benign Strain"))
        return labeled

    def _load_real_training_data(self) -> List[Tuple[str, str]]:
        """Load labeled training sequences from data/training/*.fasta.

        Labels are parsed from each record's header.  Expected header format:
          ><gene>_<label>_<accession>_<description>
        where <label> is one of: benign, moderate, high.
        """
        from Bio import SeqIO
        from io import StringIO

        training_dir = os.path.join(MODEL_DIR, "training")
        if not os.path.isdir(training_dir):
            return []

        labeled: List[Tuple[str, str]] = []
        label_map = {
            "benign": "Benign Strain",
            "moderate": "Moderate Risk",
            "high": "High-Risk Variant",
            "high_risk": "High-Risk Variant",
        }
        for filename in os.listdir(training_dir):
            if not filename.endswith((".fasta", ".fa", ".fna")):
                continue
            filepath = os.path.join(training_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as fh:
                    text = fh.read()
                for record in SeqIO.parse(StringIO(text), "fasta"):
                    seq = str(record.seq).upper()
                    if len(seq) < 20:
                        continue
                    header = record.description.lower()
                    label = None
                    for key, mapped in label_map.items():
                        if f"_{key}_" in f"_{header}_" or header.startswith(key):
                            label = mapped
                            break
                    if label is None:
                        if "high" in header or "risk" in header or "pathogen" in header:
                            label = "High-Risk Variant"
                        elif "moderate" in header:
                            label = "Moderate Risk"
                        else:
                            label = "Benign Strain"
                    labeled.append((seq, label))
            except Exception:
                continue
        return labeled

    def save_model(self) -> bool:
        """Persist the trained model to disk with joblib."""
        try:
            import joblib
            os.makedirs(MODEL_DIR, exist_ok=True)
            joblib.dump(self, MODEL_PATH, compress=3)
            return True
        except Exception:
            return False

    @staticmethod
    def load_persisted() -> Optional["PathogenAIEngine"]:
        """Load a persisted model from disk."""
        return _load_model()

    # ============= Prediction =============

    def predict_sequence(self, sequence_str: str) -> Dict[str, Any]:
        """Classify a sequence using hybrid heuristic + RandomForest scoring."""
        seq = sequence_str.upper()

        heuristic = self.compute_risk_score(seq)

        rf_high_prob = 0.5
        rf_score = 50.0
        if self.model is not None:
            try:
                features = self._extract_k_mers(seq, k=3)
                features_array = np.array([features])
                proba = self.model.predict_proba(features_array)[0]
                classes = list(self.model.classes_)
                if "High-Risk Variant" in classes:
                    rf_high_prob = float(proba[classes.index("High-Risk Variant")])
                rf_score = rf_high_prob * 100.0
            except Exception:
                rf_score = 50.0

        # Blend: 80% transparent heuristic + 20% ensemble
        final_score = 0.8 * heuristic["risk_score"] + 0.2 * rf_score

        # Gaussian softmax over class centers -> probabilities summing to 100
        bandwidth = 25.0
        weights = {
            cls: math.exp(-(((final_score - center) / bandwidth) ** 2))
            for cls, center in self._CLASS_CENTERS.items()
        }
        total_w = sum(weights.values())
        probabilities = {
            cls: round(w / total_w * 100.0, 2) for cls, w in weights.items()
        }

        predicted_class = max(probabilities, key=lambda k: probabilities[k])
        confidence = probabilities[predicted_class]

        return {
            "sequence": sequence_str,
            "predicted_class": predicted_class,
            "confidence_percent": round(confidence, 2),
            "all_probabilities": probabilities,
            "final_score": round(final_score, 2),
            "rf_score": round(rf_score, 2),
            "heuristic": heuristic,
            "feature_vector_length": 64,
        }


def analyze_sequence_with_ai(sequence_str: str, engine: PathogenAIEngine = None) -> Dict[str, Any]:
    """Convenience function to predict sequence classification."""
    if engine is None:
        engine = PathogenAIEngine()
    return engine.predict_sequence(sequence_str)