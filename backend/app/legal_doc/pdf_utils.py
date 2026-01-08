import os
import subprocess
from pathlib import Path


def convert_docx_to_pdf(docx_path: str) -> str:
    """Convert a DOCX file to PDF using LibreOffice (soffice) in headless mode.

    Returns the path to the generated PDF.
    """
    docx_p = Path(docx_path)
    if docx_p.suffix.lower() != ".docx":
        raise ValueError(f"Expected .docx path, got: {docx_path}")

    out_dir = docx_p.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_p = docx_p.with_suffix(".pdf")

    env = os.environ.copy()
    # Ensure LibreOffice can create its profile/cache somewhere writable
    env.setdefault("HOME", str(out_dir))

    cmd = [
        "soffice",
        "--headless",
        "--nologo",
        "--nofirststartwizard",
        "--norestore",
        "--convert-to",
        "pdf",
        "--outdir",
        str(out_dir),
        str(docx_p),
    ]

    r = subprocess.run(cmd, check=False, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout or "").strip()
        raise RuntimeError(f"soffice failed ({r.returncode}): {msg}")

    if not pdf_p.exists():
        raise RuntimeError(f"PDF not created at {pdf_p}")

    return str(pdf_p)
