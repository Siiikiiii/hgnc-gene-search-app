
import csv
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


def read_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Read the HGNC TSV dataset and extract specific fields into a structured list of dictionaries.

    Parameters
    ----------
    filepath : str
        Path to the input TSV file.

    Returns
    -------
    list of dict
        Parsed records, one per line in the file.

    Raises
    ------
    IOError
        If the file cannot be opened or read.
    ValueError
        If parsing fails for all lines.
    """
    logger.info(f"Reading data file: {filepath}")

    output_list = []

    try:
        with open(filepath, mode='r', encoding='utf-8') as f:
            # The HGNC complete set has ~50 columns and HGNC has added and
            # reordered columns between releases. Reading by header name
            # (DictReader) rather than by column position means only the
            # columns this app uses need to stay the same.
            reader = csv.DictReader(f, delimiter='\t')
            for i, entry in enumerate(reader):
                # One bad row should not stop ~45,000 genes from loading,
                # so errors are logged and the row skipped. Rows that are
                # merely incomplete are filtered out by parse_line
                # returning None and are not logged.
                try:
                    parsed = parse_line(entry)
                    if parsed:
                        output_list.append(parsed)
                except Exception:
                    # +2 converts the 0-based row index to a file line
                    # number: +1 for 1-based numbering, +1 for the header.
                    logger.warning(f"Skipping malformed line {i+2}")

        # A file that yields no genes is almost certainly the wrong file or
        # format (e.g. comma- rather than tab-separated), so stop here
        # rather than start an app that can never find anything.
        if not output_list:
            raise ValueError("No valid data parsed from file")

        logger.info(f"Successfully loaded {len(output_list)} records")
        return output_list

    except Exception:
        logger.exception("Error reading input file")
        raise


def parse_line(row: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Parse a single row dictionary from the HGNC dataset.
    Returns None if critical data (like symbol or hgnc_id) is missing.

    Parameters
    ----------
    row : dict
        A dictionary representing a row from the input file, typically from csv.DictReader.

    Returns
    -------
    dict or None
        Parsed data as a dictionary, or None if the line is empty or invalid.

    Raises
    ------
    ValueError
        If the line structure is invalid.
    """
    # The approved symbol and HGNC ID are the only fields find_gene
    # searches, so a row without them could never be returned to a user.
    if not row.get("hgnc_id") or not row.get("symbol"):
        return None

    # Keep only the columns shown on the results page, renamed to the keys
    # used by templates/index.html. Multi-value fields (previous symbols,
    # previous names, aliases) are kept exactly as HGNC provides them,
    # separated by "|", and displayed as-is.
    return {
        "hgnc_id": row.get("hgnc_id", ""),
        "gene_symbol": row.get("symbol", ""),
        "gene_name": row.get("name", ""),
        "prev_symbol": row.get("prev_symbol", ""),
        "prev_name": row.get("prev_name", ""),
        "alias_symbol": row.get("alias_symbol", ""),
        "mane_select": row.get("mane_select", "")
    }


def find_gene(query: str, data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Find a gene query (HGNC-approved gene symbol or an HGNC ID) within a parsed hgnc dataset.

    Parameters
    ----------
    query : str
        The search term (e.g., "BRCA2" or "HGNC:1101").
    data : list of dict
        Parsed dataset returned from `read_file`.

    Returns
    -------
    dict or None
        Matching gene record if found, otherwise None.

    Notes
    -----
    Search is case-insensitive and matches exact gene symbols or HGNC IDs.
    """
    # HGNC symbols are mostly upper case but some contain lower case
    # (e.g. C1orf21), and users often type IDs as "hgnc:1100", so both
    # sides are upper-cased before comparing.
    clean_query = query.strip().upper()
    logger.debug(f"Searching for gene: {clean_query}")

    # Design notes:
    # - A linear scan of ~45,000 records takes about 10 ms, which is fine
    #   for one search per request. If the dataset or traffic grew, a dict
    #   keyed by symbol and ID could be built once in read_file instead.
    # - Approved symbols and HGNC IDs are unique in the HGNC dataset and
    #   never equal each other, so the first match is the only match.
    # - Previous symbols and aliases are deliberately not searched: several
    #   hundred of them are identical to another gene's approved symbol,
    #   so matching on them could return the wrong gene.
    for entry in data:
        symbol = str(entry.get("gene_symbol", "")).strip().upper()
        hgnc_id = str(entry.get("hgnc_id", "")).strip().upper()
        if symbol == clean_query or hgnc_id == clean_query:
            logger.info(f"Match found for gene: {clean_query}")
            return entry

    logger.info(f"No match found for gene: {clean_query}")
    return None