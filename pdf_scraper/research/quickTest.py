import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect
import sys, re

from pdf_scraper.block_utils import identify_dual_column, get_block_text, sort_dual_column_blocks
from pdf_scraper.doc_utils   import open_exam, get_doc_line_df, identify_section_headers
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
    df = get_doc_line_df(doc)

    identify_section_headers(df)
    df['rank'] = df.groupby('page')['y0'].rank(method='first', ascending=True)

    if df.section.sum() == 0:
        raise RuntimeError("Assign section headings first")

    middle        = doc[0].rect.width/2
    median_font   = df.font_size.median()
    large_font    = df.font_size >= median_font*1.15
    bold_font     = df.mode_font.str.contains("Bold")
    pages        =  (df.page > 1) & (df.page <9)
    centred       = ( (df.x0 + df.x1)/2 > middle -30 ) & ( (df.x0 + df.x1)/2 < middle +30 )
    uncategorised = (df.section==0) & (df.caption ==0) & (df.instruction==0)
    top           = df['rank'] <= 20

    result = df.loc[large_font & bold_font & pages & uncategorised & centred & top , ["text","font_size","font_sizes", "page","mode_font","common_font"]].copy()
    result["font_multip"] = result.font_size/median_font

    if year==2010:
        import ipdb; ipdb.set_trace()



    print(year)
    print(f"median font size: {median_font}")
    print("--"*40)
    print(len(result))
    print(result.head(40))
    print("--"*40)

    #if  year==2001:
    #    import ipdb; ipdb.set_trace()

    doc.close()
