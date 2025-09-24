import tkinter as tk
from tkinter import ttk, messagebox

class TrainingTypeFrame(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.grid(row=0, column=0, sticky="nsew")

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Select Training Type", font=("Arial", 14)).pack(pady=10)

        # Program descriptions
        self.training_descriptions = {
            1: "Explosive Power: A series of sprints in a speed ramp progression and regression. "
               "Adapted by session time. Duration: ~5–10 minutes.",
            2: "Power Endurance: Fixed three step blocks (walk, feed, spring) to improve fatigue resistance. "
               "Duration: ~10–20 minutes.",
            3: "Endurance: Steady moderate effort to build aerobic base. Duration: ~20–60 minutes.",
        }

        # Training type selection
        self.training_var = tk.IntVar(value=3)  # Default to Endurance

        training_options = [
            (1, "Explosive"),
            (2, "Power Endurance"),
            (3, "Endurance"),
        ]

        for val, text in training_options:
            ttk.Radiobutton(
                self, text=text, variable=self.training_var, value=val,
                command=self.update_description
            ).pack(anchor="w", padx=20)

        # Description label
        self.description_label = ttk.Label(
            self, wraplength=400, justify="left",
            text=self.training_descriptions[self.training_var.get()]
        )
        self.description_label.pack(pady=(10, 15), padx=10)

        # Session time input
        ttk.Label(self, text="Session time (minutes, ≥ 5):").pack(pady=(5, 5))
        self.session_time_var = tk.StringVar(value="30")
        self.session_time_entry = ttk.Entry(self, textvariable=self.session_time_var, width=10)
        self.session_time_entry.pack()

        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Next", command=self.on_next).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Back", command=self.on_back).pack(side="left", padx=10)

    def update_description(self):
        selected = self.training_var.get()
        self.description_label.config(text=self.training_descriptions[selected])

    def on_next(self):
        try:
            session_time = int(self.session_time_var.get())
            if session_time < 5:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid session time (minimum 5 minutes).")
            return

        training_map = {1: "explosive", 2: "power_endurance", 3: "endurance"}
        training_type = training_map.get(self.training_var.get(), "endurance")

        # Build program using controller method
        self.controller.build_program(training_type, session_time)

        # Navigate to result frame
        self.controller.show_frame("ResultFrame")

    def on_back(self):
        # Go back to Wingate Test frame or RampTest depending on your flow
        self.controller.show_frame("WingateInputFrame")  

