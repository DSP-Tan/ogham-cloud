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


for year in range(2001,2026):
    doc = open_exam(year, "english", "al",1)
    df = get_doc_line_df(doc).drop(columns=["caption","dual_col","instruction"])

    df['rank'] = df.groupby('page')['y0'].rank(method='first', ascending=False)

    n_page_regex= r'page[ \xa0](?:1[0-2]|[1-9])[ \xa0]of[ \xa0](?:1[0-2]|[1-9])'
    lc_regex    = r'leaving[ \xa0]certificate[ \xa0]examination[ \xa0]20[0-9][0-9]'
    eng_regex   = r'english[ \xa0]–[ \xa0]higher[ \xa0]level[ \xa0]–[ \xa0]paper[ \xa0]1'
    num_regex   = r'^(?:1[0-2]|[1-9])$'

    pattern1 = df.text.str.lower().str.contains(n_page_regex, regex=True)
    pattern2 = df.text.str.lower().str.contains(lc_regex, regex=True)
    pattern3 = df.text.str.lower().str.contains(eng_regex, regex=True)
    pattern4 = df.text.str.strip().str.contains(num_regex, regex=True)
    bottom = df['rank'] <= 3

    result = df[ bottom & (pattern1 | pattern2 | pattern3 | pattern4 ) ].drop(columns=["rank"],inplace=False)


    print(year)
    print("--"*40)
    print(result.head(20))
    print("--"*40)

    doc.close()
