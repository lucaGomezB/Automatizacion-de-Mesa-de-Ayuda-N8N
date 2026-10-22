"""Add disclaimer note to the beginning of a pandoc-generated DOCX."""
import sys
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

DOCX_PATH = Path(__file__).resolve().parent / "paper" / "tesis.docx"

def add_disclaimer(docx_path: Path) -> None:
    if not docx_path.exists():
        print(f"ERROR: {docx_path} not found")
        sys.exit(1)

    doc = Document(str(docx_path))

    # Create the disclaimer paragraph
    disclaimer = doc.paragraphs[0]._element  # placeholder to get styles
    new_para = doc.element.body.makeelement(
        disclaimer.tag, disclaimer.attrib
    )

    # Build the run
    from docx.oxml.ns import qn
    from lxml import etree

    # Create paragraph properties with gray background
    pPr = etree.SubElement(new_para, qn('w:pPr'))
    pBdr = etree.SubElement(pPr, qn('w:pBdr'))
    bottom = etree.SubElement(pBdr, qn('w:bottom'))
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '8')
    bottom.set(qn('w:color'), 'FF0000')

    shd = etree.SubElement(pPr, qn('w:shd'))
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:fill'), 'FFF3CD')  # light yellow background

    # Create run element
    r = etree.SubElement(new_para, qn('w:r'))
    rPr = etree.SubElement(r, qn('w:rPr'))
    b = etree.SubElement(rPr, qn('w:b'))
    color = etree.SubElement(rPr, qn('w:color'))
    color.set(qn('w:val'), '856404')
    sz = etree.SubElement(rPr, qn('w:sz'))
    sz.set(qn('w:val'), '20')  # 10pt

    t = etree.SubElement(r, qn('w:t'))
    t.text = "NOTA IMPORTANTE: "
    t.set(qn('xml:space'), 'preserve')

    # Normal text run
    r2 = etree.SubElement(new_para, qn('w:r'))
    rPr2 = etree.SubElement(r2, qn('w:rPr'))
    color2 = etree.SubElement(rPr2, qn('w:color'))
    color2.set(qn('w:val'), '856404')
    sz2 = etree.SubElement(rPr2, qn('w:sz'))
    sz2.set(qn('w:val'), '20')

    t2 = etree.SubElement(r2, qn('w:t'))
    t2.text = (
        "Este documento fue generado automaticamente desde la fuente LaTeX "
        "utilizando pandoc 3.8 con procesamiento de citas (--citeproc). "
        "El formato, las tablas y la disposicion de las paginas pueden diferir "
        "del original. Para la version autoritativa, consulte el archivo "
        "main.pdf compilado con XeLaTeX. "
        "This document was automatically generated from LaTeX source using "
        "pandoc 3.8 with citation processing. Formatting, tables, and page "
        "layout may differ from the original. Refer to main.pdf for the "
        "authoritative version."
    )
    t2.set(qn('xml:space'), 'preserve')

    # Insert at the beginning
    doc.element.body.insert(0, new_para)

    doc.save(str(docx_path))
    print(f"Disclaimer added to {docx_path.name}")
    print(f"File size: {docx_path.stat().st_size:,} bytes")


if __name__ == "__main__":
    add_disclaimer(DOCX_PATH)
