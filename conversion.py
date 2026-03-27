from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from docx import Document
import os


def docx_to_pdf(docx_file, pdf_file):
    # Load DOCX
    document = Document(docx_file)

    # Create PDF
    pdf = SimpleDocTemplate(pdf_file, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    # Add paragraphs to PDF
    for para in document.paragraphs:
        text = para.text.strip()
        if text:
            elements.append(Paragraph(text.replace("\n", "<br/>"), normal_style))
            elements.append(Spacer(1, 0.2 * inch))

    pdf.build(elements)

    print("✅ Conversion successful!")
    print(f"📄 Created: {pdf_file}")


def start(filepath):
    if not os.path.exists(filepath):
        print("❌ File does not exist.")
        return None

    if not filepath.lower().endswith(".docx"):
        print("❌ Not a DOCX file.")
        return None

    # Generate output filename safely
    base_name = os.path.splitext(filepath)[0]
    converted_file = base_name + ".pdf"

    try:
        docx_to_pdf(filepath, converted_file)
    except Exception as e:
        print("❌ Conversion failed:", e)
        return None

    return converted_file