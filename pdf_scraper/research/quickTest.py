import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect
import sys

from pdf_scraper.block_utils import identify_dual_column, get_block_text, sort_dual_column_blocks
from pdf_scraper.doc_utils   import open_exam, get_doc_line_df
from pdf_scraper.block_utils import is_empty_block, clean_blocks, print_block_table, get_block_table, rebox_blocks
from pdf_scraper.block_utils import preproc_blocks
from pdf_scraper.draw_utils  import get_pink_boundary, get_fill_df, in_the_pink
from pdf_scraper.draw_utils  import draw_rectangle_on_page
from pdf_scraper.line_utils  import get_line_df, print_line_table, get_all_lines, line_is_empty

pd.set_option("display.float_format", "{:.2f}".format)


#new_doc = fitz.open()
#for year in range(2001,2026):
#    doc = open_exam(year, "english", "al",1)
#    for p in [3, 5, 7]:
#        new_doc.insert_pdf(doc, from_page=p-1, to_page=p-1)
#    doc.close()
#
#new_doc.save("check_NBS.pdf")
#new_doc.close()

doc = open_exam(2017)
df = get_doc_line_df(doc)
# The n.b instruction line is usually:
# "N.B. Candidates may NOT answer Question A and Question B on the same text."
# However in 2021 it says
# "N.B. Answer only ONE question in Section I, either one Question A OR one Question B on one text."


for year in range(2001,2026):
    doc = open_exam(year, "english", "al",1)
    df = get_doc_line_df(doc)
    page = (df.page != 1)
    pattern1 = df.text.str.lstrip().str.contains(r"^N\.B\.")
    pattern2 = df.text.str.contains(r"^Candidates may NOT")
    pattern3 = df.text.str.contains(r"^Questions.*A.*and.*B.*carry.*50.*marks.*each")

    general_nb_pattern = r"N\.B\..*[aA]nswer.*Question.*A.*Question.*B.*on.*text"
    instructs = df[page & (pattern1 | pattern2 | pattern3) ]
    print(f"{'year':<5}:{'count':<5}")
    print(f"{year:<5}:{len(instructs):<5}")
    print(instructs.head(10))

    doc.close()
