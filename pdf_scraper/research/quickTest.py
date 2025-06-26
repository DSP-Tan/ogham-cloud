import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect
import sys, re

from pdf_scraper.block_utils import identify_dual_column, get_block_text, sort_dual_column_blocks
from pdf_scraper.doc_utils   import open_exam, get_doc_line_df
from pdf_scraper.block_utils import is_empty_block, clean_blocks, print_block_table, get_block_table, rebox_blocks
from pdf_scraper.block_utils import preproc_blocks
from pdf_scraper.draw_utils  import get_pink_boundary, get_fill_df, in_the_pink
from pdf_scraper.draw_utils  import draw_rectangle_on_page
from pdf_scraper.line_utils  import get_line_df, print_line_table, get_all_lines, line_is_empty

pd.set_option("display.float_format", "{:.2f}".format)

"""
Section Titles will have the following properties:
- Centred
- Larger than the median text size on page.
- Top of page
- Mostly on specific pages.
- Contain [section,I,II,Composing,Comprehending, n marks]
"""

for year in range(2001,2026):
    doc = open_exam(year, "english", "al",1)
    df = get_doc_line_df(doc).drop(columns=["caption","dual_col","instruction"])


    df['rank'] = df.groupby('page')['y0'].rank(method='first', ascending=True)

    section_regex= r'section[\xa0 ]*(?:I{1,2}|[1-2])'
    compre_regex = r'comprehending'
    compos_regex = r'composing'
    marks_regex  = r'\(\d{1,3}\)\s*marks'

    pattern1 = df.text.str.contains(section_regex,flags=re.IGNORECASE, regex=True)
    pattern2 = df.text.str.lower().str.contains(compre_regex, regex=True)
    pattern3 = df.text.str.lower().str.contains(compos_regex, regex=True)
    pattern4 = df.text.str.strip().str.contains(marks_regex, regex=True)
    top = df['rank'] <= 4

    result = df[ top & (pattern1 | pattern2 | pattern3 | pattern4 ) ].drop(columns=["rank"],inplace=False)


    print(year)
    print("--"*40)
    print(len(result))
    print(result.head(40))
    print("--"*40)

    #if  year==2001:
    #    import ipdb; ipdb.set_trace()

    doc.close()
