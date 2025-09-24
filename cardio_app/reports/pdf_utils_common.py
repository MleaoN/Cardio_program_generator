# -*- coding: utf-8 -*-
"""
Common utilities for PDF report generation
"""

import os
import re

USE_TK = os.environ.get("USE_TK", "0") == "1"

if USE_TK:
    import tkinter as tk
    from tkinter import filedialog


def format_seconds(seconds: float) -> str:
    """Convert seconds to a MM:SS string format."""
    try:
        seconds = float(seconds)
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    except (ValueError, TypeError):
        return "N/A"


def safe_filename(name: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)


def ask_save_filepath(default_name="cardio_report.pdf") -> str:
    """
    Return a file path where the PDF should be saved.
    - If Tkinter is enabled (local desktop use), open save dialog.
    - Otherwise (Render server), return a default filename.
    """
    if USE_TK:
        root = tk.Tk()
        root.withdraw()  # Hide root window
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_name,
            title="Save PDF Report As"
        )
        root.destroy()
        return file_path or ""
    else:
        # On Render (headless), just return a fixed filename in current dir
        return os.path.join(os.getcwd(), default_name)
