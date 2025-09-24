# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 09:24:58 2025

@author: leaon
"""

"""
Input validation and CLI data collection fallback
"""

import pandas as pd

def collect_ramp_test(unit):
    # CLI fallback or dummy input for ramp test
    # Here you can replace with actual CLI input or file read
    print(f"Collecting Ramp Test data in {unit} mode.")
    # Dummy data example:
    data = {
        'time': [0, 60, 120, 180],
        'speed': [3, 6, 9, 12],
        'power': [50, 100, 150, 200]
    }
    df = pd.DataFrame(data)
    return df, unit


def collect_wingate_test(unit):
    # CLI fallback or dummy input for Wingate test
    print(f"Collecting Wingate Test data in {unit} mode.")
    # Dummy data example:
    data = {
        'time': [0, 30, 60],
        'peak_speed': [10, 11, 12]
    }
    df = pd.DataFrame(data)
    return df
