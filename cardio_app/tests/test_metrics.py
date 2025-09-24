# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 09:32:11 2025

@author: leaon
"""

import pandas as pd
from logic.metrics import calculate_metrics

def test_calculate_metrics_without_wingate():
    ramp_data = pd.DataFrame({
        'speed': [3, 6, 9, 12]
    })
    metrics = calculate_metrics(ramp_data, None, 'mph')
    assert metrics["VO2max Speed (mph)"] == 12
    assert metrics["Aerobic Threshold (mph)"] == 7.2
    assert metrics["Anaerobic Threshold (mph)"] == 9.6

def test_calculate_metrics_with_wingate():
    ramp_data = pd.DataFrame({
        'speed': [3, 6, 9, 12]
    })
    wingate_data = pd.DataFrame({
        'peak_speed': [10, 11, 12]
    })
    metrics = calculate_metrics(ramp_data, wingate_data, 'mph')
    assert "Wingate Peak Speed (mph)" in metrics
    assert metrics["Wingate Peak Speed (mph)"] == 12
