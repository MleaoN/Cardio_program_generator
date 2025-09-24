# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 12:16:28 2025
@author: leaon
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend
import matplotlib.pyplot as plt
import tempfile
import os
from cardio_app.reports.pdf_utils_common import format_seconds

def _save_plot_to_file(fig):
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp_file.name, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    tmp_file.close()
    return tmp_file.name

def create_metrics_table_image(metrics: dict):
    df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
    df["Value"] = df["Value"].round(1)

    fig, ax = plt.subplots(figsize=(5.5, 2.3))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.2)

    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')
            cell.set_facecolor("#D3D3D3")

    return _save_plot_to_file(fig)

def create_program_table_image(program_data, unit="mph"):
    if all(len(row) == 2 for row in program_data):
        df = pd.DataFrame(program_data[1:], columns=program_data[0])
    else:
        df = pd.DataFrame(program_data, columns=["Activity", "Duration (sec)", "Start Time (sec)", f"Speed ({unit})"])
        df[f"Speed ({unit})"] = df[f"Speed ({unit})"].round(1)
        df["Start Time (sec)"] = df["Start Time (sec)"].apply(format_seconds)

    fig, ax = plt.subplots(figsize=(7, max(2, len(df) * 0.28)))
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.1)

    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_text_props(weight='bold')
            cell.set_facecolor("#ADD8E6")

    return _save_plot_to_file(fig)
