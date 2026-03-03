"""
Script to convert raw data files to CSV with renamed columns
"""

import re
import sys
from pathlib import Path

import polars as pl

# Add root dir to path to import util.py
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.utils import FAMILIES_SCHEMA, MEMBERSHIP_SCHEMA, PROPER_ELEMENTS_SCHEMA

FAMILIES = {
    "in_path": "data/raw/asteroid_families_RAW.txt",
    "out_path": "data/asteroid_families.csv",
    "schema": FAMILIES_SCHEMA,
}

MEMBERSHIP = {
    "in_path": "data/raw/individual_family_membership_RAW.txt",
    "out_path": "data/individual_family_membership.csv",
    "schema": MEMBERSHIP_SCHEMA,
}

PROPER_ELEMENTS = {
    "in_path": "data/raw/proper_elements_numbered_and_multiopposition_RAW.txt",
    "out_path": "data/proper_elements_numbered_and_multiopposition.csv",
    "schema": PROPER_ELEMENTS_SCHEMA,
}


def load_raw_and_save_csv(in_path: str, out_path: str, schema: dict) -> None:
    """
    Load raw data file, excluding comment lines, and save as CSV with renamed columns.

    Args:
        in_path (str): Path to the raw data file.
        out_path (str): Path to save the processed CSV file.
        schema (dict): Dictionary mapping column names to Polars data types.
    """
    with open(in_path, "r", encoding="utf-8") as f:
        # Exclude comment lines, including header
        lines = [ln.strip() for ln in f if not ln.startswith("%")]

    rows = [re.split(r"\s+", ln) for ln in lines]

    df = pl.DataFrame(rows, schema=schema, orient="row")

    df.write_csv(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    for file in [FAMILIES, MEMBERSHIP, PROPER_ELEMENTS]:
        load_raw_and_save_csv(**file)
