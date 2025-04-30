import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect

from pdf_scraper.block_utils import identify_dual_column, get_block_text, sort_dual_column_blocks
from pdf_scraper.block_utils import is_empty_block, clean_blocks, print_block_table, get_block_table, rebox_blocks
from pdf_scraper.block_utils import preproc_blocks
from pdf_scraper.draw_utils  import get_pink_boundary, get_fill_df, in_the_pink
from pdf_scraper.draw_utils  import draw_rectangle_on_page
from pdf_scraper.line_utils  import get_line_df, print_line_table, get_all_lines

pd.set_option("display.float_format", "{:.2f}".format)

def open_exam(year:int):
    fname = f"LC002ALP100EV_{year}.pdf"
    examDir=Path.cwd().parent.parent / "Exams"  / "english" / 'AL'
    pdf_file = examDir / fname

    return fitz.open(pdf_file)

dfs=[]
for year in range(2005,2025):
    print("--"*40)
    print(year)
    print("--"*40)
    doc              = open_exam(year)
    print(len(doc))


    for i in range(1,7):
        page2_drawings   = doc[i].get_drawings()
        fill_df = get_fill_df(page2_drawings)
        if len(fill_df)==0:
            print(f"page {i} no fills.")
            continue
        fill_colour      = fill_df.fill.mode().values[0]
        print(fill_colour)

    print("--"*40)
    print("--"*40)
