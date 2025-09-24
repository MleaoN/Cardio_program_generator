import tkinter as tk
from tkinter import messagebox
from cardio_app.gui.unit_selection_frame import UnitSelectionFrame
from cardio_app.gui.name_input_frame import NameInputFrame
from cardio_app.gui.ramp_test_frame import RampTestFrame
from cardio_app.gui.wingate_input_frame import WingateInputFrame
from cardio_app.gui.result_frame import ResultFrame
from cardio_app.gui.training_type_frame import TrainingTypeFrame
from cardio_app.gui.unit_selection_frame import UnitSelectionFrame
from cardio_app.reports.pdf_report import PDFReportBuilder
from cardio_app.reports.pdf_utils_common import ask_save_filepath
from cardio_app.logic.metrics import calculate_metrics
from cardio_app.logic.program_builder import CardioProgramBuilder

class CardioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # <--- Prevent window from showing too early
        self.title("Cardio Program Generator")
        self.geometry("600x600")
        self.resizable(False, False)

        # Shared data across frames
        self.shared_data = {
            "unit": None,
            "client_name": None,
            "ramp_df": None,
            "wingate_df": None,
            "metrics": None,
            "max_speed": None,
            "wing_peak": None,
            "all_programs": {}
        }

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialize all frames
        self.frames = {}
        for F in (UnitSelectionFrame, NameInputFrame, RampTestFrame, WingateInputFrame, TrainingTypeFrame, ResultFrame):
            frame_name = F.__name__
            frame = F(container, self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show welcome message first
        self.after(100, self.show_welcome_message)

    def show_welcome_message(self):
        intro_text = (
            "Welcome to the Cardio Program Generator!\n\n"
            "This tool creates a personalized cardio training plan based on two tests:\n"
            "1. Ramp Test\n2. Wingate Test (optional)\n\n"
            "Let's get started!"
        )
        messagebox.showinfo("Welcome", intro_text, parent=self)
        self.deiconify()  # <--- Show window AFTER popup closes
        self.show_frame("UnitSelectionFrame")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()

       
    
    def calculate_and_prepare(self):
        ramp_df = self.shared_data.get("ramp_df")
        wingate_df = self.shared_data.get("wingate_df")
        unit = self.shared_data.get("unit", "mph")

        metrics = calculate_metrics(ramp_df, wingate_df, unit)
        self.shared_data["metrics"] = metrics

        max_spd = metrics.get(f"VO2max Speed ({unit})", 10)
        self.shared_data["max_speed"] = max_spd

        if wingate_df is not None and not wingate_df.empty:
            wing_col = f"Speed ({unit})" if f"Speed ({unit})" in wingate_df.columns else "Speed"
            wing_peak = wingate_df[wing_col].max()
        
        else:
            wing_peak = max_spd * 1.4  # fallback if no wingate data

        self.shared_data["wing_peak"] = wing_peak

    def build_program(self, training_type, session_time):
        metrics = self.shared_data["metrics"]
        unit = self.shared_data["unit"]

        # Validate required metrics
        if f"Aerobic Threshold ({unit})" not in metrics or f"Anaerobic Threshold ({unit})" not in metrics:
            messagebox.showerror("Missing Thresholds", "Aerobic and anaerobic thresholds are required for endurance mode.")
            return

        peak_speed = self.shared_data["wing_peak"]
        max_speed = self.shared_data["max_speed"]

        builder = CardioProgramBuilder(
            total_time=session_time * 60,
            max_speed=max_speed,
            wingate_peak_speed=peak_speed,
            recovery_speed=metrics.get(f"Aerobic Threshold ({unit})", 5),
            aerobic_thres=metrics.get(f"Aerobic Threshold ({unit})"),
            anaerobic_thres=metrics.get(f"Anaerobic Threshold ({unit})"),
            unit=unit
        )

        program_df = builder.build_program(
            training_type=training_type,
            num_sprints=6,
            start_intensity=0.7,
            max_intensity=0.9,
            wingate_peak_speed=peak_speed
        )

        #  Merge with existing
        self.shared_data["all_programs"][training_type] = program_df

    def generate_pdf_report(self):
        # Build PDF from all collected programs and data
        pdf_builder = PDFReportBuilder(
            metrics=self.shared_data["metrics"],
            programs=self.shared_data["all_programs"],
            username=self.shared_data["client_name"],
            unit=self.shared_data["unit"],
            ramp_df=self.shared_data["ramp_df"]
        )
        pdf_builder.build_pdf()
        filename = ask_save_filepath(default_name=f"{self.shared_data['client_name'].replace(' ', '_')}_cardio_report.pdf")
        if filename:
            pdf_builder.save_pdf(filename)
            messagebox.showinfo("Success", f"PDF saved successfully:\n{filename}", parent=self)
        else:
            messagebox.showinfo("Cancelled", "Save cancelled. Report not saved.", parent=self)


def main():
    app = CardioApp()
    app.mainloop()

if __name__ == "__main__":
    main()
