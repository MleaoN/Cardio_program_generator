import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from cardio_app.reports.pdf_report import PDFReportBuilder
from cardio_app.reports.pdf_utils_common import ask_save_filepath

class ResultFrame(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.grid(row=0, column=0, sticky="nsew")

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Generated Cardio Program", font=("Arial", 14)).pack(pady=10)

        # ScrolledText widget to display program summary
        self.text_area = scrolledtext.ScrolledText(self, width=60, height=20, state='disabled')
        self.text_area.pack(padx=10, pady=10)

        # Buttons Frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Save PDF Report", command=self.save_pdf).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="New Program", command=self.new_program).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Exit", command=self.controller.quit).pack(side="left", padx=10)



    def display_program(self, all_programs, metrics, client_name, unit, ramp_df):
        # Enable editing
        self.text_area.config(state='normal')
        self.text_area.delete('1.0', tk.END)

        for training_type, program in all_programs.items():
            self.text_area.insert(tk.END, f"--- {training_type.title()} Program ---\n")
            for phase, duration, start_time, speed in program:
                mins = duration // 60
                secs = duration % 60
                self.text_area.insert(tk.END,
                                      f"{phase}: {mins}m {secs}s, Speed: {speed} {unit}\n")
            self.text_area.insert(tk.END, "\n")

        # Disable editing
        self.text_area.config(state='disabled')

        # Store program info for PDF generation
        self.all_programs = all_programs

    def on_show(self):
        # Called when frame is raised
        self.display_program(
            all_programs=self.controller.shared_data.get("all_programs", {}),
            metrics=self.controller.shared_data.get("metrics", {}),
            client_name=self.controller.shared_data.get("client_name", ""),
            unit=self.controller.shared_data.get("unit", ""),
            ramp_df=self.controller.shared_data.get("ramp_df", None)
        )
    def save_pdf(self):
        pdf_builder = PDFReportBuilder(
            metrics=self.controller.shared_data.get("metrics"),
            programs=self.controller.shared_data.get("all_programs"),
            username=self.controller.shared_data.get("client_name"),
            unit=self.controller.shared_data.get("unit"),
            ramp_df=self.controller.shared_data.get("ramp_df")
        )
        pdf_builder.build_pdf()
        filename = ask_save_filepath(default_name=f"{self.controller.shared_data.get('client_name', 'cardio')}_cardio_report.pdf")
        if filename:
            pdf_builder.save_pdf(filename)
            messagebox.showinfo("Success", f"PDF saved successfully:\n{filename}", parent=self)
            self.controller.quit()


        else:
            messagebox.showinfo("Cancelled", "Save cancelled. Report not saved.", parent=self)

    def new_program(self):
        # Simply return to TrainingTypeFrame to allow generating additional programs
        self.controller.show_frame("TrainingTypeFrame")
    