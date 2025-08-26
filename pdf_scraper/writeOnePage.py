import fitz  
from pdf_scraper.doc_utils import open_exam

def extract_7th_page(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    if len(doc) < 7:
        print("The PDF has fewer than 7 pages.")
        return
    
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=6, to_page=6)  # 7th page (0-based index)
    new_doc.save(output_pdf)
    new_doc.close()
    doc.close()
    print(f"Extracted 7th page saved as {output_pdf}")



for year in range(2001,2026):
    new_doc = fitz.open()
    output_pdf = f"{year}_title_subtitle_check.pdf"
    doc = open_exam(year, "english", "al",1)
    pages = [2,4,6] if year != 2001 else [2,4,6,8]
    for i in pages:
        new_doc.insert_pdf(doc, from_page=i-1, to_page=i-1)  
    doc.close()
    new_doc.save(output_pdf)
    new_doc.close()