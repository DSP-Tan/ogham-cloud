import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect
import sys, re

from pdf_scraper.block_utils import identify_dual_column, get_block_text, sort_dual_column_blocks
from pdf_scraper.doc_utils   import open_exam, get_doc_line_df, identify_section_headers, identify_text_headers
from pdf_scraper.doc_utils   import identify_footers, identify_instructions
from pdf_scraper.block_utils import is_empty_block, clean_blocks, print_block_table, get_block_table, rebox_blocks
from pdf_scraper.block_utils import preproc_blocks
from pdf_scraper.draw_utils  import get_pink_boundary, get_fill_df, in_the_pink
from pdf_scraper.line_utils  import get_line_df, print_line_table, get_all_lines, line_is_empty, clean_line_df


for year in range(2001,2026):

    doc = open_exam(year, "english", "al",1)
    df = get_doc_line_df(doc)
    
    doc_width     = doc[0].rect.width
    
    df = clean_line_df(df)
    identify_footers(df)
    identify_instructions(df)
    identify_section_headers(df)
    identify_text_headers(df, doc_width)

    test_categories = ["dual_col", "caption","instruction", "footer", "section","title"]
    
    result = df[df.section == 1]

    print(f"if year=={year}:")
    for i, row in result.iterrows():
        print(f"    assert doc_df.loc[{i}].text=='{row.text}'")
    print("--"*40)


    doc.close()
