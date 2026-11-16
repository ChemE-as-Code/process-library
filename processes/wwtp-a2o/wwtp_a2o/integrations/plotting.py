"""Lazy matplotlib wrapper; explicit values and units in, plot file out."""


def save_plot(run, trajectory, metric_units):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    times = [row["day"] for row in trajectory]
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), constrained_layout=True)
    for ax, key in zip(axes.flat, ["COD", "NH4", "TN", "TP"], strict=True):
        ax.plot(times, [r[key] for r in trajectory], color="#007f82", lw=1.8)
        ax.set(xlabel="Simulated days", ylabel=f"{key} ({metric_units[key]})")
        ax.grid(alpha=0.2)
    fig.suptitle("Generic A2/O example | QSDsan ASM2d | uncalibrated")
    fig.savefig(run / "trajectory.png", dpi=150)
    plt.close(fig)
