#!/usr/bin/env python3
"""Create a representative held-out force prediction curve for the paper."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_ALIGNED_PARQUET = Path(
    "/home/zn/flap-system-identification/artifacts/"
    "20260602_bc_correction_measured_massprops_v1/evaluation/aligned/"
    "test_phase_structured_aligned.parquet"
)
DEFAULT_PER_LOG = Path(
    "/home/zn/flap-system-identification/artifacts/"
    "20260602_bc_correction_measured_massprops_v1/evaluation/per_log_metrics.csv"
)
OUT_ROOT = Path(__file__).resolve().parents[1] / "figures"
OUT_STEM = OUT_ROOT / "heldout_force_prediction_curve"
TARGETS = [
    ("fx_b", r"$f_{x,B}$ (N)"),
    ("fy_b", r"$f_{y,B}$ (N)"),
    ("fz_b", r"$f_{z,B}$ (N)"),
]
COLORS = {
    "label": "#000000",
    "prior": "#D55E00",
    "corrected": "#0072B2",
}


def _select_representative_log(per_log_path: Path) -> str:
    per_log = pd.read_csv(per_log_path)
    rows = per_log[
        per_log["split"].eq("test")
        & per_log["model"].eq("phase_structured")
        & per_log["group"].eq("force")
    ].copy()
    if rows.empty:
        raise ValueError("No test phase_structured force rows found in per-log metrics.")
    median_rmse = rows["rmse"].median()
    rows["distance_to_median"] = (rows["rmse"] - median_rmse).abs()
    return str(rows.sort_values(["distance_to_median", "log_id"]).iloc[0]["log_id"])


def _window_for_log(df: pd.DataFrame, duration_s: float) -> pd.DataFrame:
    time = df["time_s"].to_numpy(dtype=float)
    if len(time) < 2:
        return df
    t_min = float(np.nanmin(time))
    t_max = float(np.nanmax(time))
    if t_max - t_min <= duration_s:
        return df
    start = t_min + 0.5 * (t_max - t_min - duration_s)
    end = start + duration_s
    return df[df["time_s"].between(start, end)].copy()


def make_figure(aligned_path: Path, per_log_path: Path, log_id: str | None, duration_s: float) -> str:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "legend.fontsize": 7,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "axes.linewidth": 0.7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    selected_log = _select_representative_log(per_log_path) if log_id is None else log_id
    samples = pd.read_parquet(aligned_path)
    log = samples[samples["log_id"].eq(selected_log)].sort_values("time_s").copy()
    if log.empty:
        raise ValueError(f"Selected log not found in aligned samples: {selected_log}")
    window = _window_for_log(log, duration_s=duration_s)
    if len(window) > 3500:
        stride = int(np.ceil(len(window) / 3500))
        window = window.iloc[::stride].copy()

    t = window["time_s"].to_numpy(dtype=float)
    t = t - float(t[0])

    fig, axes = plt.subplots(3, 1, figsize=(7.15, 4.0), sharex=True)
    for ax, (target, ylabel) in zip(axes, TARGETS):
        ax.plot(
            t,
            window[f"label_{target}"],
            color=COLORS["label"],
            linewidth=0.85,
            label="Effective label",
        )
        ax.plot(
            t,
            window[f"prior_{target}"],
            color=COLORS["prior"],
            linewidth=0.9,
            linestyle="--",
            label="Calibrated prior",
        )
        ax.plot(
            t,
            window[f"corrected_{target}"],
            color=COLORS["corrected"],
            linewidth=1.0,
            label="Structured correction",
        )
        ax.set_ylabel(ylabel)
        ax.grid(True, color="#D0D0D0", linewidth=0.45, alpha=0.75)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[-1].set_xlabel("Time in held-out segment (s)")
    axes[0].legend(loc="upper right", frameon=True, framealpha=0.92, edgecolor="#FFFFFF", facecolor="#FFFFFF")
    axes[0].set_title(f"Held-out log segment: {selected_log}")

    fig.tight_layout(pad=0.35, h_pad=0.9)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_STEM.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(OUT_STEM.with_suffix(".png"), dpi=450, bbox_inches="tight")
    plt.close(fig)
    return selected_log


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aligned-parquet", type=Path, default=DEFAULT_ALIGNED_PARQUET)
    parser.add_argument("--per-log-metrics", type=Path, default=DEFAULT_PER_LOG)
    parser.add_argument("--log-id", default=None)
    parser.add_argument("--duration-s", type=float, default=25.0)
    args = parser.parse_args()
    selected_log = make_figure(args.aligned_parquet, args.per_log_metrics, args.log_id, args.duration_s)
    print(f"selected_log={selected_log}")
    for suffix in (".pdf", ".png"):
        print(OUT_STEM.with_suffix(suffix))


if __name__ == "__main__":
    main()
