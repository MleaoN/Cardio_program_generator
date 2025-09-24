# -*- coding: utf-8 -*-
"""
Calculations for cardio metrics
"""

import pandas as pd

def calculate_metrics(ramp_df, wingate_df, unit):
    metrics = {}

    if ramp_df is not None and not ramp_df.empty:
        speed_col = f"Speed ({unit})" if f"Speed ({unit})" in ramp_df.columns else "Speed"

        # Calculate thresholds using your logic:
        aerobic_threshold = ramp_df[(ramp_df["RPE"] > 2) & (ramp_df["RPE"] < 6)][speed_col].mean()
        anaerobic_threshold = ramp_df[(ramp_df["RPE"] > 6) & (ramp_df["RPE"] < 9)][speed_col].mean()

        vo2max_speed = (
            ramp_df[ramp_df["RPE"] == 10][speed_col].values[0]
            if not ramp_df[ramp_df["RPE"] == 10].empty
            else ramp_df[speed_col].max()
        )

        metrics[f"Aerobic Threshold ({unit})"] = round(aerobic_threshold, 2) if not pd.isna(aerobic_threshold) else None
        metrics[f"Anaerobic Threshold ({unit})"] = round(anaerobic_threshold, 2) if not pd.isna(anaerobic_threshold) else None
        metrics[f"VO2max Speed ({unit})"] = round(vo2max_speed, 2)

        metrics[f"Ramp Avg Speed ({unit})"] = ramp_df[speed_col].mean()

    if wingate_df is not None and not wingate_df.empty:
        wing_col = f"Speed ({unit})" if f"Speed ({unit})" in wingate_df.columns else "Speed"
        peak_speed = wingate_df[wing_col].max()
        avg_speed = wingate_df[wing_col].mean()
        fatigue_index = (wingate_df[wing_col].iloc[-1] / peak_speed) * 100

        metrics.update({
            f"Wingate Peak Speed ({unit})": round(peak_speed, 2),
            f"Wingate Average Speed ({unit})": round(avg_speed, 2),
            "Fatigue Index (%)": round(fatigue_index, 2)
        })

    return metrics
