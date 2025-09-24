# -*- coding: utf-8 -*-
"""
Program builder logic
"""

class CardioProgramBuilder:
    def __init__(self, total_time, max_speed, recovery_speed,
                 aerobic_thres=None, anaerobic_thres=None, wingate_peak_speed=None, unit='mph'):
        self.total_time = total_time * 60
        self.max_speed = max_speed
        self.recovery_speed = recovery_speed
        self.aerobic_thres = aerobic_thres
        self.anaerobic_thres = anaerobic_thres
        self.wingate_peak_speed = wingate_peak_speed
        self.unit = unit.lower()
        self.program = []
        self.time_marker = 0

        # Default walk speed based on unit
        self.walk_speed = 2.0 if self.unit == 'mph' else 4.0

    def request_training_type(self):
        print("Select training type:")
        print("1 - Explosive")
        print("2 - Power Endurance")
        print("3 - Endurance")
        while True:
            choice = input("Enter 1, 2 or 3: ").strip()
            if choice == "1":
                return "explosive"
            elif choice == "2":
                return "power_endurance"
            elif choice == "3":
                return "endurance"
            else:
                print("Invalid choice. Try again.")

    def build_program(self, training_type, num_sprints=6,
                      start_intensity=0.7, max_intensity=0.9,
                      wingate_peak_speed=None):
        self.add_warmup()
        if training_type == "explosive":
            if wingate_peak_speed is None:
                if self.max_speed is None:
                    raise ValueError("Cannot compute wingate peak speed: max_speed is not defined.")
                wingate_peak_speed= self.max_speed *1.4
            self.build_explosive(num_sprints, start_intensity, max_intensity, wingate_peak_speed)
        elif training_type == "power_endurance":
            self.build_power_endurance(num_sprints)
        elif training_type == "endurance":
            self.build_endurance_block()
        self.add_cooldown()
        return self.program

    def add_warmup(self):
        self.program.append(("W-UP Walk", 30, self.time_marker, self.walk_speed))
        self.time_marker += 30
        jog_speed = self._round_speed(self.recovery_speed * 0.8)
        self.program.append(("W-UP Jog", 30, self.time_marker, jog_speed))
        self.time_marker += 30

    def build_explosive(self, num_sprints, start_intensity, max_intensity, wingate_peak_speed):
        max_sprint_speed = 0.9 * wingate_peak_speed
        half = num_sprints // 2
        intensities = []

        for i in range(half):
            pct = start_intensity + ((max_intensity - start_intensity) * i / (half - 1))
            intensities.append(pct)
        if num_sprints % 2 != 0:
            intensities.append(max_intensity)
        intensities += list(reversed(intensities[:half]))

        total_work = len(intensities) * 20
        remaining_time = self.total_time - self.time_marker - total_work - 60
        recovery_time = self._round_to_5(remaining_time // len(intensities))

        for pct in intensities:
            sprint_speed = self._round_speed(max_sprint_speed * pct)
            self.program.append(("Sprint", 20, self._round_to_5(self.time_marker), sprint_speed))
            self.time_marker += 20
            self.program.append(("Recovery", recovery_time, self._round_to_5(self.time_marker),
                                 self._round_speed(self.recovery_speed)))
            self.time_marker += recovery_time

    def build_power_endurance(self, num_sprints=None):
        jog_speed = self._round_speed(self.max_speed * 0.60)
        sprint_speed = self._round_speed(self.max_speed * 0.85)
        jog_duration = self._round_to_5(60)
        sprint_duration = self._round_to_5(30)
        walk_duration = self._round_to_5(30)
        block_time = jog_duration + sprint_duration + walk_duration

        while self.time_marker + block_time + 60 <= self.total_time:
            self.program.append(("Jog", jog_duration, self._round_to_5(self.time_marker), jog_speed))
            self.time_marker += jog_duration

            self.program.append(("Sprint", sprint_duration, self._round_to_5(self.time_marker), sprint_speed))
            self.time_marker += sprint_duration

            self.program.append(("Recovery Walk", walk_duration, self._round_to_5(self.time_marker), self.walk_speed))
            self.time_marker += walk_duration

        time_left = self.total_time - self.time_marker - 60
        if 30 <= time_left < block_time:
            jog_partial_duration = self._round_to_5(time_left)
            self.program.append(("Jog (Partial)", jog_partial_duration, self._round_to_5(self.time_marker), jog_speed))
            self.time_marker += jog_partial_duration

    def build_endurance_block(self):
        if self.aerobic_thres is None or self.anaerobic_thres is None:
            raise ValueError("Aerobic and anaerobic thresholds are required for endurance mode.")

        low_speed = self._round_speed(self.recovery_speed)
        high_speed = self._round_speed((self.aerobic_thres + self.anaerobic_thres) / 2)

        block_parts = [
            ("EL", 300, low_speed),
            ("EH", 300, high_speed)
        ]

        block_total = sum(d for _, d, _ in block_parts)
        available = self.total_time - self.time_marker - 60
        full_blocks = available // block_total

        for _ in range(int(full_blocks)):
            for label, dur, speed in block_parts:
                self.program.append((label, dur, self.time_marker, speed))
                self.time_marker += dur

        # Add partial recovery block if remaining time allows
        remaining = self.total_time - self.time_marker - 60
        if remaining >= 60:
            label, _, speed = block_parts[0]  # Add partial EL
            self.program.append((label + " (Partial)", remaining, self.time_marker, speed))
            self.time_marker += remaining

        # Add cooldown if any remaining time

    def add_cooldown(self):
        
        # Add a cooldown jog phase if you want, similar to warm-up jog
        cooldown_jog_speed = self._round_speed(self.recovery_speed * 0.8)
        self.program.append(("Cool Jog", 30, self._round_to_5(self.time_marker), cooldown_jog_speed))
        self.time_marker += 30
        
        cooldown_walk_speed = self.walk_speed
        self.program.append(("Cool Walk", 30, self._round_to_5(self.time_marker), cooldown_walk_speed))
        self.time_marker += 30
    

    def _round_speed(self, speed):
        return round(speed, 1)

    def _round_to_5(self, seconds):
        return 5 * round(seconds / 5)
