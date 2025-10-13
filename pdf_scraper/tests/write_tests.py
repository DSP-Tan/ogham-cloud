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


paper=1
level="al"
subject="english"


test_categories = ["dual_col", "caption1","caption2", "instruction", "footer", "section","title","subtitle","subsubtitle"]
cat = "temp"
write = False

out_dir = Path(__file__).parent.resolve() / Path(f"resources/expected_{cat}s")
out_dir.mkdir(parents=True, exist_ok=True)

for year in range(2001,2026):

    doc = open_exam(year, subject, level,paper)
    df = get_doc_line_df(doc)
    doc_width     = doc[0].rect.width

    images = get_images(doc)
    images = preproc_images(images)
    assign_in_image_captions(df,images)
    
    df = clean_line_df(df)
    df = enrich_doc_df_with_images(df,images)
    identify_all_page_clusters(df,2.0/3.0, 1.15, True)

    identify_footers(df)
    identify_instructions(df)
    identify_section_headers(df)
    identify_text_headers(df, doc_width)
    identify_subtitles(df, doc_width)
    identify_subsubtitles(df, doc_width)


    new_vertical_captions(df, images)

    
    test_df = df[df.category == cat]

    if write:
        out_file = out_dir / f"{subject}_{level}_{paper}_{year}.txt"
        with out_file.open("w", encoding="utf-8") as f:
            for text in test_df.text.tolist():
                f.write(text + "\n")  # preserve \xa0 and all Unicode chars
    
    if year==2001:
        print(f"if year=={year}:")
    else:
        print(f"elif year=={year}:")
    print(f"    assert len(test_df)=={len(test_df)}")
    for i, i_row in enumerate(test_df.iterrows() ):
        idx, row = i_row
        print(f"    assert test_df.iloc[{i}].text=={repr(row.text)}; page = {row.page}")

    doc.close()
