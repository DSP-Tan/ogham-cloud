from pathlib import Path
import fitz

def open_exam(year:int):
    fname = f"LC002ALP100EV_{year}.pdf"
    examDir=Path.cwd().parent.parent / "Exams"  / "english" / 'AL'
    pdf_file = examDir / fname

    return fitz.open(pdf_file)

for year in range(2005,2025):
    print("--"*40)
    print(year)
    print("--"*40)
    doc              = open_exam(year)
    print(len(doc))
    for page in doc:
        page_width       = page.get_text("dict")["width"]   # This is a document wide thing doesn't need to be per page.
        page_height      = page.get_text("dict")["height"]   # This is a document wide thing doesn't need to be per page.
        print(page_width, page_height)


    print("--"*40)
    print("--"*40)

def get_max_width( year_start:int , year_end:int):
    max_width = 0
    for year in range(year_start,year_end):
        doc              = open_exam(year)
        for page in doc:
            page_width = page.get_text("dict")["width"]
            if page_width > max_width:  
                max_width = page_width
    return max_width
    