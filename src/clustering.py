from typing import Literal, Optional

import polars as pl
from sklearn.cluster import AgglomerativeClustering

import utils


def hierarchical_cluster_zone(
    distance_threshold: float,
    zone: int,
    inclination: Literal["all", "low", "high"],
    sample_size: Optional[int] = None,
    sample_seed: Optional[int] = 3,
) -> pl.DataFrame:
    """
    Perform hierarchical clustering on a specific zone and inclination range asteroids.
    Utilize built-in caching of AgglomerativeClustering to speed up repeated runs.

    Args:
        distance_threshold (float): The distance threshold for clustering.
        zone (int): The zone to filter asteroids by.
        inclination (Literal["all", "low", "high"]): The inclination range to filter asteroids by.
        sample_size (Optional[int]): The number of samples to randomly select for a quicker subset of clustering.
        sample_seed (Optional[int]): The random seed for sampling, used if sample_size is provided.

    Returns:
        pl.DataFrame: A DataFrame containing zone data with an additional column for hierarchical cluster labels.
    """
    full = utils.load_full()
    zone_df = utils.filter_by_zone(full, zone=zone, inclination=inclination)

    if sample_size is not None:
        zone_df = zone_df.sample(n=sample_size, seed=sample_seed)

    X = zone_df[["semimajor_axis", "sin_inclination", "eccentricity"]].to_numpy()

    hc = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        linkage="single",
        memory=f"cache/z{str(zone)}_{inclination}",
    )
    labels = hc.fit_predict(X)

    return zone_df.with_columns(pl.Series("hierarchical_cluster", labels))
