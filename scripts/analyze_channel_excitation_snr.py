#!/usr/bin/env python3
"""Channel excitation and predictability diagnostics for the AeroConf draft."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-cache")

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_ROOT = REPO_ROOT / "analysis" / "channel_excitation_snr"
FIG_ROOT = OUT_ROOT / "figures"

SPLIT_ROOT = Path(
    "/home/zn/flap-system-identification/dataset/"
    "canonical_v0.2_training_ready_split_measured_massprops_sg0p03_v1"
)
ALIGNED_ROOT = Path(
    "/home/zn/flap-system-identification/artifacts/"
    "20260602_bc_correction_measured_massprops_v1/evaluation/aligned"
)
PER_CHANNEL_METRICS = Path(
    "/home/zn/flap-system-identification/artifacts/"
    "20260602_bc_correction_measured_massprops_v1/evaluation/per_channel_metrics.csv"
)
FREQUENCY_SUMMARY = Path(
    "/home/zn/flap-system-identification/artifacts/"
    "20260602_residual_diagnostics_measured_massprops_v1/frequency/frequency_residual_summary.csv"
)

TARGETS = ["fx_b", "fy_b", "fz_b", "mx_b", "my_b", "mz_b"]
TARGET_LABELS = {
    "fx_b": r"$f_{x,B}$",
    "fy_b": r"$f_{y,B}$",
    "fz_b": r"$f_{z,B}$",
    "mx_b": r"$m_{x,B}$",
    "my_b": r"$m_{y,B}$",
    "mz_b": r"$m_{z,B}$",
}
CONDITION_BY_TARGET = {
    "fx_b": ("cycle_flap_frequency_hz", "Cycle flap frequency (Hz)"),
    "fy_b": ("beta_proxy_rad", "Sideslip proxy (rad)"),
    "fz_b": ("alpha_rad", "Pitch/AoA proxy (rad)"),
    "mx_b": ("p_dot_smooth", r"$\dot{p}$ smooth (rad/s$^2$)"),
    "my_b": ("elevon_sum", "Elevon sum"),
    "mz_b": ("servo_rudder", "Rudder command"),
}
OKABE_ITO = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "black": "#000000",
    "gray": "#777777",
}


@dataclass
class DatasetBundle:
    split: str
    frame: pd.DataFrame


def _rotation_body_to_ned_from_quat(df: pd.DataFrame) -> np.ndarray:
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


def _euler_from_quat(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
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
    roll = np.arctan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch = np.arcsin(np.clip(2.0 * (w * y - z * x), -1.0, 1.0))
    yaw = np.arctan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return roll, pitch, yaw


def _add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    phase = out["phase_corrected_rad"].to_numpy(dtype=float, copy=True)
    out["phase_sin_1"] = np.sin(phase)
    out["phase_cos_1"] = np.cos(phase)
    out["phase_sin_2"] = np.sin(2.0 * phase)
    out["phase_cos_2"] = np.cos(2.0 * phase)
    out["elevon_sum"] = 0.5 * (out["servo_left_elevon"] + out["servo_right_elevon"])
    out["elevon_diff"] = 0.5 * (out["servo_left_elevon"] - out["servo_right_elevon"])
    out["p"] = out["vehicle_angular_velocity.xyz[0]"]
    out["q"] = out["vehicle_angular_velocity.xyz[1]"]
    out["r"] = out["vehicle_angular_velocity.xyz[2]"]
    out["p_dot_raw"] = out["vehicle_angular_velocity.xyz_derivative[0]"]
    out["q_dot_raw"] = out["vehicle_angular_velocity.xyz_derivative[1]"]
    out["r_dot_raw"] = out["vehicle_angular_velocity.xyz_derivative[2]"]
    out["p_dot_smooth"] = out["vehicle_angular_velocity.xyz_derivative_smooth[0]"]
    out["q_dot_smooth"] = out["vehicle_angular_velocity.xyz_derivative_smooth[1]"]
    out["r_dot_smooth"] = out["vehicle_angular_velocity.xyz_derivative_smooth[2]"]
    out["true_airspeed_m_s"] = out["airspeed_validated.true_airspeed_m_s"]
    out["alpha_rad"] = out["airspeed_validated.pitch_filtered"]
    out["dynamic_pressure_pa"] = 0.5 * out["vehicle_air_data.rho"] * out["true_airspeed_m_s"] ** 2

    roll, pitch, yaw = _euler_from_quat(out)
    out["roll_rad"] = roll
    out["pitch_rad"] = pitch
    out["yaw_rad"] = yaw

    rot_body_to_ned = _rotation_body_to_ned_from_quat(out)
    velocity_n = out[["vehicle_local_position.vx", "vehicle_local_position.vy", "vehicle_local_position.vz"]].to_numpy(
        dtype=float, copy=True
    )
    wind_n = np.zeros_like(velocity_n)
    wind_n[:, 0] = out["wind.windspeed_north"].to_numpy(dtype=float, copy=True)
    wind_n[:, 1] = out["wind.windspeed_east"].to_numpy(dtype=float, copy=True)
    v_air_n = velocity_n - wind_n
    v_air_b = np.einsum("nji,nj->ni", rot_body_to_ned, v_air_n)
    speed = np.linalg.norm(v_air_b, axis=1)
    out["v_air_b_x"] = v_air_b[:, 0]
    out["v_air_b_y"] = v_air_b[:, 1]
    out["v_air_b_z"] = v_air_b[:, 2]
    out["beta_proxy_rad"] = np.arcsin(np.clip(np.divide(v_air_b[:, 1], speed, out=np.zeros_like(speed), where=speed > 1e-8), -1.0, 1.0))
    return out


def load_split(split: str) -> DatasetBundle:
    samples = pd.read_parquet(SPLIT_ROOT / f"{split}_samples.parquet")
    samples = _add_derived_features(samples)
    return DatasetBundle(split=split, frame=samples)


def _target_prediction_frame(split: str) -> pd.DataFrame:
    aligned = pd.read_parquet(ALIGNED_ROOT / f"{split}_phase_structured_aligned.parquet")
    keep = ["timestamp_us", "log_id", "segment_id", "time_s"]
    for target in TARGETS:
        keep.extend([f"label_{target}", f"prior_{target}", f"corrected_{target}"])
    return aligned[keep].copy()


def _merge_predictions(samples: pd.DataFrame, split: str) -> pd.DataFrame:
    preds = _target_prediction_frame(split)
    merge_cols = ["timestamp_us", "log_id", "segment_id"]
    merged = samples.merge(preds.drop(columns=["time_s"]), on=merge_cols, how="inner", validate="one_to_one")
    if len(merged) != len(samples):
        raise ValueError(f"merge dropped rows for {split}: {len(samples)} -> {len(merged)}")
    return merged


def r2_score(y: np.ndarray, yhat: np.ndarray) -> float:
    finite = np.isfinite(y) & np.isfinite(yhat)
    if finite.sum() < 2:
        return float("nan")
    yy = y[finite]
    pp = yhat[finite]
    denom = np.sum((yy - yy.mean()) ** 2)
    if denom <= 0:
        return float("nan")
    return float(1.0 - np.sum((yy - pp) ** 2) / denom)


def rmse(y: np.ndarray, yhat: np.ndarray) -> float:
    finite = np.isfinite(y) & np.isfinite(yhat)
    return float(np.sqrt(np.mean((y[finite] - yhat[finite]) ** 2))) if finite.any() else float("nan")


def mae(y: np.ndarray, yhat: np.ndarray) -> float:
    finite = np.isfinite(y) & np.isfinite(yhat)
    return float(np.mean(np.abs(y[finite] - yhat[finite]))) if finite.any() else float("nan")


def channel_excitation_summary(test: pd.DataFrame) -> pd.DataFrame:
    metrics = pd.read_csv(PER_CHANNEL_METRICS)
    phase_rows = metrics[metrics["split"].eq("test") & metrics["model"].eq("phase_structured")]
    rows = []
    for target in TARGETS:
        y = test[target].to_numpy(dtype=float, copy=True)
        y = y[np.isfinite(y)]
        m = phase_rows[phase_rows["target"].eq(target)].iloc[0]
        med = float(np.median(y))
        centered = y - med
        std = float(np.std(y))
        rows.append(
            {
                "target": target,
                "n": int(len(y)),
                "mean": float(np.mean(y)),
                "median": med,
                "std": std,
                "rms": float(np.sqrt(np.mean(y**2))),
                "p95_minus_p5": float(np.percentile(y, 95) - np.percentile(y, 5)),
                "p99_minus_p1": float(np.percentile(y, 99) - np.percentile(y, 1)),
                "activity_frac_abs_centered_gt_0p5std": float(np.mean(np.abs(centered) > 0.5 * std)) if std > 0 else np.nan,
                "activity_frac_abs_centered_gt_1std": float(np.mean(np.abs(centered) > std)) if std > 0 else np.nan,
                "corrected_rmse": float(m["rmse"]),
                "corrected_mae": float(m["mae"]),
                "corrected_r2": float(m["r2"]),
                "corrected_rmse_over_std": float(m["rmse_over_std"]),
                "corrected_snr_proxy_std_over_rmse": float(1.0 / m["rmse_over_std"]),
            }
        )
    return pd.DataFrame(rows)


FEATURE_GROUPS = {
    "phase": ["phase_sin_1", "phase_cos_1", "phase_sin_2", "phase_cos_2"],
    "condition": ["true_airspeed_m_s", "dynamic_pressure_pa", "alpha_rad", "beta_proxy_rad", "cycle_flap_frequency_hz"],
    "controls": ["motor_cmd_0", "servo_left_elevon", "servo_right_elevon", "servo_rudder", "elevon_sum", "elevon_diff"],
    "rates": ["p", "q", "r"],
}
DIAGNOSTIC_FEATURE_GROUPS = {
    "angular_derivatives_label_diagnostic": ["p_dot_smooth", "q_dot_smooth", "r_dot_smooth"],
}


def _ridge_fit_predict(train: pd.DataFrame, test: pd.DataFrame, features: list[str], target: str, alpha: float = 1.0) -> tuple[np.ndarray, int]:
    cols = [col for col in features if col in train.columns and col in test.columns]
    tr = train[cols + [target]].replace([np.inf, -np.inf], np.nan).dropna()
    te = test[cols + [target]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(cols) == 0 or len(tr) < len(cols) + 5 or len(te) == 0:
        return np.full(len(test), np.nan), 0
    x_train = tr[cols].to_numpy(dtype=float, copy=True)
    y_train = tr[target].to_numpy(dtype=float, copy=True)
    x_test = test[cols].to_numpy(dtype=float, copy=True)
    mean = x_train.mean(axis=0)
    scale = x_train.std(axis=0)
    scale[scale < 1e-9] = 1.0
    xs = (x_train - mean) / scale
    xt = (x_test - mean) / scale
    xs = np.column_stack([np.ones(len(xs)), xs])
    xt = np.column_stack([np.ones(len(xt)), xt])
    reg = np.eye(xs.shape[1]) * alpha
    reg[0, 0] = 0.0
    beta = np.linalg.solve(xs.T @ xs + reg, xs.T @ y_train)
    return xt @ beta, len(cols)


def feature_group_ridge(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_specs = dict(FEATURE_GROUPS)
    group_specs["phase+condition"] = FEATURE_GROUPS["phase"] + FEATURE_GROUPS["condition"]
    group_specs["condition+controls+rates"] = FEATURE_GROUPS["condition"] + FEATURE_GROUPS["controls"] + FEATURE_GROUPS["rates"]
    group_specs["all"] = sorted({col for cols in FEATURE_GROUPS.values() for col in cols})
    group_specs.update(DIAGNOSTIC_FEATURE_GROUPS)
    for target in TARGETS:
        y = test[target].to_numpy(dtype=float, copy=True)
        for group, features in group_specs.items():
            pred, n_features = _ridge_fit_predict(train, test, features, target, alpha=10.0)
            rows.append(
                {
                    "target": target,
                    "feature_group": group,
                    "n_features": n_features,
                    "test_r2": r2_score(y, pred),
                    "test_rmse": rmse(y, pred),
                    "test_mae": mae(y, pred),
                }
            )
    return pd.DataFrame(rows)


def top_correlations(test: pd.DataFrame) -> pd.DataFrame:
    features = sorted({col for cols in FEATURE_GROUPS.values() for col in cols})
    rows = []
    for target in TARGETS:
        y = test[target].to_numpy(dtype=float, copy=True)
        for feature in features:
            x = test[feature].to_numpy(dtype=float, copy=True)
            finite = np.isfinite(x) & np.isfinite(y)
            if finite.sum() < 10 or np.nanstd(x[finite]) <= 1e-12 or np.nanstd(y[finite]) <= 1e-12:
                corr = np.nan
            else:
                corr = float(np.corrcoef(x[finite], y[finite])[0, 1])
            rows.append({"target": target, "feature": feature, "pearson_r": corr, "abs_pearson_r": abs(corr) if np.isfinite(corr) else np.nan})
    out = pd.DataFrame(rows)
    return out.sort_values(["target", "abs_pearson_r"], ascending=[True, False])


def condition_bin_excitation(test: pd.DataFrame, bins: int = 5) -> pd.DataFrame:
    rows = []
    for target, (condition, _) in CONDITION_BY_TARGET.items():
        frame = test[[condition, target, f"corrected_{target}"]].replace([np.inf, -np.inf], np.nan).dropna()
        if frame.empty:
            continue
        try:
            frame["bin"] = pd.qcut(frame[condition], q=bins, duplicates="drop")
        except ValueError:
            continue
        for bin_index, (interval, group) in enumerate(frame.groupby("bin", observed=True, sort=True)):
            y = group[target].to_numpy(dtype=float, copy=True)
            pred = group[f"corrected_{target}"].to_numpy(dtype=float, copy=True)
            y_std = float(np.std(y))
            err = rmse(y, pred)
            rows.append(
                {
                    "target": target,
                    "condition": condition,
                    "bin_index": int(bin_index),
                    "bin_label": str(interval),
                    "condition_median": float(np.median(group[condition])),
                    "n": int(len(group)),
                    "label_std": y_std,
                    "corrected_rmse": err,
                    "corrected_rmse_over_std": float(err / y_std) if y_std > 0 else np.nan,
                    "corrected_r2": r2_score(y, pred),
                }
            )
    return pd.DataFrame(rows)


def mx_roll_subset_metrics(test: pd.DataFrame) -> pd.DataFrame:
    target = "mx_b"
    specs = [("all", np.ones(len(test), dtype=bool))]
    for col, label in [
        ("p_dot_smooth", "abs_p_dot_smooth"),
        ("p", "abs_roll_rate_p"),
        ("roll_rad", "abs_roll_angle"),
        ("elevon_diff", "abs_elevon_diff"),
    ]:
        values = np.abs(test[col].to_numpy(dtype=float, copy=True))
        for q in [0.75, 0.90]:
            threshold = float(np.nanquantile(values, q))
            specs.append((f"{label}_gt_p{int(q*100)}", values >= threshold))

    rows = []
    for name, mask in specs:
        sub = test.loc[mask, [target, f"corrected_{target}", "p_dot_smooth", "p", "elevon_diff", "roll_rad"]].replace([np.inf, -np.inf], np.nan).dropna()
        if sub.empty:
            continue
        y = sub[target].to_numpy(dtype=float, copy=True)
        pred = sub[f"corrected_{target}"].to_numpy(dtype=float, copy=True)
        std = float(np.std(y))
        e = rmse(y, pred)
        rows.append(
            {
                "subset": name,
                "n": int(len(sub)),
                "fraction": float(len(sub) / len(test)),
                "mx_std": std,
                "mx_rmse": e,
                "mx_rmse_over_std": float(e / std) if std > 0 else np.nan,
                "mx_r2": r2_score(y, pred),
                "median_abs_p_dot_smooth": float(np.median(np.abs(sub["p_dot_smooth"]))),
                "median_abs_p": float(np.median(np.abs(sub["p"]))),
                "median_abs_elevon_diff": float(np.median(np.abs(sub["elevon_diff"]))),
            }
        )
    return pd.DataFrame(rows)


def make_condition_bin_figure(bin_df: pd.DataFrame) -> None:
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
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.35), sharex=False)
    for ax, target in zip(axes.ravel(), TARGETS):
        rows = bin_df[bin_df["target"].eq(target)].sort_values("bin_index")
        x = np.arange(len(rows))
        ax.bar(x, rows["label_std"], color=OKABE_ITO["blue"], alpha=0.72, label="Label std")
        ax2 = ax.twinx()
        ax2.plot(x, rows["corrected_rmse_over_std"], color=OKABE_ITO["vermillion"], marker="o", linewidth=1.2, label="RMSE/std")
        ax.set_title(f"{TARGET_LABELS[target]} vs {CONDITION_BY_TARGET[target][1]}")
        ax.set_xticks(x)
        ax.set_xticklabels([f"{v:.2g}" for v in rows["condition_median"]], rotation=30, ha="right")
        ax.set_ylabel("Label std")
        ax2.set_ylabel("RMSE/std")
        ax.grid(True, axis="y", color="#D0D0D0", linewidth=0.4, alpha=0.7)
        ax.spines["top"].set_visible(False)
        ax2.spines["top"].set_visible(False)
        for xi, n in zip(x, rows["n"]):
            ax.text(xi, 0.02, f"n={int(n/1000)}k", transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=6.4, color="#444444")
    handles = [
        plt.Line2D([0], [0], color=OKABE_ITO["blue"], linewidth=6, alpha=0.72),
        plt.Line2D([0], [0], color=OKABE_ITO["vermillion"], marker="o", linewidth=1.2),
    ]
    fig.legend(handles, ["Label std", "Corrected RMSE/std"], loc="upper center", ncol=2, frameon=False)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.94), pad=0.5, w_pad=1.1, h_pad=1.0)
    FIG_ROOT.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_ROOT / "condition_bin_excitation_snr.pdf", bbox_inches="tight")
    fig.savefig(FIG_ROOT / "condition_bin_excitation_snr.png", dpi=400, bbox_inches="tight")
    plt.close(fig)


def make_channel_summary_figure(summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(6.0, 3.0))
    x = np.arange(len(summary))
    ax.bar(x - 0.18, summary["std"], width=0.36, color=OKABE_ITO["blue"], alpha=0.75, label="Label std")
    ax2 = ax.twinx()
    ax2.bar(x + 0.18, summary["corrected_rmse_over_std"], width=0.36, color=OKABE_ITO["orange"], alpha=0.75, label="RMSE/std")
    ax.set_xticks(x)
    ax.set_xticklabels([TARGET_LABELS[t] for t in summary["target"]])
    ax.set_ylabel("Label std")
    ax2.set_ylabel("Corrected RMSE/std")
    ax.grid(True, axis="y", color="#D0D0D0", linewidth=0.4, alpha=0.7)
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    handles = [
        plt.Line2D([0], [0], color=OKABE_ITO["blue"], linewidth=6, alpha=0.75),
        plt.Line2D([0], [0], color=OKABE_ITO["orange"], linewidth=6, alpha=0.75),
    ]
    ax.legend(handles, ["Label std", "Corrected RMSE/std"], frameon=False, loc="upper left")
    fig.tight_layout(pad=0.35)
    FIG_ROOT.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG_ROOT / "channel_excitation_summary.pdf", bbox_inches="tight")
    fig.savefig(FIG_ROOT / "channel_excitation_summary.png", dpi=400, bbox_inches="tight")
    plt.close(fig)


def write_summary(
    channel_summary: pd.DataFrame,
    ridge_df: pd.DataFrame,
    mx_df: pd.DataFrame,
    freq_df: pd.DataFrame,
    top_corr: pd.DataFrame,
) -> None:
    strong = channel_summary[channel_summary["target"].isin(["fx_b", "fz_b", "my_b"])]
    weak = channel_summary[channel_summary["target"].isin(["fy_b", "mx_b", "mz_b"])]
    deployable_ridge = ridge_df[~ridge_df["feature_group"].eq("angular_derivatives_label_diagnostic")].copy()
    deployable_best = deployable_ridge.sort_values(["target", "test_r2"], ascending=[True, False]).groupby("target").head(1)
    derivative_rows = ridge_df[ridge_df["feature_group"].eq("angular_derivatives_label_diagnostic")].copy()
    lines = [
        "# Channel Excitation and SNR Diagnostics",
        "",
        "This diagnostic is a draft analysis for explaining why the strongest measured-massprops results occur in `fx_b`, `fz_b`, and `my_b`, while `fy_b`, `mx_b`, and `mz_b` remain weaker.",
        "",
        "## Main Observations",
        "",
        f"- Stronger channels (`fx_b`, `fz_b`, `my_b`) have mean corrected RMSE/std `{strong['corrected_rmse_over_std'].mean():.3f}`.",
        f"- Weaker channels (`fy_b`, `mx_b`, `mz_b`) have mean corrected RMSE/std `{weak['corrected_rmse_over_std'].mean():.3f}`.",
        "- `fx_b` and `fz_b` have large target variance, high deployable-feature linear R2, and strong wingbeat-frequency residual structure, supporting the phase/condition correction story.",
        "- `my_b` has the best moment-channel prediction and strong structured frequency content, making it a reasonable supporting effective-moment result.",
        "- `fy_b`, `mx_b`, and `mz_b` have higher normalized errors and weaker or more broadband residual structure; they should be framed as limitations rather than hidden failures.",
        "- `mx_b` does not become clearly strong in high-roll-rate or high-elevon-difference subsets, so the current evidence points beyond simple low excitation toward derivative/reference/timing sensitivity.",
        "- Feature-group ridge rows named `angular_derivatives_label_diagnostic` are diagnostic only because angular acceleration is part of moment-label construction and is not a deployable correction input.",
        "",
        "## Best Deployable Ridge Feature Groups by Channel",
        "",
    ]
    for target in TARGETS:
        rows = deployable_best[deployable_best["target"].eq(target)]
        best = rows.iloc[0]
        lines.append(f"- `{target}`: best linear feature group `{best['feature_group']}` with test R2 `{best['test_r2']:.3f}`.")
    lines.extend(["", "## Angular-Derivative Diagnostic Rows", ""])
    for row in derivative_rows.itertuples():
        lines.append(f"- `{row.target}`: derivative-diagnostic R2 `{row.test_r2:.3f}`. This is label-chain information, not a deployable model input.")
    lines.extend(["", "## Top Pearson Correlations", ""])
    for target in TARGETS:
        rows = top_corr[top_corr["target"].eq(target)].head(5)
        txt = ", ".join(f"{r.feature} ({r.pearson_r:+.2f})" for r in rows.itertuples())
        lines.append(f"- `{target}`: {txt}")
    lines.extend(["", "## mx Roll-Specific Subsets", ""])
    for row in mx_df.itertuples():
        lines.append(
            f"- `{row.subset}`: n={row.n}, std={row.mx_std:.3f}, RMSE={row.mx_rmse:.3f}, "
            f"RMSE/std={row.mx_rmse_over_std:.3f}, R2={row.mx_r2:.3f}."
        )
    lines.extend(["", "## Frequency Structure Anchor", ""])
    for row in freq_df[freq_df["target"].isin(TARGETS)].itertuples():
        lines.append(
            f"- `{row.target}`: dominant component `{row.dominant_component}`, "
            f"true energy fraction `{row.dominant_true_energy_fraction:.3f}`, "
            f"remaining fraction of true `{row.dominant_remaining_energy_fraction_of_true:.3f}`."
        )
    lines.extend(
        [
            "",
            "## Paper-Safe Interpretation",
            "",
            "The channels with the strongest prediction performance are also the channels with sustained excitation and repeatable phase/condition/frequency structure. The weaker channels should be described as directions where the retained logs provide less informative excitation or where the labels are more sensitive to wind, sideslip, reference-point assumptions, and gyro differentiation.",
            "",
        ]
    )
    (OUT_ROOT / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    FIG_ROOT.mkdir(parents=True, exist_ok=True)

    train = load_split("train").frame
    test = load_split("test").frame
    test = _merge_predictions(test, "test")

    channel_summary = channel_excitation_summary(test)
    ridge_df = feature_group_ridge(train, test)
    corr_df = top_correlations(test)
    bin_df = condition_bin_excitation(test)
    mx_df = mx_roll_subset_metrics(test)
    freq_df = pd.read_csv(FREQUENCY_SUMMARY)
    freq_selected = freq_df[freq_df["target"].isin(TARGETS)].copy()

    channel_summary.to_csv(OUT_ROOT / "channel_excitation_summary.csv", index=False)
    ridge_df.to_csv(OUT_ROOT / "feature_group_ridge_r2.csv", index=False)
    ridge_df[~ridge_df["feature_group"].eq("angular_derivatives_label_diagnostic")].sort_values(
        ["target", "test_r2"], ascending=[True, False]
    ).groupby("target").head(1).to_csv(OUT_ROOT / "feature_group_ridge_best_deployable.csv", index=False)
    corr_df.to_csv(OUT_ROOT / "top_feature_correlations.csv", index=False)
    bin_df.to_csv(OUT_ROOT / "condition_bin_excitation.csv", index=False)
    mx_df.to_csv(OUT_ROOT / "mx_roll_subset_metrics.csv", index=False)
    freq_selected.to_csv(OUT_ROOT / "frequency_structure_summary.csv", index=False)
    with (OUT_ROOT / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "split_root": str(SPLIT_ROOT),
                "aligned_root": str(ALIGNED_ROOT),
                "per_channel_metrics": str(PER_CHANNEL_METRICS),
                "frequency_summary": str(FREQUENCY_SUMMARY),
                "targets": TARGETS,
            },
            handle,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")

    make_channel_summary_figure(channel_summary)
    make_condition_bin_figure(bin_df)
    write_summary(channel_summary, ridge_df, mx_df, freq_selected, corr_df)
    print(OUT_ROOT)
    print(channel_summary[["target", "std", "p95_minus_p5", "corrected_rmse", "corrected_rmse_over_std", "corrected_r2"]].to_string(index=False))
    print("\nBest deployable feature groups:")
    deployable_best = ridge_df[~ridge_df["feature_group"].eq("angular_derivatives_label_diagnostic")]
    print(deployable_best.sort_values(["target", "test_r2"], ascending=[True, False]).groupby("target").head(1).to_string(index=False))
    print("\nmx subsets:")
    print(mx_df.to_string(index=False))


if __name__ == "__main__":
    main()
