#!/usr/bin/env python3
"""Create the editable real-flight correction pipeline figure."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


OUT_ROOT = Path(__file__).resolve().parents[1] / "figures"
OUT_STEM = OUT_ROOT / "real_flight_correction_pipeline"

BLOCKS = [
    (
        "Outdoor Flight\nPlatform",
        [
            "PX4 logs",
            "state estimates",
            "airdata",
            "actuator commands",
            "flap phase/frequency",
        ],
    ),
    (
        "Preprocessing",
        [
            "whole-log split",
            "resampling",
            "time alignment",
            "smoothing",
        ],
    ),
    (
        "Effective-Wrench\nLabels",
        [
            "measured mass",
            "measured CG",
            "measured inertia",
            "force/moment reconstruction",
        ],
    ),
    (
        "DeLaurier-Style\nPrior",
        [
            "fast low-dimensional prior",
            "bounded force calibration",
        ],
    ),
    (
        "Structured\nCorrection",
        [
            "phase terms",
            "airspeed/AoA/frequency",
            "controls and body rates",
            "deployable inputs only",
        ],
    ),
    (
        "Diagnostics\nand Use",
        [
            "corrected wrench map",
            "residual structure",
            "replay diagnostic only",
        ],
    ),
]


def _add_block(ax: plt.Axes, x: float, y: float, w: float, h: float, title: str, lines: list[str], color: str) -> None:
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.015,rounding_size=0.035",
        linewidth=1.0,
        edgecolor="#243447",
        facecolor=color,
    )
    ax.add_patch(box)
    ax.text(
        x + w / 2.0,
        y + h - 0.16,
        title,
        ha="center",
        va="top",
        fontsize=8.6,
        fontweight="bold",
        color="#17212b",
        linespacing=1.05,
    )
    body = "\n".join(lines)
    ax.text(
        x + 0.08,
        y + h - 0.46,
        body,
        ha="left",
        va="top",
        fontsize=6.8,
        color="#17212b",
        linespacing=1.35,
    )


def main() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )

    colors = ["#d7ecff", "#e7f3df", "#fff1c7", "#eadff5", "#f8dfdc", "#e7e7e7"]
    fig, ax = plt.subplots(figsize=(7.35, 2.85))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    left = 0.025
    gap = 0.018
    w = (0.95 - 5 * gap) / 6.0
    y = 0.30
    h = 0.56
    xs = [left + i * (w + gap) for i in range(6)]

    for i, ((title, lines), color) in enumerate(zip(BLOCKS, colors)):
        _add_block(ax, xs[i], y, w, h, title, lines, color)
        if i < len(BLOCKS) - 1:
            arrow = FancyArrowPatch(
                (xs[i] + w + 0.004, y + h / 2.0),
                (xs[i + 1] - 0.004, y + h / 2.0),
                arrowstyle="-|>",
                mutation_scale=10,
                linewidth=1.0,
                color="#243447",
            )
            ax.add_patch(arrow)

    ax.text(
        0.5,
        0.17,
        "Validated here: log-conditioned effective-wrench prediction.    Not claimed here: closed-loop simulator validation.",
        ha="center",
        va="center",
        fontsize=7.8,
        color="#17212b",
        bbox={"boxstyle": "round,pad=0.25", "facecolor": "#ffffff", "edgecolor": "#8a8a8a", "linewidth": 0.8},
    )
    ax.text(
        0.025,
        0.955,
        "Real-flight data pathway for correcting a low-dimensional flapping-wing simulator prior",
        ha="left",
        va="center",
        fontsize=9.0,
        fontweight="bold",
        color="#17212b",
    )

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_STEM.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.03)
    fig.savefig(OUT_STEM.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.03)
    fig.savefig(OUT_STEM.with_suffix(".png"), dpi=450, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)

    for suffix in (".svg", ".pdf", ".png"):
        print(OUT_STEM.with_suffix(suffix))


if __name__ == "__main__":
    main()
