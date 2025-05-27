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
from pdf_scraper.draw_utils  import get_fill_colours

pd.set_option("display.float_format", "{:.8f}".format)

def open_exam(year:int):
    fname = f"LC002ALP100EV_{year}.pdf"
    examDir=Path.cwd().parent.parent / "Exams"  / "english" / 'AL'
    pdf_file = examDir / fname

    return fitz.open(pdf_file)

dfs=[]
for year in range(2011,2023):
    print("--"*40)
    print(year)
    print("--"*40)
    doc              = open_exam(year)
    fill_colours     = get_fill_colours(doc)

    xs = []
    for page in doc[1:7]:
        text_dict        = page.get_text("dict",sort=True)
        page_drawings    = page.get_drawings()
        blocks           = text_dict["blocks"]

        bounding_pink    = get_pink_boundary(page_drawings, fill_colours)
        clean_blocks     = preproc_blocks(blocks, bounding_pink)

        if not bounding_pink:
            continue
        pink_blocks      = [block for block in clean_blocks if in_the_pink(block["bbox"], bounding_pink) ]
        pink_lines       = get_all_lines(pink_blocks)
        if not pink_lines:
            continue
        pink_df          = get_line_df(pink_lines)
        pink_df.x0 = pink_df.x0.map(lambda x: round(x))
        pink_df.x1 = pink_df.x1.map(lambda x: round(x))


        counts    = pink_df.x0.value_counts()
        x_coords  = counts.index.values

        if len(counts)<2:
            continue
        xl   = x_coords[0]     if x_coords[0] < x_coords[1] else x_coords[1]
        n_xl = counts.iloc[0]  if x_coords[0] < x_coords[1] else counts.iloc[1]
        xr   = x_coords[0]     if x_coords[0] > x_coords[1] else x_coords[1]
        n_xr = counts.iloc[0]  if x_coords[0] > x_coords[1] else counts.iloc[1]

        third   = np.nan if len(x_coords) <3 else x_coords[2]
        n_third = np.nan if len(x_coords) <3 else counts.iloc[2]

        row={"xl":xl,"n_xl":n_xl,"xr":xr,"n_xr":n_xr,"third":third,"n_third":n_third}

        xs.append(row)

    col_df = pd.DataFrame(xs,index=[f'{year}_{i+2}' for i in range(len(xs))])
    dfs.append(col_df)
big_df=pd.concat(dfs,axis=0)
print(big_df.head(100))
import ipdb
ipdb.set_trace()
