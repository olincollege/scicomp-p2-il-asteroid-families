from typing import Literal, Optional

import matplotlib.pyplot as plt
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


def clustering_comparison(zone, inc, distance_threshold):
    full = utils.load_full()
    zone_df = utils.filter_by_zone(full, zone=zone, inclination=inc)
    clusters = hierarchical_cluster_zone(distance_threshold, zone=zone, inclination=inc)

    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)

    plotting.plot_all_families(
        zone_df,
        ax=ax1,
        title=f"Zone {zone} {inc.capitalize()} Actual Families",
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


def find_all_complete_clusters():
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
    return combined
