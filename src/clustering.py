"""
Hierarchical clustering functions for asteroid data, containing top level functions for
testing and visualizing clustering results.
"""

from typing import Literal, Optional

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from sklearn.cluster import AgglomerativeClustering

import plotting
import scoring
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
        inclination (Literal["all", "low", "high"]): The inclination range to filter
            asteroids by.
        sample_size (Optional[int]): The number of samples to randomly select for a
            quicker subset of clustering.
        sample_seed (Optional[int]): The random seed for sampling, used if sample_size
            is provided.

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


def param_sweep(
    zone: int,
    inc: Literal["all", "low", "high"],
    min_dist: float,
    max_dist: float,
    step: float,
) -> pl.DataFrame:
    """
    Perform a parameter sweep over distance thresholds for hierarchical clustering.
    Generates plot visualizing parameter sweep results.

    Args:
        zone (int): The zone to filter asteroids by.
        inc (Literal["all", "low", "high"]): The inclination range to filter asteroids by.
        min_dist (float): The minimum distance threshold to test.
        max_dist (float): The maximum distance threshold to test.
        step (float): The step size for distance thresholds to test.

    Returns:
        pl.DataFrame: A DataFrame summarizing the results of the parameter sweep
    """
    out = []

    for dist in np.arange(min_dist, max_dist, step):
        clusters = hierarchical_cluster_zone(dist, zone=zone, inclination=inc)
        summary = scoring.clustering_summary(
            clusters, cluster_col="hierarchical_cluster"
        )
        res = {
            "distance": dist,
            "complete_and_pure": scoring.complete_and_pure_count(summary),
            "complete": scoring.completeness_count(summary),
            "avg_purity_complete": summary.filter(pl.col("family_completeness") >= 95)[
                "cluster_purity"
            ].mean(),
            "clust_count": len(summary),
        }
        out.append(res)

    sweep_df = pl.DataFrame(out)
    plotting.plot_parameter_sweep(
        sweep_df, f"Zone {zone} {inc.capitalize()} Parameter Sweep"
    )
    return sweep_df


def clustering_comparison(
    zone: int, inc: Literal["all", "low", "high"], distance_threshold: float
) -> pl.DataFrame:
    """
    Perform clustering on a zone, then plot the actual families and the hierarchical
    clustering results side by side for comparison.

    Args:
        zone (int): The zone to filter asteroids by.
        inc (Literal["all", "low", "high"]): The inclination range to filter asteroids by.
        distance_threshold (float): The distance threshold to use for hierarchical clustering.

    Returns:
        pl.DataFrame: A DataFrame containing stats about complete clusters from
            hierarchical clustering results.
    """
    full = utils.load_full()
    zone_df = utils.filter_by_zone(full, zone=zone, inclination=inc)
    clusters = hierarchical_cluster_zone(distance_threshold, zone=zone, inclination=inc)

    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)

    plotting.plot_all_families(
        zone_df,
        title=f"Zone {zone} {inc.capitalize()} Actual Families",
        ax=ax1,
    )
    plotting.plot_clusters(
        clusters,
        title=f"Zone {zone} {inc.capitalize()} Hierarchical Clustering (d={distance_threshold:.4f})",
        ax=ax2,
    )

    plt.tight_layout()
    plt.show()

    return (
        scoring.clustering_summary(clusters, cluster_col="hierarchical_cluster")
        .filter(pl.col("family_completeness") >= 95)
        .select("main_family", "cluster_size", "family_completeness", "cluster_purity")
        .sort("cluster_purity", descending=True)
    )


def find_all_complete_clusters() -> pl.DataFrame:
    """
    Perform hierarchical clustering  on all zones, then plot all complete clusters.
    """
    DIST_THRESHOLDS = {
        (1, "all"): 0.0021,
        (2, "low"): 0.0019,
        (2, "high"): 0.0050,
        (3, "low"): 0.0014,
        (3, "high"): 0.0045,
        (4, "low"): 0.0016,
        (4, "high"): 0.0030,
        (5, "all"): 0.0045,
        (6, "all"): 0.0018,
    }
    all_tagged = []
    for (zone, inc), dist in DIST_THRESHOLDS.items():
        clusters = hierarchical_cluster_zone(
            distance_threshold=dist, zone=zone, inclination=inc
        )
        summary = scoring.clustering_summary(
            clusters, cluster_col="hierarchical_cluster"
        )
        complete_ids = summary.filter(pl.col("family_completeness") >= 95).select(
            "cluster_id", "main_family"
        )
        tagged = (
            clusters.join(
                complete_ids,
                left_on="hierarchical_cluster",
                right_on="cluster_id",
                how="left",
            )
            .with_columns(pl.col("main_family").fill_null(0).alias("complete_family"))
            .select(["semimajor_axis", "sin_inclination", "complete_family"])
        )
        all_tagged.append(tagged)

    combined = pl.concat(all_tagged)
    plotting.plot_complete_clusters(combined)
