import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

class RampTestFrame(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.unit = None
        self.speed_step = None
        self.initial_speed = None
        self.rpe_limit = 10
        self.speed_values = []
        self.rpe_values = []

        self.tree = None
        self.entry_rpe = None

        self.grid(row=0, column=0, sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        self.title_label = ttk.Label(self, text="Ramp Test - RPE Entry", font=("Arial", 14))
        self.title_label.pack(pady=(10, 5))

        self.instructions = ttk.Label(self, text="", wraplength=400, justify="left")
        self.instructions.pack(padx=10, pady=5)

        # === Scrollable Treeview for Speed/RPE table ===
        tree_container = ttk.Frame(self)
        tree_container.pack(padx=10, pady=5)

        self.tree = ttk.Treeview(tree_container, columns=("Speed", "RPE"), show="headings", height=10)
        self.tree.heading("Speed", text="Speed")
        self.tree.heading("RPE", text="RPE (0-10)")
        self.tree.column("Speed", width=150, anchor="center")
        self.tree.column("RPE", width=100, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # === RPE Entry and Buttons ===
        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=10)

        ttk.Label(entry_frame, text="Enter RPE:").pack(side="left", padx=(0, 5))
        self.entry_rpe = ttk.Entry(entry_frame, width=5)
        self.entry_rpe.pack(side="left")
        self.entry_rpe.bind("<Return>", lambda event: self.add_rpe())
        self.entry_rpe.focus()

        ttk.Button(entry_frame, text="Add RPE", command=self.add_rpe).pack(side="left", padx=5)
        ttk.Button(self, text="Finish", command=self.finish).pack(pady=(0, 10))

    def on_show(self):
        self.unit = self.controller.shared_data.get("unit", "kmh")  # Default fallback
        self.speed_step = 0.5 if self.unit == 'mph' else 1.0
        self.initial_speed = 2.0 if self.unit == 'mph' else 4.0

        self.speed_values = [self.initial_speed]
        self.rpe_values = []

        self.tree.delete(*self.tree.get_children())
        self.insert_row()
        self.entry_rpe.delete(0, tk.END)
        self.entry_rpe.focus()

        self.instructions.config(
            text=f"Enter RPE for each speed step.\nSpeed increases by {self.speed_step} {self.unit} every 30s.\nTest ends when RPE reaches 10."
        )
        self.title_label.config(text=f"Ramp Test - Unit: {self.unit}")

    def insert_row(self):
        speed = self.speed_values[-1]
        self.tree.insert('', 'end', values=(f"{speed:.1f}", ""))

    def add_rpe(self):
        rpe_text = self.entry_rpe.get().strip()
        if not rpe_text:
            messagebox.showwarning("Input Required", "Please enter an RPE value.")
            return
        try:
            rpe_val = float(rpe_text)
            if not (0 <= rpe_val <= 10):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "RPE must be a number between 0 and 10.")
            self.entry_rpe.delete(0, tk.END)
            self.entry_rpe.focus()
            return

        last_row = self.tree.get_children()[-1]
        speed = float(self.tree.item(last_row)['values'][0])
        self.tree.item(last_row, values=(f"{speed:.1f}", f"{rpe_val:.1f}"))

        self.rpe_values.append(rpe_val)

        if rpe_val >= self.rpe_limit:
            self.finish()
            return

        next_speed = speed + self.speed_step
        self.speed_values.append(next_speed)
        self.insert_row()

        self.entry_rpe.delete(0, tk.END)
        self.entry_rpe.focus()

    def finish(self):
        data = []
        for item in self.tree.get_children():
            speed, rpe = self.tree.item(item)['values']
            if rpe == '':
                continue
            data.append({'Speed': float(speed), 'RPE': float(rpe)})

        if not data:
            messagebox.showwarning("No Data", "No ramp test data was entered.")
            return

        self.result = pd.DataFrame(data)
        self.controller.shared_data["ramp_df"] = self.result

        self.controller.calculate_and_prepare()

        answer = messagebox.askyesno("Wingate Test", "Do you want to enter Wingate Test results?", parent=self)
        if answer:
            self.controller.show_frame("WingateInputFrame")
        else:
            self.controller.shared_data["wingate_df"] = None
            self.controller.calculate_and_prepare()
            self.controller.show_frame("TrainingTypeFrame")
