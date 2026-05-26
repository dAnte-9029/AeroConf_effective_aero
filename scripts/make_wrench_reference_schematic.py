#!/usr/bin/env python3
"""Create a schematic for the effective-wrench reference frame."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle


OUT_ROOT = Path(__file__).resolve().parents[1] / "figures"
OUT_STEM = OUT_ROOT / "wrench_reference_schematic"


def arrow(ax, start, end, color, label, text_offset=(0.0, 0.0), lw=1.5):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=lw,
            color=color,
            shrinkA=0,
            shrinkB=0,
        )
    )
    ax.text(
        end[0] + text_offset[0],
        end[1] + text_offset[1],
        label,
        color=color,
        fontsize=8,
        ha="center",
        va="center",
    )


def main() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, ax = plt.subplots(figsize=(3.45, 2.45))
    ax.set_aspect("equal")
    ax.axis("off")

    # Top-view schematic, not to scale.
    fuselage = Rectangle((-0.15, -0.08), 1.65, 0.16, facecolor="#E8E8E8", edgecolor="#555555", linewidth=0.9)
    ax.add_patch(fuselage)
    nose = Polygon([[1.50, -0.08], [1.74, 0.0], [1.50, 0.08]], closed=True, facecolor="#D8D8D8", edgecolor="#555555", linewidth=0.9)
    ax.add_patch(nose)
    tail = Polygon([[-0.20, -0.14], [-0.02, 0.0], [-0.20, 0.14]], closed=True, facecolor="#D8D8D8", edgecolor="#555555", linewidth=0.9)
    ax.add_patch(tail)
    left_wing = Polygon([[0.45, 0.05], [0.18, 0.85], [1.08, 0.18]], closed=True, facecolor="#BFD7EA", edgecolor="#35688B", alpha=0.95, linewidth=0.9)
    right_wing = Polygon([[0.45, -0.05], [0.18, -0.85], [1.08, -0.18]], closed=True, facecolor="#BFD7EA", edgecolor="#35688B", alpha=0.95, linewidth=0.9)
    ax.add_patch(left_wing)
    ax.add_patch(right_wing)

    cg = (0.62, 0.0)
    imu = (0.48, -0.05)
    ax.add_patch(Circle(cg, 0.035, facecolor="#D55E00", edgecolor="#7A2A00", linewidth=0.8))
    ax.add_patch(Circle(imu, 0.026, facecolor="#CC79A7", edgecolor="#7A3C65", linewidth=0.8))
    ax.text(cg[0], cg[1] + 0.13, "CG / wrench origin\nTBD measured location", color="#D55E00", ha="center", fontsize=7)
    ax.text(imu[0] - 0.13, imu[1] - 0.18, "IMU offset\nTBD", color="#CC79A7", ha="center", fontsize=7)

    arrow(ax, cg, (1.10, 0.0), "#0072B2", r"$x_B$ forward", (0.18, 0.0))
    arrow(ax, cg, (0.62, -0.48), "#0072B2", r"$y_B$ right", (0.02, -0.08))
    ax.add_patch(Circle((0.30, 0.42), 0.055, facecolor="white", edgecolor="#0072B2", linewidth=1.1))
    ax.text(0.30, 0.42, r"$z_B$", color="#0072B2", ha="center", va="center", fontsize=7)
    ax.text(0.30, 0.29, "down", color="#0072B2", ha="center", fontsize=7)

    arrow(ax, (-0.95, 0.62), (-0.55, 0.62), "#009E73", r"$N$", (0.06, 0.0), lw=1.2)
    arrow(ax, (-0.95, 0.62), (-0.95, 0.22), "#009E73", r"$E$", (0.0, -0.06), lw=1.2)
    ax.add_patch(Circle((-0.73, 0.38), 0.045, facecolor="white", edgecolor="#009E73", linewidth=1.0))
    ax.text(-0.73, 0.38, r"$D$", color="#009E73", ha="center", va="center", fontsize=7)
    ax.text(-0.86, 0.78, "NED frame", color="#009E73", fontsize=7, ha="left")

    ax.text(
        -0.92,
        -0.72,
        r"$\mathbf{y}=[\mathbf{F}_{\mathrm{eff}}^B,\mathbf{M}_{\mathrm{eff,CG}}^B]$",
        fontsize=8,
        ha="left",
        va="center",
    )
    ax.text(
        -0.92,
        -0.92,
        "Component simulator loads are shifted to the same CG reference.",
        fontsize=7,
        ha="left",
        va="center",
    )
    ax.text(0.40, 0.98, "schematic, not to scale", fontsize=7, color="#555555", ha="center")

    ax.set_xlim(-1.05, 1.95)
    ax.set_ylim(-1.05, 1.08)
    fig.tight_layout(pad=0.02)

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_STEM.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(OUT_STEM.with_suffix(".png"), dpi=450, bbox_inches="tight")
    plt.close(fig)
    for suffix in (".pdf", ".png"):
        print(OUT_STEM.with_suffix(suffix))


if __name__ == "__main__":
    main()
