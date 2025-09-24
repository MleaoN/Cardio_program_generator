# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 10:21:15 2025

@author: leaon
"""


import pandas as pd

def collect_ramp_test(unit='mph', rpe_inputs=None):
    """
    Collect ramp test data.

    Parameters:
    - unit: 'mph' or 'kmh'
    - rpe_inputs: Optional iterable/list of RPE values matching speed steps,
                  if None, must be provided by frontend.

    Returns:
    - pd.DataFrame with columns ['Speed', 'RPE']
    - unit string
    """
    # Normalize unit for internal use
    unit = unit.lower()
    if unit in ['km/h', 'kmh']:
        unit = 'kmh'
        speed = 4.0
        increment = 1.0
    else:
        unit = 'mph'
        speed = 2.0
        increment = 0.5

    ramp_data = []

    if rpe_inputs is not None:
        # Use provided RPE input list
        for rpe in rpe_inputs:
            if not (0 <= rpe <= 10):
                raise ValueError("RPE must be between 0 and 10.")
            ramp_data.append((speed, rpe))
            if rpe == 10:
                break
            speed += increment
    else:
        raise NotImplementedError("Interactive input is not supported in the logic layer. Provide rpe_inputs.")

    return pd.DataFrame(ramp_data, columns=["Speed", "RPE"]), unit


def collect_wingate_test(unit='mph', speed_inputs=None):
    """
    Collect Wingate test speed data.

    Parameters:
    - unit: 'mph' or 'kmh'
    - speed_inputs: List of 6 speed values (1 per 5-second interval)

    Returns:
    - pd.DataFrame with columns ['Time (s)', f'Speed ({unit})']
    """
    unit = unit.lower()
    if unit in ['km/h', 'kmh']:
        unit = 'kmh'
    else:
        unit = 'mph'

    if speed_inputs is None or len(speed_inputs) != 6:
        raise ValueError("speed_inputs must be a list with exactly 6 speed values.")

    time_points = [i * 5 for i in range(6)]
    speed_col = f"Speed ({unit})"

    return pd.DataFrame({
        "Time (s)": time_points,
        speed_col: speed_inputs
    })
