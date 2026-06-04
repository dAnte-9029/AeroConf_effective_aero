#!/usr/bin/env python3
"""Render the IsaacLab flapping-bot URDF with publication-style frame annotations.

Run with:
  PYOPENGL_PLATFORM=egl MPLCONFIGDIR=/tmp/matplotlib-cache \
    /home/zn/anaconda3/envs/paper_figures/bin/python scripts/render_urdf_reference_frame_pyrender.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyrender
import trimesh
from urdfpy import URDF


URDF_PATH = Path(
    "/home/zn/IsaacLab/source/isaaclab_assets/data/flapping_bot/robots/"
    "flap_robot_552/urdf/flap_robot_552.urdf"
)
OUT_DIR = Path("/home/zn/paper/AeroConf_effective_aero/figures")
OUT_STEM = "urdf_reference_frame_pyrender"

# Measured CG expressed from the IMU-origin metadata frame in FRD.
CG_FRD_FROM_IMU = np.array([-0.12154, 0.00541, -0.04298])


def frd_to_urdf(v_frd: np.ndarray) -> np.ndarray:
    # URDF geometry uses x-forward, y-left, z-up. The paper body frame is FRD.
    return np.array([v_frd[0], -v_frd[1], -v_frd[2]], dtype=float)


def look_at_pose(eye: np.ndarray, target: np.ndarray, up: np.ndarray) -> np.ndarray:
    """Return camera-to-world pose for a pyrender/OpenGL camera."""
    eye = np.asarray(eye, dtype=float)
    target = np.asarray(target, dtype=float)
    up = np.asarray(up, dtype=float)
    z_axis = eye - target
    z_axis /= np.linalg.norm(z_axis)
    x_axis = np.cross(up, z_axis)
    x_axis /= np.linalg.norm(x_axis)
    y_axis = np.cross(z_axis, x_axis)

    pose = np.eye(4)
    pose[:3, 0] = x_axis
    pose[:3, 1] = y_axis
    pose[:3, 2] = z_axis
    pose[:3, 3] = eye
    return pose


def transform_points(points: np.ndarray, transform: np.ndarray) -> np.ndarray:
    hom = np.c_[points, np.ones(len(points))]
    return (transform @ hom.T).T[:, :3]


def material(color: tuple[float, float, float, float], roughness: float = 0.62) -> pyrender.MetallicRoughnessMaterial:
    return pyrender.MetallicRoughnessMaterial(
        baseColorFactor=color,
        metallicFactor=0.0,
        roughnessFactor=roughness,
        alphaMode="BLEND" if color[3] < 1.0 else "OPAQUE",
    )


def link_style(mesh: trimesh.Trimesh, pose: np.ndarray) -> tuple[tuple[float, float, float, float], str]:
    center = pose[:3, 3]
    n_vertices = len(mesh.vertices)
    if n_vertices > 10_000:
        return (0.62, 0.64, 0.66, 0.82), "body"
    if center[0] < -0.45 and abs(center[1]) < 0.05:
        return (0.86, 0.43, 0.12, 0.78), "rudder"
    if center[0] < -0.45:
        return (0.33, 0.64, 0.30, 0.78), "tail"
    return (0.33, 0.67, 0.88, 0.58), "wing"


def create_scene(robot: URDF) -> tuple[pyrender.Scene, np.ndarray]:
    scene = pyrender.Scene(bg_color=[1.0, 1.0, 1.0, 1.0], ambient_light=[0.54, 0.54, 0.54])
    visual_fk = robot.visual_trimesh_fk()
    all_points = []

    for mesh, pose in visual_fk.items():
        color, _ = link_style(mesh, pose)
        mesh_for_render = mesh.copy()
        if len(mesh_for_render.faces) > 25_000:
            try:
                mesh_for_render = mesh_for_render.simplify_quadric_decimation(face_count=25_000)
            except ModuleNotFoundError:
                pass
        render_mesh = pyrender.Mesh.from_trimesh(mesh_for_render, material=material(color), smooth=True)
        scene.add(render_mesh, pose=pose)
        all_points.append(transform_points(mesh.vertices, pose))

    points = np.vstack(all_points)
    return scene, points


def camera_from_points(points: np.ndarray) -> tuple[np.ndarray, float, float, np.ndarray]:
    target = np.array([-0.18, 0.0, 0.01])
    eye = np.array([0.28, -1.25, 0.48])
    up = np.array([0.0, 0.0, 1.0])
    pose = look_at_pose(eye, target, up)

    world_to_camera = np.linalg.inv(pose)
    cam_points = transform_points(points, world_to_camera)
    xmag = float(np.max(np.abs(cam_points[:, 0])) * 1.04)
    ymag = float(np.max(np.abs(cam_points[:, 1])) * 1.06)
    return pose, xmag, ymag, world_to_camera


def project(points: np.ndarray, world_to_camera: np.ndarray, xmag: float, ymag: float, width: int, height: int) -> np.ndarray:
    cam = transform_points(np.asarray(points, dtype=float).reshape(-1, 3), world_to_camera)
    x_ndc = cam[:, 0] / xmag
    y_ndc = cam[:, 1] / ymag
    px = (x_ndc + 1.0) * 0.5 * width
    py = (1.0 - y_ndc) * 0.5 * height
    return np.c_[px, py]


def overlay_annotations(
    color: np.ndarray,
    world_to_camera: np.ndarray,
    xmag: float,
    ymag: float,
    output_stem: Path,
) -> None:
    h, w = color.shape[:2]
    imu = np.zeros(3)
    cg = frd_to_urdf(CG_FRD_FROM_IMU)

    x_axis_len = 0.155
    y_axis_len = 0.205
    z_axis_len = 0.155
    axes = [
        (cg, cg + frd_to_urdf(np.array([x_axis_len, 0.0, 0.0])), r"$x_B$", "#0072B2", (7, -2)),
        (cg, cg + frd_to_urdf(np.array([0.0, y_axis_len, 0.0])), r"$y_B$", "#009E73", (-78, 18)),
        (cg, cg + frd_to_urdf(np.array([0.0, 0.0, z_axis_len])), r"$z_B$", "#D55E00", (8, 14)),
    ]

    fig, ax = plt.subplots(figsize=(5.2, 3.0), dpi=300)
    ax.imshow(color)
    ax.set_axis_off()

    def p(point: np.ndarray) -> np.ndarray:
        return project(point[None, :], world_to_camera, xmag, ymag, w, h)[0]

    cg_px = p(cg)

    for start, end, label, color_name, offset in axes:
        start_px = p(start)
        end_px = p(end)
        ax.annotate(
            "",
            xy=end_px,
            xytext=start_px,
            arrowprops=dict(arrowstyle="-|>", color=color_name, lw=2.4, shrinkA=0, shrinkB=0, mutation_scale=14),
            zorder=10,
        )
        ax.text(
            end_px[0] + offset[0],
            end_px[1] + offset[1],
            label,
            color=color_name,
            fontsize=13,
            weight="bold",
            zorder=11,
        )

    ax.scatter([cg_px[0]], [cg_px[1]], s=52, color="#CC3311", edgecolor="white", linewidth=0.9, zorder=20)
    ax.text(cg_px[0] - 18, cg_px[1] - 16, "CG", color="#CC3311", fontsize=10, weight="bold", zorder=21)

    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(output_stem.with_suffix(".png"), dpi=450, bbox_inches="tight", pad_inches=0.01)
    fig.savefig(output_stem.with_suffix(".pdf"), dpi=450, bbox_inches="tight", pad_inches=0.01)
    plt.close(fig)


def main() -> None:
    robot = URDF.load(str(URDF_PATH))
    scene, points = create_scene(robot)

    camera_pose, xmag, ymag, world_to_camera = camera_from_points(points)
    camera = pyrender.OrthographicCamera(xmag=xmag, ymag=ymag, znear=0.01, zfar=10.0)
    scene.add(camera, pose=camera_pose)

    light_pose = look_at_pose(np.array([0.15, -0.9, 1.2]), np.array([-0.18, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]))
    scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=3.3), pose=light_pose)
    scene.add(pyrender.DirectionalLight(color=np.ones(3), intensity=1.4), pose=look_at_pose(np.array([-0.6, 0.8, 0.7]), np.zeros(3), np.array([0.0, 0.0, 1.0])))

    renderer = pyrender.OffscreenRenderer(viewport_width=1800, viewport_height=1080)
    color, _ = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)
    renderer.delete()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output_stem = OUT_DIR / OUT_STEM
    overlay_annotations(color, world_to_camera, xmag, ymag, output_stem)
    print(f"URDF: {URDF_PATH}")
    print(f"PNG: {output_stem.with_suffix('.png')}")
    print(f"PDF: {output_stem.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()
