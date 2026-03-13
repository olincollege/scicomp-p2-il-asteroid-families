"""
Data loading utils to access asteroid data
"""

from pathlib import Path
from typing import Literal

import polars as pl

FAMILIES_SCHEMA = {
    "core_fam": pl.Int64,
    "zone": pl.Int64,
    "dist_max": pl.Float64,
    "num_core": pl.Int64,
    "num_small": pl.Int64,
    "num_add": pl.Int64,
    "num_tot": pl.Int64,
    "semimajor_axis_min": pl.Float64,
    "semimajor_axis_max": pl.Float64,
    "eccentricity_min": pl.Float64,
    "eccentricity_max": pl.Float64,
    "sin_inclination_min": pl.Float64,
    "sin_inclination_max": pl.Float64,
}

MEMBERSHIP_SCHEMA = {
    "name": pl.Utf8,
    "magnitude": pl.Float64,
    "status": pl.Int64,
    "family_1": pl.Int64,
    "dist_fam_1": pl.Float64,
    "near_1": pl.Utf8,
    "family_2": pl.Int64,
    "dist_fam_2": pl.Float64,
    "near_2": pl.Utf8,
    "resonance_code": pl.Utf8,
}

PROPER_ELEMENTS_SCHEMA = {
    "name": pl.Utf8,
    "magnitude": pl.Float64,
    "semimajor_axis": pl.Float64,
    "eccentricity": pl.Float64,
    "sin_inclination": pl.Float64,
    "mean_motion": pl.Float64,
    "precession_perihelion": pl.Float64,
    "precession_ascending_node": pl.Float64,
    "lyap_exp_x1e6": pl.Float64,
    "lyap_timescale": pl.Float64,
}

ROOT_DIR = Path(__file__).parent.parent


def load_families() -> pl.DataFrame:
    """
    Returns:
        pl.DataFrame: DataFrame containing the asteroid families data.
    """
    return pl.read_csv(
        ROOT_DIR / "data" / "asteroid_families.csv", schema=FAMILIES_SCHEMA
    )


def load_membership() -> pl.DataFrame:
    """
    Returns:
        pl.DataFrame: DataFrame containing the individual membership data.
    """
    return pl.read_csv(
        ROOT_DIR / "data" / "individual_family_membership.csv", schema=MEMBERSHIP_SCHEMA
    )


def load_proper_elements() -> pl.DataFrame:
    """
    Returns:
        pl.DataFrame: DataFrame containing the proper elements data.
    """
    return pl.read_csv(
        ROOT_DIR / "data" / "proper_elements_numbered_and_multiopposition.csv",
        schema=PROPER_ELEMENTS_SCHEMA,
    )


def load_full() -> pl.DataFrame:
    """
    Returns:
        pl.DataFrame: DataFrame containing the merged data from membership and proper
            elements, with missing values filled with zeros.
    """
    pes = load_proper_elements()
    membership = load_membership()
    full = pes.join(membership, on="name", how="left")
    full = full.fill_null(strategy="zero")
    return full


def filter_by_zone(
    df: pl.DataFrame, zone: int, inclination: Literal["all", "low", "high"]
) -> pl.DataFrame:
    """
    Filters the DataFrame by the specified zone as defined by "Milani et al. (2014).
    Asteroid families classification: Exploiting very large datasets"

    Args:
        df (pl.DataFrame): The input DataFrame to filter.
        zone (int): The zone to filter by.
        inclination (Literal["all", "low", "high"]): The inclination category to filter
            by. Low will only select asteroids with sinI < 0.3, high will only select
            asteroids with sinI > 0.3.
    Returns:
        pl.DataFrame: A filtered DataFrame containing only rows that match the specified zone.
    """
    ZONE_SEMIMAJOR_AXIS_RANGES = {
        1: (1.600, 2.000),
        2: (2.000, 2.500),
        3: (2.500, 2.825),
        4: (2.825, 3.278),
        5: (3.278, 3.700),
        6: (3.700, 4.000),
    }

    zone_range = ZONE_SEMIMAJOR_AXIS_RANGES[zone]
    out = df.filter(
        (pl.col("semimajor_axis") >= zone_range[0])
        & (pl.col("semimajor_axis") < zone_range[1])
    )

    match inclination:
        case "low":
            out = out.filter(pl.col("sin_inclination") < 0.3)
        case "high":
            out = out.filter(pl.col("sin_inclination") >= 0.3)

    return out
