import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

class WingateInputFrame(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.unit = self.controller.shared_data["unit"]

        self.grid(row=0, column=0, sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Wingate Test Data Entry", font=("Arial", 14)).pack(pady=10)

        ttk.Label(
            self,
            text="Enter speed for each 5-second interval of the 30-second Wingate test.\n"
                 f"Total 6 entries required. Unit: {self.unit}",
            wraplength=400,
            justify="center"
        ).pack(pady=(0, 15))

        self.entries = []
        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=5)

        # Create labels and entry boxes for 0s, 5s, 10s, 15s, 20s, 25s
        for i in range(6):
            frame = ttk.Frame(entry_frame)
            frame.grid(row=0, column=i, padx=5)

            ttk.Label(frame, text=f"{i*5} s").pack()
            entry = ttk.Entry(frame, width=6, justify="center")
            entry.pack(pady=5)
            self.entries.append(entry)

        # Navigation buttons
        nav_frame = ttk.Frame(self)
        nav_frame.pack(pady=15)

        ttk.Button(nav_frame, text="Back", command=self.go_back).pack(side="left", padx=20)
        ttk.Button(nav_frame, text="Next", command=self.finish_input).pack(side="left", padx=20)

    def on_show(self):
        # Clear all entries when this frame is shown
        for entry in self.entries:
            entry.delete(0, tk.END)

    def go_back(self):
        self.controller.show_frame("RampTestFrame")

    def finish_input(self):
        speeds = []
        for i, entry in enumerate(self.entries):
            val = entry.get().strip()
            if not val:
                messagebox.showerror("Missing Data", f"Speed at {i*5} seconds is required.")
                return
            try:
                speed = float(val)
                if speed <= 0:
                    raise ValueError
                speeds.append(speed)
            except ValueError:
                messagebox.showerror("Invalid Input", f"Speed at {i*5} seconds must be a positive number.")
                return

        # Save speeds as DataFrame with times in shared_data
        data = {"Time": [i*5 for i in range(6)], "Speed": speeds}
        self.controller.shared_data["wingate_df"] = pd.DataFrame(data)

        # Recalculate metrics here
        self.controller.calculate_and_prepare()

        # Proceed to next frame
        self.controller.show_frame("TrainingTypeFrame")
