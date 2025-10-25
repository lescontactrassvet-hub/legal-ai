import subprocess
from pathlib import Path


def convert_docx_to_pdf(docx_path: str) -> str:
    """
    Convert a DOCX file to PDF using unoconv. Returns the path to the generated PDF.

    This function assumes that `unoconv` is installed and available in the system path.
    It will generate a PDF file in the same directory as the input DOCX, replacing
    the `.docx` extension with `.pdf`.
    """
    pdf_path = docx_path.replace(".docx", ".pdf")
    # Ensure output directory exists
    output_dir = Path(pdf_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    # Run the conversion command
    subprocess.run(["unoconv", "-f", "pdf", docx_path], check=True)
    return pdf_path