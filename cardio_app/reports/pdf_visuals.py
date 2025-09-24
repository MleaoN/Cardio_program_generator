# -*- coding: utf-8 -*-
"""
PDF visuals: plots for programs and ramp test
"""

import matplotlib
matplotlib.use("Agg")  # Ensure no GUI backend is used
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO


def _save_plot_to_memory(fig):
    """Save Matplotlib figure to a BytesIO object for FPDF usage"""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def create_ramp_test_plot(ramp_df, metrics, unit='mph'):
    """Create a ramp test plot (speed vs RPE) with thresholds zones"""
    if ramp_df is None or ramp_df.empty:
        return None

    try:
        speeds = ramp_df['Speed'] if 'Speed' in ramp_df.columns else ramp_df.iloc[:, 0]
        rpe = ramp_df['RPE'] if 'RPE' in ramp_df.columns else ramp_df.iloc[:, 1]

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(speeds, rpe, marker='o', linestyle='-', color='green', label='Ramp Test Speed')
        ax.set_xlabel(f"Speed ({unit})")
        ax.set_ylabel("RPE - Borg(10)")
        ax.set_title("Ramp Test Speed Over Time")

        # Show all ticks
        ax.set_xticks(speeds)
        ax.set_yticks(sorted(set(rpe)))

        # Zones from metrics
        aerobic_thres = metrics.get(f"Aerobic Threshold ({unit})")
        anaerobic_thres = metrics.get(f"Anaerobic Threshold ({unit})")
        if aerobic_thres is not None and anaerobic_thres is not None:
            ax.axvspan(speeds.iloc[0], aerobic_thres, facecolor='lightgreen', alpha=0.3, label='Aerobic Zone')
            ax.axvspan(aerobic_thres, anaerobic_thres, facecolor='khaki', alpha=0.3, label='Moderate Zone')
            ax.axvspan(anaerobic_thres, speeds.iloc[-1], facecolor='lightcoral', alpha=0.3, label='Anaerobic Zone')

        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='upper left')

        return _save_plot_to_memory(fig)

    except Exception as e:
        print(f"Error creating ramp test plot: {e}")
        return None


def create_program_speed_plot(program_data, unit="mph"):
    """
    Create a speed-over-time plot for a training program.
    program_data: list of tuples (label, duration_sec, start_time, speed)
    """
    if not all(len(row) == 4 for row in program_data):
        return None

    def format_seconds(sec):
        m, s = divmod(int(sec), 60)
        return f"{m}:{s:02d}"

    try:
        # Compute scaled times for visualization
        total_duration = sum(float(duration) for _, duration, _, _ in program_data)
        warmup_scale = cooldown_scale = 1.0 if total_duration < 10*60 else (2.0 if total_duration < 20*60 else 5.0)
        work_scale = 1.0

        scaled_times, speeds, scaled_blocks = [0], [], []
        visual_time = 0

        for label, duration, _, speed in program_data:
            duration = float(duration)
            scale = warmup_scale if "W-UP" in label else cooldown_scale if "Cool" in label else work_scale
            vis_duration = duration * scale
            scaled_blocks.append((label, vis_duration, visual_time, speed))
            visual_time += vis_duration
            scaled_times.append(visual_time)
            speeds.append(speed)

        fig, ax = plt.subplots(figsize=(9, 3))
        speeds_extended = speeds + [speeds[-1]]
        ax.step(scaled_times, speeds_extended, where='post', color='blue', linewidth=2)

        # Add colored blocks and speed labels
        for label, vis_duration, vis_start, speed in scaled_blocks:
            mid = vis_start + vis_duration / 2
            ax.text(mid, speed + 0.3, f"{speed:.1f} {unit}", ha='center', fontsize=7)
            color = 'lightblue' if "W-UP" in label else 'lightpink' if "Cool" in label else None
            if color:
                rect = patches.Rectangle((vis_start, 0), vis_duration, max(speeds) + 2, facecolor=color, alpha=0.3)
                ax.add_patch(rect)

        ax.set_xlabel("Time (visually scaled)")
        ax.set_ylabel(f"Speed ({unit})")
        ax.set_title("Program Speed Over Time")
        ax.set_ylim(0, max(speeds) + 2)
        ax.grid(True, linestyle='--', alpha=0.5)

        # X-axis real times
        real_times = [sum(float(row[1]) for row in program_data[:i]) for i in range(len(program_data) + 1)]
        ax.set_xticks(scaled_times)
        ax.set_xticklabels([format_seconds(t) for t in real_times], rotation=45)

        return _save_plot_to_memory(fig)

    except Exception as e:
        print(f"Error creating program speed plot: {e}")
        return None
