import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect
import sys, re

from pdf_scraper.block_utils import identify_dual_column, get_block_text, sort_dual_column_blocks
from pdf_scraper.doc_utils   import open_exam, get_doc_line_df, identify_section_headers, identify_text_headers
from pdf_scraper.doc_utils   import identify_footers, identify_instructions, identify_subtitles, identify_subsubtitles
from pdf_scraper.doc_utils   import get_images,preproc_images, assign_in_image_captions, identify_vertical_captions
from pdf_scraper.draw_utils  import get_pink_boundary, get_fill_df, in_the_pink
from pdf_scraper.line_utils  import get_line_df, print_line_table, get_all_lines, line_is_empty, clean_line_df
from pdf_scraper.doc_utils   import new_vertical_captions, identify_all_page_clusters, enrich_doc_df_with_images
from pdf_scraper.image_utils import filter_point_images


paper=1
level="al"
subject="english"
year_and_diff = []

for year in range(2001,2026):


    doc = open_exam(year, subject, level,paper)
    df = get_doc_line_df(doc)
    doc_width     = doc[0].rect.width

    images = get_images(doc)
    n_before = len(images)
    images = filter_point_images(images)
    n_after = len(images)

    n_diff = n_before -n_after 

    
    if year==2001:
        print(f"if year=={year}:")
    else:
        print(f"elif year=={year}:")
    print(f"    get_image_and_doc({year},{n_diff})")

    year_and_diff.append((year,n_diff))

    doc.close()

print(year_and_diff)
