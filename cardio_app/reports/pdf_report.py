import tempfile
import os
from fpdf import FPDF
from cardio_app.reports.pdf_tables import create_metrics_table_image, create_program_table_image
from cardio_app.reports.pdf_visuals import create_program_speed_plot, create_ramp_test_plot

class PDFReportBuilder:
    def __init__(self, metrics, programs, username, unit='mph', ramp_df=None, filename=None):
        self.unit = unit
        self.metrics = metrics
        self.programs = programs
        self.username = username or "Client"
        self.ramp_df = ramp_df
        safe_name = (username or "client").replace(" ", "_")
        self.filename = filename or f"{safe_name}_cardio_report.pdf"
        self.pdf = FPDF()
        self.temp_files = []

    def build_pdf(self):
        self.pdf.add_page()
        self._add_cover_page()

        # Each program page
        for program_name, program_data in self.programs.items():
            self.pdf.add_page()
            self._add_section_title(f"{program_name} Program")

            # Program table
            table_img = create_program_table_image(program_data, unit=self.unit)
            if table_img:
                path = self._save_temp_image(table_img)
                self.pdf.image(path, x=10, w=190)

            # Program speed plot
            plot_img = create_program_speed_plot(program_data, unit=self.unit)
            if plot_img:
                path = self._save_temp_image(plot_img)
                self.pdf.image(path, x=10, w=190)

        return self.pdf

    def save_pdf(self, path=None):
        output_path = path or self.filename
        self.pdf.output(output_path)
        # Clean up temp images
        for f in self.temp_files:
            try: os.remove(f)
            except: pass
        return output_path

    def _save_temp_image(self, img_bytesio):
        """Save BytesIO image to a temporary PNG file and return the path"""
        if isinstance(img_bytesio, str):
            # Already a path, just return it
            return img_bytesio
        elif img_bytesio is None:
            return None
        # Else, it's BytesIO
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_file.write(img_bytesio.getbuffer())
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name


    def _add_cover_page(self):
        self.pdf.set_font("Arial", 'B', 16)
        title = f"{self.username}'s Cardiovascular Fitness Report"
        self.pdf.cell(0, 10, title, ln=True, align="C")
        self.pdf.ln(10)

        # Metrics table
        metrics_img = create_metrics_table_image(self.metrics)
        if metrics_img:
            path = self._save_temp_image(metrics_img)
            self.pdf.image(path, x=30, w=150)
            self.pdf.ln(5)

        # Ramp test plot
        if self.ramp_df is not None:
            ramp_plot_img = create_ramp_test_plot(self.ramp_df, self.metrics, unit=self.unit)
            if ramp_plot_img:
                path = self._save_temp_image(ramp_plot_img)
                self.pdf.image(path, x=10, w=190)

    def _add_section_title(self, text):
        self.pdf.set_font("Arial", 'B', 16)
        self.pdf.cell(0, 10, text, ln=True, align="C")
        self.pdf.ln(5)
