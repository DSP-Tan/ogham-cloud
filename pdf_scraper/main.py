import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect
import sys, re

from pdf_scraper.doc_utils   import open_exam, get_doc_line_df, identify_section_headers, identify_text_headers
from pdf_scraper.doc_utils   import identify_footers, identify_instructions, identify_subtitles, identify_subsubtitles
from pdf_scraper.doc_utils   import get_images,filter_images, assign_in_image_captions, identify_vertical_captions
from pdf_scraper.line_utils  import get_line_df, print_line_table, get_all_lines, line_is_empty, clean_line_df
from pdf_scraper.doc_utils   import new_vertical_captions, identify_all_page_clusters, enrich_doc_df_with_images


paper=1
level="al"
subject="english"

db_cols = ['year', 'page', 'text', 'x0', 'y0', 'x1', 'y1', 'common_font', 'mode_font', 'font_size', 'category', 'cluster'] 
all_dfs = []
for year in range(2001,2026):

    doc = open_exam(year, subject, level,paper)
    df = get_doc_line_df(doc)
    doc_width     = doc[0].rect.width

    images = get_images(doc)
    images = filter_images(images)
    assign_in_image_captions(df,images)
    
    df = clean_line_df(df)
    df = enrich_doc_df_with_images(df,images)
    identify_all_page_clusters(df,2.0/3.0, 1.15)

    identify_footers(df)
    identify_instructions(df)
    identify_section_headers(df)
    identify_text_headers(df, doc_width)
    identify_subtitles(df, doc_width)
    identify_subsubtitles(df, doc_width)

    df["year"] = year
    db_df = df[db_cols].copy()
    all_dfs.append(db_df)

    doc.close()

big_df = pd.concat(all_dfs, axis=0).reset_index(drop=True)
db_dest = Path(__file__).parent.parent / "database_api" / f"{subject}_p{paper}_{level}_exams.csv"

big_df.to_csv(db_dest)
    
