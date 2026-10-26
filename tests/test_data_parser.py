import pytest
from pathlib import Path
from typing import List, Dict, Any

from hgnc_app.models import data_parser


# ------------------------------------------------------------------
# parse_line tests
# ------------------------------------------------------------------

def test_parse_line_valid() -> None:
    """Test parsing a valid dictionary row from DictReader."""
    row = {
        "hgnc_id": "HGNC:5",
        "symbol": "A1BG",
        "name": "alpha-1-B glycoprotein",
        "prev_symbol": "",
        "prev_name": "",
        "alias_symbol": "",
        "mane_select": "ENST00000263100.8"
    }
    result = data_parser.parse_line(row)

    assert result is not None
    assert result["gene_symbol"] == "A1BG"
    assert result["hgnc_id"] == "HGNC:5"
    assert result["mane_select"] == "ENST00000263100.8"


def test_parse_line_empty() -> None:
    """An empty dictionary (representing an empty row) should return None."""
    assert data_parser.parse_line({}) is None


def test_parse_line_invalid_format() -> None:
    """Row missing both HGNC ID and symbol should safely return None."""
    bad_row = {"unrelated_column": "GENE1", "some_value": "1111"}
    assert data_parser.parse_line(bad_row) is None


# ------------------------------------------------------------------
# read_file tests
# ------------------------------------------------------------------
def test_read_file_happy(tmp_path: Path) -> None:
    """Test reading valid TSV file with headers and multiple entries."""
    file = tmp_path / "test.txt"
    # HGNC distributes the complete set as tab-separated values, so the
    # fixture mirrors that format with the same column names.
    file.write_text(
        "hgnc_id\tsymbol\tname\tprev_symbol\tprev_name\talias_symbol\tmane_select\n"
        "HGNC:1\tGENE1\tName 1\t\t\t\t\n"
        "HGNC:2\tGENE2\tName 2\t\t\t\t\n"
    )
    result = data_parser.read_file(file)
    assert len(result) == 2
    assert result[0]["gene_symbol"] == "GENE1"
    assert result[1]["gene_symbol"] == "GENE2"


def test_read_file_skips_invalid_lines(tmp_path: Path) -> None:
    """Malformed lines should be skipped, not crash."""
    file = tmp_path / "test.txt"
    file.write_text(
        "hgnc_id\tsymbol\tname\tprev_symbol\tprev_name\talias_symbol\tmane_select\n"
        "HGNC:1\tGENE1\tName 1\t\t\t\t\n"
        "BADLINE\n"
        "HGNC:2\tGENE2\tName 2\t\t\t\t\n"
    )

    result = data_parser.read_file(file)

    assert len(result) == 2


def test_read_file_all_invalid(tmp_path: Path) -> None:
    """All invalid lines should raise ValueError."""
    file = tmp_path / "test.txt"
    file.write_text("BADLINE\nBADLINE2\n")

    with pytest.raises(ValueError):
        data_parser.read_file(file)


def test_read_file_missing_file(tmp_path: Path) -> None:
    """Non-existent file should raise an error."""
    file = tmp_path / "does_not_exist.txt"

    with pytest.raises(Exception):
        data_parser.read_file(file)


# ------------------------------------------------------------------
# find_gene tests
# ------------------------------------------------------------------

def test_find_gene_found_by_symbol() -> None:
    """Should return matching gene entry using the gene symbol."""
    data: List[Dict[str, str]] = [
        {"gene_symbol": "BRCA1", "hgnc_id": "HGNC:1100"},
        {"gene_symbol": "BRCA2", "hgnc_id": "HGNC:1101"},
    ]

    result = data_parser.find_gene("BRCA2", data)

    assert result is not None
    assert result["hgnc_id"] == "HGNC:1101"


def test_find_gene_found_by_id() -> None:
    """Should return matching gene entry using the HGNC ID."""
    data: List[Dict[str, str]] = [
        {"gene_symbol": "BRCA1", "hgnc_id": "HGNC:1100"},
        {"gene_symbol": "BRCA2", "hgnc_id": "HGNC:1101"},
    ]

    result = data_parser.find_gene("HGNC:1101", data)

    assert result is not None
    assert result["gene_symbol"] == "BRCA2"


def test_find_gene_not_found() -> None:
    """Should return None if gene not found."""
    data: List[Dict[str, str]] = [
        {"gene_symbol": "BRCA1", "hgnc_id": "HGNC:1100"},
    ]

    result = data_parser.find_gene("TP53", data)

    assert result is None


def test_find_gene_empty_data() -> None:
    """Searching empty dataset returns None."""
    result = data_parser.find_gene("A", [])

    assert result is None


def test_find_gene_case_insensitive() -> None:
    """Search is case-insensitive."""
    data = [{"gene_symbol": "GENE1", "hgnc_id": "HGNC:1100"}]

    assert data_parser.find_gene("gene1", data) is not None
    assert data_parser.find_gene("hgnc:1100", data) is not None