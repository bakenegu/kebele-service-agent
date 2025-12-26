import os
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def ensure_generated_dir() -> Path:
    """Ensure generated PDF directory exists."""
    gen_dir = Path("data/generated")
    gen_dir.mkdir(parents=True, exist_ok=True)
    return gen_dir


def generate_birth_certificate_pdf(data: dict, output_path: str) -> str:
    """
    Generate a birth certificate PDF using reportlab.
    
    Args:
        data: Dictionary containing:
            - child_name: str
            - date_of_birth: str (DD/MM/YYYY)
            - sex: str (Male/Female)
            - father_name: str
            - mother_name: str
            - reference_number: str
        output_path: Path where PDF should be saved
        
    Returns:
        Path to generated PDF file
    """
    ensure_generated_dir()
    
    # Create PDF canvas
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 2 * cm, "Federal Democratic Republic of Ethiopia")
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 3.5 * cm, "Birth Certificate")
    
    # Draw a line under title
    c.setLineWidth(1)
    c.line(2 * cm, height - 4 * cm, width - 2 * cm, height - 4 * cm)
    
    # Content area
    y_start = height - 5.5 * cm
    line_height = 0.8 * cm
    c.setFont("Helvetica", 12)
    
    # Child Name
    y = y_start
    c.setFont("Helvetica-Bold", 12)
    c.drawString(3 * cm, y, "Child Name:")
    c.setFont("Helvetica", 12)
    c.drawString(6 * cm, y, data.get("child_name", ""))
    y -= line_height
    
    # Date of Birth
    c.setFont("Helvetica-Bold", 12)
    c.drawString(3 * cm, y, "Date of Birth:")
    c.setFont("Helvetica", 12)
    c.drawString(6 * cm, y, data.get("date_of_birth", ""))
    y -= line_height
    
    # Sex
    c.setFont("Helvetica-Bold", 12)
    c.drawString(3 * cm, y, "Sex:")
    c.setFont("Helvetica", 12)
    c.drawString(6 * cm, y, data.get("sex", ""))
    y -= line_height * 1.5
    
    # Father Name
    c.setFont("Helvetica-Bold", 12)
    c.drawString(3 * cm, y, "Father Name:")
    c.setFont("Helvetica", 12)
    c.drawString(6 * cm, y, data.get("father_name", ""))
    y -= line_height
    
    # Mother Name
    c.setFont("Helvetica-Bold", 12)
    c.drawString(3 * cm, y, "Mother Name:")
    c.setFont("Helvetica", 12)
    c.drawString(6 * cm, y, data.get("mother_name", ""))
    y -= line_height * 1.5
    
    # Reference Number
    c.setFont("Helvetica-Bold", 12)
    c.drawString(3 * cm, y, "Reference Number:")
    c.setFont("Helvetica", 12)
    c.drawString(6 * cm, y, data.get("reference_number", ""))
    y -= line_height
    
    # Issue Date
    issue_date = datetime.now().strftime("%d/%m/%Y")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(3 * cm, y, "Issue Date:")
    c.setFont("Helvetica", 12)
    c.drawString(6 * cm, y, issue_date)
    
    # Footer
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, 1.5 * cm, "Kebele Service Agent MVP")
    
    # Save PDF
    c.save()
    return output_path

