import tkinter as tk
from tkinter import ttk, messagebox

class NameInputFrame(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.name_var = tk.StringVar()

        self.grid(row=0, column=0, sticky="nsew")
        self.create_widgets()

    def create_widgets(self):
        label = ttk.Label(self, text="Enter Client Name:", font=("Arial", 14))
        label.pack(pady=(60, 10))

        entry = ttk.Entry(self, textvariable=self.name_var, width=30)
        entry.pack(pady=(0, 20))
        entry.focus()

        continue_btn = ttk.Button(self, text="Continue", command=self.go_next)
        continue_btn.pack()

    def go_next(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Input Required", "Please enter the client's name.")
            return
        self.controller.shared_data["client_name"] = name  
        self.controller.show_frame("RampTestFrame")
