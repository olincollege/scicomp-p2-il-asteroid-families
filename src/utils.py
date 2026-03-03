from pathlib import Path

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
