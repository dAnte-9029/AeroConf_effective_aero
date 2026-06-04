#!/usr/bin/env python3
"""Render the IsaacLab flapping-bot URDF with paper reference-frame annotations."""

from __future__ import annotations

import math
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


URDF_PATH = Path(
    "/home/zn/IsaacLab/source/isaaclab_assets/data/flapping_bot/robots/"
    "flap_robot_552/urdf/flap_robot_552.urdf"
)
OUT_DIR = Path("/home/zn/paper/AeroConf_effective_aero/figures")

# Paper metadata: measured CG expressed from the IMU-origin metadata frame in FRD.
CG_FRD_FROM_IMU = np.array([-0.12154, 0.00541, -0.04298])


def rpy_matrix(rpy: np.ndarray) -> np.ndarray:
    roll, pitch, yaw = rpy
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return rz @ ry @ rx


def origin_transform(elem: ET.Element | None) -> np.ndarray:
    transform = np.eye(4)
    if elem is None:
        return transform
    xyz = np.fromstring(elem.attrib.get("xyz", "0 0 0"), sep=" ")
    rpy = np.fromstring(elem.attrib.get("rpy", "0 0 0"), sep=" ")
    transform[:3, :3] = rpy_matrix(rpy)
    transform[:3, 3] = xyz
    return transform


def read_binary_stl(path: Path) -> np.ndarray:
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError(f"STL file is too small: {path}")
    n_tri = struct.unpack_from("<I", data, 80)[0]
    expected = 84 + 50 * n_tri
    if expected > len(data):
        raise ValueError(f"Unexpected STL size for {path}")
    vertices = np.empty((n_tri, 3, 3), dtype=np.float32)
    offset = 84
    for i in range(n_tri):
        # normal is ignored; three vertices follow.
        vals = struct.unpack_from("<12f", data, offset)
        vertices[i] = np.array(vals[3:12], dtype=np.float32).reshape(3, 3)
        offset += 50
    return vertices


def apply_transform(triangles: np.ndarray, transform: np.ndarray) -> np.ndarray:
    flat = triangles.reshape(-1, 3)
    hom = np.c_[flat, np.ones(len(flat))]
    out = (transform @ hom.T).T[:, :3]
    return out.reshape(triangles.shape)


def collect_link_transforms(root: ET.Element) -> dict[str, np.ndarray]:
    transforms = {"base_link": np.eye(4)}
    joints = []
    for joint in root.findall("joint"):
        parent = joint.find("parent").attrib["link"]
        child = joint.find("child").attrib["link"]
        joints.append((parent, child, origin_transform(joint.find("origin"))))

    unresolved = joints[:]
    while unresolved:
        next_unresolved = []
        for parent, child, tf in unresolved:
            if parent in transforms:
                transforms[child] = transforms[parent] @ tf
            else:
                next_unresolved.append((parent, child, tf))
        if len(next_unresolved) == len(unresolved):
            missing = ", ".join(child for _, child, _ in next_unresolved)
            raise RuntimeError(f"Could not resolve URDF link transforms: {missing}")
        unresolved = next_unresolved
    return transforms


def frd_to_urdf(v_frd: np.ndarray) -> np.ndarray:
    # The URDF geometry uses x-forward, y-left, z-up. The paper body frame is FRD.
    return np.array([v_frd[0], -v_frd[1], -v_frd[2]])


def set_equal_axes(ax, points: np.ndarray, pad: float = 0.08) -> None:
    mins = points.min(axis=0)
    maxs = points.max(axis=0)
    center = (mins + maxs) / 2
    radius = max(maxs - mins) / 2 + pad
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)


def add_axis(ax, origin: np.ndarray, direction: np.ndarray, label: str, color: str, length: float) -> None:
    direction = direction / np.linalg.norm(direction)
    ax.quiver(
        origin[0],
        origin[1],
        origin[2],
        direction[0],
        direction[1],
        direction[2],
        length=length,
        normalize=True,
        color=color,
        linewidth=2.4,
        arrow_length_ratio=0.18,
    )
    p = origin + direction * length * 1.12
    ax.text(p[0], p[1], p[2], label, color=color, fontsize=9, weight="bold")


def main() -> None:
    root = ET.parse(URDF_PATH).getroot()
    link_tfs = collect_link_transforms(root)
    urdf_dir = URDF_PATH.parent

    colors = {
        "base_link": "#8a8f98",
        "left_wing": "#6aaed6",
        "right_wing": "#6aaed6",
        "left_tail": "#79b473",
        "right_tail": "#79b473",
        "rudder": "#d98c4a",
    }

    rng = np.random.default_rng(7)
    all_triangles = []
    all_points = []
    for link in root.findall("link"):
        name = link.attrib["name"]
        visual = link.find("visual")
        if visual is None:
            continue
        mesh = visual.find("geometry/mesh")
        if mesh is None:
            continue
        mesh_path = (urdf_dir / mesh.attrib["filename"]).resolve()
        triangles = read_binary_stl(mesh_path)
        if len(triangles) > 8000:
            keep = rng.choice(len(triangles), size=8000, replace=False)
            triangles = triangles[keep]
        triangles = apply_transform(triangles, link_tfs[name] @ origin_transform(visual.find("origin")))
        all_triangles.append((name, triangles))
        all_points.append(triangles.reshape(-1, 3))

    points = np.vstack(all_points)
    imu_origin = np.zeros(3)
    cg = frd_to_urdf(CG_FRD_FROM_IMU)

    fig = plt.figure(figsize=(5.2, 2.8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_proj_type("ortho")

    for name, triangles in all_triangles:
        poly = Poly3DCollection(
            triangles,
            facecolor=colors.get(name, "#999999"),
            edgecolor=(0.12, 0.12, 0.12, 0.11),
            linewidth=0.05,
            alpha=0.50 if "wing" in name else 0.78,
        )
        ax.add_collection3d(poly)

    # IMU/URDF origin marker.
    ax.scatter(*imu_origin, color="black", s=24, depthshade=False)

    # Measured CG marker and offset vector.
    ax.scatter(*cg, color="#cc3311", s=46, depthshade=False)
    ax.text(cg[0] - 0.03, cg[1] - 0.04, cg[2] + 0.035, "CG", color="#cc3311", fontsize=9, weight="bold")
    ax.quiver(
        imu_origin[0],
        imu_origin[1],
        imu_origin[2],
        cg[0],
        cg[1],
        cg[2],
        length=1.0,
        normalize=False,
        color="#cc3311",
        linewidth=1.5,
        arrow_length_ratio=0.16,
    )
    mid = 0.55 * cg
    ax.text(mid[0], mid[1] - 0.045, mid[2] + 0.02, r"$\mathbf{r}_{\mathrm{CG}}^I$", color="#cc3311", fontsize=8)

    # Body FRD axes attached to measured CG, expressed in URDF coordinates.
    axis_len = 0.22
    add_axis(ax, cg, frd_to_urdf(np.array([1.0, 0.0, 0.0])), r"$x_B$", "#0072B2", axis_len)
    add_axis(ax, cg, frd_to_urdf(np.array([0.0, 1.0, 0.0])), r"$y_B$", "#009E73", axis_len)
    add_axis(ax, cg, frd_to_urdf(np.array([0.0, 0.0, 1.0])), r"$z_B$", "#D55E00", axis_len)

    set_equal_axes(ax, np.vstack([points, imu_origin[None, :], cg[None, :]]), pad=0.05)
    try:
        ax.set_box_aspect((1.0, 1.0, 0.38), zoom=2.05)
    except TypeError:
        ax.set_box_aspect((1.0, 1.0, 0.38))
    ax.view_init(elev=22, azim=-57, roll=0)
    ax.set_axis_off()
    ax.grid(False)
    ax.set_position([-0.08, -0.20, 1.16, 1.34])
    fig.subplots_adjust(0.00, 0.00, 1.00, 1.00)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT_DIR / f"urdf_reference_frame_annotated.{ext}", dpi=450, bbox_inches="tight", pad_inches=0.02)
    print(f"URDF: {URDF_PATH}")
    print(f"PDF: {OUT_DIR / 'urdf_reference_frame_annotated.pdf'}")
    print(f"PNG: {OUT_DIR / 'urdf_reference_frame_annotated.png'}")


if __name__ == "__main__":
    main()
