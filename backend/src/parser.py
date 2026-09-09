"""Biopython FASTA sequence parser for PathoVariant-AI."""

from typing import Dict, List, Any, Union
from io import StringIO
from Bio import SeqIO


def parse_fasta_file(content: Union[str, bytes]) -> Dict[str, Any]:
    records: List[Dict[str, Any]] = []
    total_length: int = 0
    total_gc_count: int = 0
    total_bases: int = 0

    try:
        if isinstance(content, bytes):
            text = content.decode("utf-8-sig")
        else:
            text = content

        handle = StringIO(text)
        for record in SeqIO.parse(handle, "fasta"):
            seq_str: str = str(record.seq).upper()
            seq_len: int = len(seq_str)
            gc_count: int = seq_str.count("G") + seq_str.count("C")
            gc_percent: float = (gc_count / seq_len * 100) if seq_len > 0 else 0.0

            protein_seq: str = ""
            try:
                trim_len = seq_len - (seq_len % 3)
                protein_seq = str(record.seq[:trim_len].translate(to_stop=False))
            except Exception:
                protein_seq = ""

            base_counts: Dict[str, int] = {
                "A": seq_str.count("A"),
                "T": seq_str.count("T"),
                "G": seq_str.count("G"),
                "C": seq_str.count("C"),
                "U": seq_str.count("U"),
                "N": seq_str.count("N"),
            }
            base_composition: Dict[str, float] = {}
            for base in ["A", "T", "G", "C", "U", "N"]:
                base_composition[base] = (
                    round(base_counts[base] / seq_len * 100, 2) if seq_len > 0 else 0.0
                )

            record_data: Dict[str, Any] = {
                "id": record.id,
                "description": record.description,
                "sequence": seq_str,
                "length": seq_len,
                "gc_content": gc_percent,
                "protein_translation": protein_seq,
                "sequence_type": "nucleotide",
                "base_counts": base_counts,
                "base_composition": base_composition,
            }
            records.append(record_data)

            total_length += seq_len
            total_bases += seq_len
            total_gc_count += gc_count
        handle.close()

    except Exception as e:
        return {"error": str(e), "records": [], "total_length": 0, "gc_content": 0.0}

    overall_gc: float = (total_gc_count / total_bases * 100) if total_bases > 0 else 0.0

    return {
        "records": records,
        "total_length": total_length,
        "gc_content": overall_gc,
        "total_sequences": len(records),
    }


def parse_sequence(raw_seq: str) -> Dict[str, Any]:
    """Parse a single raw sequence string (no FASTA header required).

    Returns the parsed record compatible with the parse_fasta_file format.
    """
    clean = "".join(ch for ch in raw_seq.upper() if ch in "ACGTUN" or ch in " \t\n")
    clean = "".join(clean.split())
    if not clean:
        return {"error": "Sequence appears to be empty"}

    return parse_fasta_file(f">sequence_1\n{clean}")