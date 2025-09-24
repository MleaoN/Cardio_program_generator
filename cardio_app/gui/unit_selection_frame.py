import tkinter as tk
from tkinter import ttk

class UnitSelectionFrame(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.selected_unit = tk.StringVar(value="mph")

        self.grid(row=0, column=0, sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        label = ttk.Label(self, text="Select Speed Unit:", font=("Arial", 14))
        label.pack(pady=(50, 10))

        units = [("Miles per hour (mph)", "mph"), ("Kilometers per hour (km/h)", "km/h")]
        for text, value in units:
            ttk.Radiobutton(self, text=text, variable=self.selected_unit, value=value).pack(anchor='w', padx=60)

        continue_btn = ttk.Button(self, text="Continue", command=self.go_next)
        continue_btn.pack(pady=30)

    def go_next(self):
        
        unit = self.selected_unit.get()
        self.controller.shared_data["unit"] = unit  # ✅ Save into shared_data
        self.controller.show_frame("NameInputFrame")

