# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 09:31:34 2025

@author: leaon
"""

import pytest
from logic.program_builder import CardioProgramBuilder

def test_round_speed_and_to_5():
    builder = CardioProgramBuilder(600, 10, 5)
    assert builder._round_speed(5.678) == 5.7
    assert builder._round_to_5(13) == 15
    assert builder._round_to_5(12) == 10

def test_build_warmup_and_cooldown():
    builder = CardioProgramBuilder(600, 10, 5)
    builder.add_warmup()
    assert builder.program[0][0] == "Warm-up Walk"
    builder.add_cooldown()
    assert builder.program[-1][0] == "Cool Down Walk"

def test_build_explosive_program():
    builder = CardioProgramBuilder(total_time=600, max_speed=10, recovery_speed=5)
    wingate_peak = 12.0
    program = builder.build_program("explosive", num_sprints=4, start_intensity=0.7, max_intensity=0.9, wingate_peak_speed=wingate_peak)
    assert any("Sprint" in session[0] for session in program)
    assert any("Recovery" in session[0] for session in program)

def test_build_power_endurance_program():
    builder = CardioProgramBuilder(total_time=600, max_speed=10, recovery_speed=5)
    program = builder.build_program("power_endurance")
    assert any("Jog" in session[0] for session in program)
    assert any("Sprint" in session[0] for session in program)

def test_build_endurance_program():
    builder = CardioProgramBuilder(total_time=600, max_speed=10, recovery_speed=5,
                                  aerobic_thres=6, anaerobic_thres=8)
    program = builder.build_program("endurance")
    assert any("EL" in session[0] or "EH" in session[0] for session in program)
