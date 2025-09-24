# cardio_app/webapp/routes.py
from flask import Blueprint, render_template, request, send_file, session, redirect, url_for
import os
import pandas as pd

from cardio_app.logic.data_collection import collect_wingate_test
from cardio_app.logic.metrics import calculate_metrics
from cardio_app.logic.program_builder import CardioProgramBuilder
from cardio_app.reports.pdf_utils_common import safe_filename
from cardio_app.reports.pdf_report import PDFReportBuilder

bp = Blueprint("routes", __name__)
bp.secret_key = "supersecret"  # needed for sessions


def _parse_ramp_rpe_inputs(rpe_inputs):
    """Convert list of "speed:RPE" strings into DataFrame"""
    data = []
    for item in rpe_inputs:
        try:
            speed_str, rpe_str = item.split(":")
            speed = float(speed_str)
            rpe = float(rpe_str)
            data.append({"Speed": speed, "RPE": rpe})
        except Exception:
            continue
    if not data:
        return None
    return pd.DataFrame(data)


@bp.route("/")
def index():
    """First page → Name, unit, Ramp Test, Wingate"""
    return render_template("index.html")


@bp.route("/next", methods=["POST"])
def next_page():
    """Store first page data in session and go to second page"""
    client_name = request.form.get("client_name", "").strip()
    unit = request.form.get("unit", "mph").lower()

    # Ramp test
    ramp_rpe_inputs = request.form.getlist("ramp_rpe_inputs")
    ramp_df = _parse_ramp_rpe_inputs(ramp_rpe_inputs)
    if ramp_df is None or ramp_df.empty:
        return render_template("error.html", message="No ramp test RPE data provided."), 400

    # Wingate
    wingate_speeds_text = request.form.get("wingate_speeds", "")
    wingate_df = None
    if wingate_speeds_text:
        try:
            speeds = [float(v.strip()) for v in wingate_speeds_text.replace(";", ",").split(",") if v.strip()]
            wingate_df = collect_wingate_test(unit=unit, speed_inputs=speeds)
        except Exception:
            wingate_df = None

    # Save to session (store as JSON-safe lists/dicts)
    session["client_name"] = client_name
    session["unit"] = unit
    session["ramp_data"] = ramp_df.to_dict(orient="records")
    session["wingate_data"] = wingate_df.to_dict(orient="records") if wingate_df is not None else None
    session["trainings"] = []  # initialize training programs

    return render_template("programs.html")  # second page template


@bp.route("/add_training", methods=["POST"])
def add_training():
    try:
        training_type = request.form.get("training_type", "endurance").lower()
        duration = int(request.form.get("duration", 10))  # now in minutes

        # append to session
        trainings = session.get("trainings", [])
        trainings.append({"training_type": training_type, "duration": duration})
        session["trainings"] = trainings

        return render_template("programs.html", message="Training added successfully!", trainings=trainings)

    except Exception as e:
        return render_template("error.html", message=f"Error in /add_training: {e}"), 500


@bp.route("/generate", methods=["POST"])
def generate():
    """Generate final PDF report using stored session data"""
    try:
        client_name = session.get("client_name", "client")
        unit = session.get("unit", "mph")
        ramp_df = pd.DataFrame(session.get("ramp_data", []))
        wingate_df = pd.DataFrame(session.get("wingate_data", [])) if session.get("wingate_data") else None
        trainings = session.get("trainings", [])

        if ramp_df.empty and not trainings:
            return render_template("error.html", message="No ramp test or training data available."), 400
        
        # ✅ Must have at least one program
        if not trainings:
            return render_template("error.html", message="You must add at least one training before generating the PDF."), 400

        # Compute metrics
        metrics = calculate_metrics(ramp_df, wingate_df, unit)

        ramp_speeds = ramp_df['Speed'] if ramp_df is not None else []
        max_speed = ramp_speeds.max() if len(ramp_speeds) > 0 else 12  # default fallback


        # Build training programs
        programs = {}
        for i, tr in enumerate(trainings, 1):
            from cardio_app.logic.program_builder import CardioProgramBuilder

            aerobic_thres = metrics.get(f"Aerobic Threshold ({unit})")

            builder = CardioProgramBuilder(
                total_time=tr["duration"],
                max_speed=max_speed,
                aerobic_thres=metrics.get(f"Aerobic Threshold ({unit})"),
                anaerobic_thres=metrics.get(f"Anaerobic Threshold ({unit})"),
                recovery_speed=aerobic_thres if aerobic_thres else 6.0,  # fallback if not available
                wingate_peak_speed=metrics.get(f"Wingate Peak Speed ({unit})"),
                unit=unit
            )

            program = builder.build_program(tr["training_type"])
            programs[tr["training_type"].capitalize()] = program
 

        # PDF output path
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        safe_name = safe_filename(client_name)
        output_path = os.path.join(output_dir, f"{safe_name}_cardio_report.pdf")

        # Build PDF
        from cardio_app.reports.pdf_report import PDFReportBuilder
        pdf_builder = PDFReportBuilder(
            metrics=metrics,
            programs=programs,
            username=client_name,
            unit=unit,
            ramp_df=ramp_df,
            filename=output_path
        )
        pdf_builder.build_pdf()
        pdf_builder.save_pdf()

        if not os.path.exists(output_path):
            return render_template("error.html", message="PDF was not created."), 500

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return render_template("error.html", message=f"Unhandled error in /generate: {e}"), 500


