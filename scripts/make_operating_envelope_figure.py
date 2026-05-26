#!/usr/bin/env python3
"""Create the operating-envelope summary figure for the AeroConf paper."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_ROOT = Path(
    "/home/zn/flap-system-identification/dataset/"
    "canonical_v0.2_training_ready_split_hq_v4_direct_airspeed_logsplit_paper_alt5_v1"
)
OUT_ROOT = Path(__file__).resolve().parents[1] / "figures"
OUT_STEM = OUT_ROOT / "operating_envelope_summary"

SPLITS = ("train", "val", "test")
COLORS = {
    "train": "#0072B2",  # Okabe-Ito blue
    "val": "#E69F00",  # Okabe-Ito orange
    "test": "#009E73",  # Okabe-Ito green
}
LINESTYLES = {"train": "-", "val": "--", "test": ":"}
LABELS = {"train": "Train", "val": "Validation", "test": "Test"}


def _body_rotation_from_quaternion(df: pd.DataFrame) -> np.ndarray:
    """Return body-to-NED rotation matrices from PX4 attitude quaternions."""

    q = df[
        [
            "vehicle_attitude.q[0]",
            "vehicle_attitude.q[1]",
            "vehicle_attitude.q[2]",
            "vehicle_attitude.q[3]",
        ]
    ].to_numpy(dtype=float, copy=True)
    norm = np.linalg.norm(q, axis=1)
    valid = np.isfinite(norm) & (norm > 0.0)
    q[valid] /= norm[valid, None]
    q[~valid] = np.nan

    w, x, y, z = q[:, 0], q[:, 1], q[:, 2], q[:, 3]
    rot = np.full((len(df), 3, 3), np.nan, dtype=float)
    rot[:, 0, 0] = 1.0 - 2.0 * (y * y + z * z)
    rot[:, 0, 1] = 2.0 * (x * y - z * w)
    rot[:, 0, 2] = 2.0 * (x * z + y * w)
    rot[:, 1, 0] = 2.0 * (x * y + z * w)
    rot[:, 1, 1] = 1.0 - 2.0 * (x * x + z * z)
    rot[:, 1, 2] = 2.0 * (y * z - x * w)
    rot[:, 2, 0] = 2.0 * (x * z - y * w)
    rot[:, 2, 1] = 2.0 * (y * z + x * w)
    rot[:, 2, 2] = 1.0 - 2.0 * (x * x + y * y)
    return rot


def _derive_envelope_quantities(df: pd.DataFrame) -> pd.DataFrame:
    """Match the training pipeline definitions used for the paper tables."""

    out = pd.DataFrame(index=df.index)
    out["true_airspeed_m_s"] = df["airspeed_validated.true_airspeed_m_s"].astype(float)
    out["cycle_flap_frequency_hz"] = df["cycle_flap_frequency_hz"].astype(float)
    out["dynamic_pressure_pa"] = (
        0.5
        * df["vehicle_air_data.rho"].astype(float)
        * out["true_airspeed_m_s"]
        * out["true_airspeed_m_s"]
    )

    rot_body_to_ned = _body_rotation_from_quaternion(df)
    velocity_n = df[
        [
            "vehicle_local_position.vx",
            "vehicle_local_position.vy",
            "vehicle_local_position.vz",
        ]
    ].to_numpy(dtype=float, copy=True)
    wind_n = np.zeros_like(velocity_n)
    wind_n[:, 0] = df["wind.windspeed_north"].to_numpy(dtype=float)
    wind_n[:, 1] = df["wind.windspeed_east"].to_numpy(dtype=float)
    relative_air_velocity_n = velocity_n - wind_n
    relative_air_velocity_b = np.einsum("nji,nj->ni", rot_body_to_ned, relative_air_velocity_n)
    relative_air_speed = np.linalg.norm(relative_air_velocity_b, axis=1)
    valid_speed = relative_air_speed > 1e-8

    alpha = np.full(len(df), np.nan, dtype=float)
    beta = np.full(len(df), np.nan, dtype=float)
    alpha[valid_speed] = np.arctan2(
        relative_air_velocity_b[valid_speed, 2],
        relative_air_velocity_b[valid_speed, 0],
    )
    beta[valid_speed] = np.arcsin(
        np.clip(relative_air_velocity_b[valid_speed, 1] / relative_air_speed[valid_speed], -1.0, 1.0)
    )
    out["alpha_deg"] = np.rad2deg(alpha)
    out["beta_deg"] = np.rad2deg(beta)
    return out


def _smooth_histogram_percent(values: np.ndarray, bins: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return lightly smoothed per-bin sample percentages at bin centers."""

    values = values[np.isfinite(values)]
    weights = np.full_like(values, 100.0 / max(len(values), 1), dtype=float)
    fractions, edges = np.histogram(values, bins=bins, weights=weights)
    centers = 0.5 * (edges[:-1] + edges[1:])

    kernel = np.array([1.0, 2.0, 3.0, 2.0, 1.0], dtype=float)
    kernel /= kernel.sum()
    padded = np.pad(fractions, (2, 2), mode="edge")
    smoothed = np.convolve(padded, kernel, mode="valid")
    return centers, smoothed


def main() -> None:
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

    split_frames: dict[str, pd.DataFrame] = {}
    for split in SPLITS:
        samples = pd.read_parquet(DATA_ROOT / f"{split}_samples.parquet")
        split_frames[split] = _derive_envelope_quantities(samples)

    panels = [
        ("true_airspeed_m_s", "True airspeed (m/s)", "a"),
        ("alpha_deg", "Angle of attack (deg)", "b"),
        ("beta_deg", "Sideslip (deg)", "c"),
        ("cycle_flap_frequency_hz", "Cycle flapping frequency (Hz)", "d"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(7.15, 3.85))
    for ax, (column, xlabel, label) in zip(axes.ravel(), panels):
        all_values = pd.concat([split_frames[split][column] for split in SPLITS], ignore_index=True)
        lo, hi = np.nanpercentile(all_values.to_numpy(dtype=float), [0.5, 99.5])
        pad = 0.04 * max(hi - lo, 1e-9)
        bins = np.linspace(lo, hi, 38)

        for split in SPLITS:
            values = split_frames[split][column].to_numpy(dtype=float)
            x, y = _smooth_histogram_percent(values, bins)
            ax.plot(
                x,
                y,
                color=COLORS[split],
                linestyle=LINESTYLES[split],
                linewidth=1.65,
                label=LABELS[split],
            )

        ax.set_xlim(lo - pad, hi + pad)
        ax.set_xlabel(xlabel)
        ax.grid(True, color="#D0D0D0", linewidth=0.45, alpha=0.75)
        ax.text(
            0.02,
            0.96,
            label,
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=9,
            fontweight="bold",
        )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[0, 0].set_ylabel("Sample fraction per bin (%)")
    axes[0, 1].set_ylabel("Sample fraction per bin (%)")
    axes[1, 0].set_ylabel("Sample fraction per bin (%)")
    axes[1, 1].set_ylabel("Sample fraction per bin (%)")
    axes[0, 1].legend(
        frameon=True,
        framealpha=0.92,
        edgecolor="#FFFFFF",
        facecolor="#FFFFFF",
        loc="upper right",
        handlelength=2.8,
        borderpad=0.35,
    )

    fig.tight_layout(pad=0.35, w_pad=1.2, h_pad=1.0)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_STEM.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(OUT_STEM.with_suffix(".png"), dpi=450, bbox_inches="tight")
    plt.close(fig)

    for suffix in (".pdf", ".png"):
        print(OUT_STEM.with_suffix(suffix))


if __name__ == "__main__":
    main()
