import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect
import sys, re

from pdf_scraper.block_utils import identify_dual_column, get_block_text, sort_dual_column_blocks
from pdf_scraper.doc_utils   import open_exam, get_doc_line_df, identify_section_headers, identify_text_headers
from pdf_scraper.doc_utils   import identify_footers, identify_instructions, identify_subtitles
from pdf_scraper.block_utils import is_empty_block, clean_blocks, print_block_table, get_block_table, rebox_blocks
from pdf_scraper.block_utils import preproc_blocks
from pdf_scraper.draw_utils  import get_pink_boundary, get_fill_df, in_the_pink
from pdf_scraper.line_utils  import get_line_df, print_line_table, get_all_lines, line_is_empty, clean_line_df

pd.set_option("display.float_format", "{:.2f}".format)

"""
subtitles
- bold
- at top of page under titles
- only on pages where there are titles.
- not dual column.
"""

for year in range(2001,2026):

    doc = open_exam(year, "english", "al",1)
    df = get_doc_line_df(doc)
    
    doc_width     = doc[0].rect.width
    middle        = doc_width/2
    standard_font = df.mode_font.mode()[0]
    median_font   = df.font_size.median()
    
    
    df = clean_line_df(df)
    identify_footers(df)
    identify_instructions(df)
    identify_section_headers(df)
    identify_text_headers(df, doc_width)
    identify_subtitles(df)
    
    #uncategorised = (df.section==0) & (df.caption ==0) & (df.instruction==0) & (df.title ==0 ) & (df.footer==0)
    #after_headers = df[uncategorised].groupby('page')['y0'].rank(method='first', ascending=True) <=6
    #title_on_page = df.groupby('page')['title'].transform('sum') >0
    #bold_font     = df.mode_font.str.contains("Bold")
    #pages         =  (df.page > 1) & (df.page <9)
    
    ##large_font    = df.font_size >= median_font*1.15
    ##centred       = ( (df.x0 + df.x1)/2 > middle -30 ) & ( (df.x0 + df.x1)/2 < middle +30 )

    #mask = bold_font & pages & uncategorised & after_headers & title_on_page
    
    #result = df.loc[mask , ["text","font_size","font_sizes", "page","mode_font"]].copy()
    #result = df.loc[df.title==1, ["text","font_size","font_sizes", "page","mode_font","common_font"] ]
    result = df[df.subtitle==1].copy()
    result.loc[:,"font_multip"] = result.font_size/median_font



    print(year)
    print(f"median font size: {median_font}")
    print(f"standard font   : {standard_font}")
    print("--"*40)
    #print(len(result))
    pd.set_option('display.max_colwidth', 180)  # or a large number like 500
    print(result.text)
    print("--"*40)

    #if year==2006:
    #    import ipdb; ipdb.set_trace()

    doc.close()
