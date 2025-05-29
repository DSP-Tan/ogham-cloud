import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect
import sys

from pdf_scraper.block_utils import identify_dual_column, get_block_text, sort_dual_column_blocks
from pdf_scraper.doc_utils import open_exam
from pdf_scraper.block_utils import is_empty_block, clean_blocks, print_block_table, get_block_table, rebox_blocks
from pdf_scraper.block_utils import preproc_blocks
from pdf_scraper.draw_utils  import get_pink_boundary, get_fill_df, in_the_pink
from pdf_scraper.draw_utils  import draw_rectangle_on_page
from pdf_scraper.line_utils  import get_line_df, print_line_table, get_all_lines, line_is_empty

pd.set_option("display.float_format", "{:.2f}".format)



year = int(sys.argv[1])

doc = open_exam(year, "english","al",1 )

def has_empty_line(block):
    if block["type"]:
        return False
    for line in block["lines"]:
        if line_is_empty(line):
            return True
    return False

for i, page in enumerate(doc):
    page_dict  = page.get_text("dict",sort=True)
    blocks    = page_dict["blocks"]
    non_empty_blocks = [block for block in blocks if not is_empty_block(block)]

    for n_block, block in enumerate(non_empty_blocks):
        if has_empty_line(block):
            print(f"page: {i}, block: {n_block}, year {year}")

import ipdb; ipdb.set_trace()