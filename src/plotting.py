import matplotlib.pyplot as plt
import polars as pl

PROMINENT_FAMILIES = {
    "Eos": 221,
    "Eunomia": 15,
    "Flora": 8,
    "Hungaria": 434,
    "Hygiea": 10,
    "Koronis": 158,
    "Hertha (aka 44 Nysa)": 135,
    "Themis": 24,
    "Vesta": 4,
}


def plot_prominent(df: pl.DataFrame, x_ax="semimajor_axis", y_ax="sin_inclination"):
    non_prom = df.filter(~pl.col("family_1").is_in(PROMINENT_FAMILIES.values()))
    prom = df.filter(pl.col("family_1").is_in(PROMINENT_FAMILIES.values()))

    _, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(
        non_prom[x_ax],
        non_prom[y_ax],
        s=0.1,
        color="lightgrey",
        alpha=0.5,
    )
    for fam, num in PROMINENT_FAMILIES.items():
        ax.scatter(
            prom.filter(pl.col("family_1") == num)[x_ax],
            prom.filter(pl.col("family_1") == num)[y_ax],
            label=f"{num} {fam}",
            s=0.1,
        )
    ax.legend(loc="upper right", markerscale=15)
    plt.xlabel(x_ax)
    plt.ylabel(y_ax)
    plt.show()


def plot_all_families(df: pl.DataFrame, x_ax="semimajor_axis", y_ax="sin_inclination"):
    background = df.filter(pl.col("family_1") == 0)

    _, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(
        background[x_ax],
        background[y_ax],
        s=0.1,
        color="lightgrey",
        alpha=0.5,
    )
    for fam in df["family_1"].unique():
        if fam == 0:
            continue
        fam_data = df.filter(pl.col("family_1") == fam)
        ax.scatter(
            fam_data[x_ax],
            fam_data[y_ax],
            s=0.1,
            label=f"Family {fam}",
        )
    plt.xlabel(x_ax)
    plt.ylabel(y_ax)
    plt.show()


def plot_clusters(df: pl.DataFrame, threshold=10, title="Clustering"):
    _, ax = plt.subplots(figsize=(7, 6))

    # Count members in each cluster
    clust_counts = df["hierarchical_cluster"].value_counts()
    cluster_sizes = dict(
        zip(clust_counts["hierarchical_cluster"], clust_counts["count"])
    )

    # Separate small and large clusters
    small_clusters = df.filter(
        pl.col("hierarchical_cluster").replace_strict(cluster_sizes) < threshold
    )
    large_clusters = df.filter(
        pl.col("hierarchical_cluster").replace_strict(cluster_sizes) >= threshold
    )

    # Plot small clusters in grey first
    ax.scatter(
        small_clusters["semimajor_axis"],
        small_clusters["sin_inclination"],
        s=0.1,
        color="lightgrey",
        alpha=0.5,
    )

    # Plot large clusters with colormap on top
    ax.scatter(
        large_clusters["semimajor_axis"],
        large_clusters["sin_inclination"],
        s=0.1,
        c=large_clusters["hierarchical_cluster"],
        cmap="tab10",
        alpha=0.5,
    )
    ax.set_xlabel("semimajor_axis")
    ax.set_ylabel("sin_inclination")
    ax.set_title(title)
    plt.show()
