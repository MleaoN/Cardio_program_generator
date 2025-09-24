# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 09:24:25 2025

@author: leaon
"""


"""
Schedule planning (if you want to extend scheduling features)
"""



import pandas as pd
import matplotlib.pyplot as plt
import os

def append_schedule_to_pdf(pdf_obj, schedule_table, filename):
    """
    Appends a schedule table as a last page to an existing FPDF pdf_obj
    and saves it to filename.
    
    schedule_table: list of tuples (e.g. [("Session", "Assigned Program"), ...])
    """
    # Convert to DataFrame for easy table plotting
    df = pd.DataFrame(schedule_table[1:], columns=schedule_table[0])
    
    fig, ax = plt.subplots(figsize=(8, max(2, len(df)*0.3)))
    ax.axis('off')

    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.2)

    for (row, _), cell in table.get_celld().items():
        if row == 0:
            cell.set_fontsize(14)
            cell.set_text_props(weight='bold')
            cell.set_facecolor("#ADD8E6")

    plt.tight_layout()
    tmp_img = "temp_schedule_table.png"
    fig.savefig(tmp_img, dpi=300, bbox_inches='tight')
    plt.close(fig)

    pdf_obj.add_page()
    pdf_obj.set_font("Arial", 'B', 16)
    pdf_obj.cell(0, 12, "Monthly Schedule", ln=True, align="C")
    pdf_obj.image(tmp_img, x=10, w=190)
    os.remove(tmp_img)

    print(f"Schedule page appended and saved to: {filename}")
