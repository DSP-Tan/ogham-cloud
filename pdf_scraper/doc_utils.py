from pathlib import Path
import fitz

subject_code = {
    "irish": "001",
    "english":"002",
    "mathematics":"003",
    "history":"004",
    "applied_mathematics":"020"
}

lang_code = {"irish":"IV", "english":"EV"}

def open_exam(year:int, subject: str, level: str, paper=0):
    code = subject_code[subject.lower()]
    fname    = f"LC{code}{level.upper()}P{paper}00EV_{year}.pdf"
    examDir  = Path(__file__).parent.parent / "Exams"  / subject.lower() / level.upper()
    pdf_file = examDir / fname

    return fitz.open(pdf_file)

def extract_and_print_page(input_pdf, output_pdf, n_page):
    doc = fitz.open(input_pdf)

    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=n_page-1, to_page=n_page-1)  # 7th page (0-based index)
    new_doc.save(output_pdf)
    new_doc.close()
    doc.close()
