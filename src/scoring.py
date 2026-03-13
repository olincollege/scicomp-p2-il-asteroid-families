import polars as pl


def clustering_summary(
    clustered_df: pl.DataFrame, cluster_col: str, threshold: int = 10
) -> pl.DataFrame:
    """
    Calculate the following metrics for each cluster, given a "main family," the family
    that is the most prevalent in the cluster:
    - family_completeness: the percentage of the main family that is in the cluster
    - cluster_purity: the percentage of the cluster that is from the main family
    - cluster_score: the product of family_completeness and cluster_purity, a combined
        metric to evaluate the quality of the cluster

    Args:
        clustered_df (pl.DataFrame): A DataFrame containing asteroid data with a column
            for cluster labels and a column for true family labels.
        cluster_col (str): The name of the column in clustered_df that contains the
            cluster labels.
        threshold (int): The minimum number of members in a cluster to be included in
            the summary. Defaults to 10.

    Returns:
        pl.DataFrame: A DataFrame summarizing the metrics for each cluster that meets
            the size threshold. Contains columns: main_family, cluster_id, cluster_size,
            family_completeness, cluster_purity, cluster_score.
    """
    return (
        clustered_df
        # Count cluster size, total family size, and family count within cluster
        .with_columns(
            cluster_size=pl.len().over(cluster_col),
            family_total=pl.len().over("family_1"),
            family_in_cluster=pl.len().over([cluster_col, "family_1"]),
        )
        # Filter clusters by size threshold and exclude background asteroids (family_1 == 0
        .filter((pl.col("cluster_size") >= threshold) & (pl.col("family_1") != 0))
        # Sort to ensure the most frequent family is on top for each cluster
        .sort([cluster_col, "family_in_cluster"], descending=[False, True])
        # Collapse to one row per cluster, the row with the most frequent family in that cluster
        .group_by(cluster_col)
        .agg(
            main_family=pl.first("family_1"),
            cluster_size=pl.first("cluster_size"),
            main_family_count=pl.first("family_in_cluster"),
            family_total=pl.first("family_total"),
        )
        # Calculate metrics for each cluster's main family
        .with_columns(
            family_completeness=(
                100 * pl.col("main_family_count") / pl.col("family_total")
            ),
            cluster_purity=(100 * pl.col("main_family_count") / pl.col("cluster_size")),
        )
        .with_columns(
            cluster_score=(pl.col("family_completeness") * pl.col("cluster_purity"))
        )
        .select(
            pl.col("main_family"),
            pl.col(cluster_col).alias("cluster_id"),
            "cluster_size",
            "family_completeness",
            "cluster_purity",
            "cluster_score",
        )
        .sort("cluster_id")
    )


def complete_and_pure_count(
    clust_summary: pl.DataFrame, threshold: float = 95.0
) -> int:
    """
    Count the number of clusters in the clustering summary that have a family
    completeness and cluster purity above a specified threshold.

    Args:
        clust_summary (pl.DataFrame): Expects return from `clustering_summary()`
        threshold (float): The minimum completeness and purity threshold. Defaults to 95.0.

    Returns:
        int: The number of clusters with completeness and purity above the threshold.
    """
    return clust_summary.filter(
        (pl.col("family_completeness") >= threshold)
        & (pl.col("cluster_purity") >= threshold)
    ).shape[0]


def completeness_count(clust_summary: pl.DataFrame, threshold: float = 95.0) -> int:
    """
    Count the number of clusters in the clustering summary that have a family
    completeness above a specified threshold.

    Args:
        clust_summary (pl.DataFrame): Expects return from `clustering_summary()`
        threshold (float): The minimum completeness threshold. Defaults to 95.0.

    Returns:
        int: The number of clusters with completeness above the threshold.
    """
    return clust_summary.filter(pl.col("family_completeness") >= threshold).shape[0]
