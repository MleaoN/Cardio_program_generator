# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 12:18:44 2025

@author: leaon
"""
"""
Common utilities for PDF report generation
"""

import re

if os.environ.get("USE_TK", "0") == "1":
    import tkinter as tk
    from tkinter import filedialog


def format_seconds(seconds: float) -> str:
    """
    Convert seconds to a MM:SS string format.
    """
    try:
        seconds = float(seconds)
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    except (ValueError, TypeError):
        return "N/A"


def safe_filename(name: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.
    """
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)


def ask_save_filepath(default_name="cardio_report.pdf") -> str:
    """
    Open a file dialog to ask the user for a save path for the PDF.
    Returns full file path as a string or empty string if canceled.
    """
    root = tk.Tk()
    root.withdraw()  # Hide root window
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=default_name,
        title="Save PDF Report As"
    )
    root.destroy()
    return file_path
