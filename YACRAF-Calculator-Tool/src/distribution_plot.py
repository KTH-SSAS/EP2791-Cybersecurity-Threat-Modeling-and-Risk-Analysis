import numpy as np


def plot_distribution(distribution_value, title, percentiles):
    """Plot the empirical density and CDF of a sampled YACRAF value."""
    import matplotlib.pyplot as plt

    samples = np.asarray(distribution_value.get_samples(), dtype=float)
    samples = samples[np.isfinite(samples)]
    if len(samples) == 0:
        raise ValueError("The distribution does not contain any finite samples")

    percentiles = tuple(percentiles)
    quantiles = np.quantile(samples, percentiles)
    labels = [f"P{round(percentile * 100)}" for percentile in percentiles]
    colors = ("tab:orange", "tab:red", "tab:purple")

    figure, (density_axis, cdf_axis) = plt.subplots(1, 2, figsize=(10, 4))
    density_axis.hist(samples, bins="auto", density=True, color="tab:blue", alpha=0.7)
    density_axis.set_title("Empirical density")
    density_axis.set_xlabel("Value")
    density_axis.set_ylabel("Density")

    sorted_samples = np.sort(samples)
    cumulative_probability = np.arange(1, len(sorted_samples) + 1) / len(sorted_samples)
    cdf_axis.step(sorted_samples, cumulative_probability, where="post", color="tab:blue")
    cdf_axis.set_title("Empirical cumulative distribution")
    cdf_axis.set_xlabel("Value")
    cdf_axis.set_ylabel("Probability")
    cdf_axis.set_ylim(0, 1)

    for label, quantile, color in zip(labels, quantiles, colors):
        line_label = f"{label}={quantile:.3g}"
        density_axis.axvline(quantile, color=color, linestyle="--", label=line_label)
        cdf_axis.axvline(quantile, color=color, linestyle="--", label=line_label)

    density_axis.legend()
    cdf_axis.legend()
    figure.suptitle(f"{title} ({len(samples):,} samples)")
    figure.tight_layout()
    plt.show(block=False)
    return figure
