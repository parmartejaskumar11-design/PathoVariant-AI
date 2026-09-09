"""Unit tests for the FASTA parser."""

import pytest

from src.parser import parse_fasta_file, parse_sequence


def test_parse_basic_fasta():
    content = ">seq1 description\nATGCATGC\n>seq2\nGGCCGGCC\n"
    result = parse_fasta_file(content)
    assert "error" not in result
    assert result["total_sequences"] == 2
    assert result["total_length"] == 16
    assert len(result["records"]) == 2
    assert result["records"][0]["id"] == "seq1"
    assert result["records"][0]["description"] == "seq1 description"
    assert result["records"][0]["sequence"] == "ATGCATGC"


def test_parse_gc_content():
    content = ">gc\nGCGCGCGCGC\n"
    result = parse_fasta_file(content)
    assert result["records"][0]["gc_content"] == 100.0


def test_parse_base_counts():
    content = ">bases\nAAATTTGGCC\n"
    result = parse_fasta_file(content)
    b = result["records"][0]["base_counts"]
    assert b["A"] == 3 and b["T"] == 3 and b["G"] == 2 and b["C"] == 2


def test_parse_empty_raises_no_error():
    result = parse_fasta_file("")
    assert result["total_sequences"] == 0
    assert len(result["records"]) == 0


def test_parse_sequence_raw():
    result = parse_sequence("ATCGATCGATCG")
    assert "error" not in result
    assert result["total_sequences"] == 1


def test_parse_sequence_empty():
    result = parse_sequence("   ")
    assert "error" in result


def test_parse_bytes_input():
    content = b">s\nACGTACGT\n"
    result = parse_fasta_file(content)
    assert result["total_sequences"] == 1