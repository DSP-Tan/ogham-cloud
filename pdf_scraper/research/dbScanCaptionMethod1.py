import pandas as pd
import numpy as np
from pathlib import Path
import fitz
from fitz import Rect
import sys, re
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import DBSCAN

from pdf_scraper.block_utils import identify_dual_column, get_block_text, sort_dual_column_blocks, clean_blocks
from pdf_scraper.doc_utils   import open_exam, get_doc_line_df, identify_section_headers, identify_text_headers, get_path_from_doc
from pdf_scraper.doc_utils   import identify_footers, identify_instructions, identify_subtitles, identify_subsubtitles
from pdf_scraper.draw_utils  import draw_rectangles_on_page, draw_rectangles_for_all_pages
from pdf_scraper.line_utils  import get_line_df, print_line_table, get_all_lines, line_is_empty, re_box_line
from pdf_scraper.line_utils  import is_buffered_line, clean_line_df, get_df_bbox
from pdf_scraper.doc_utils   import get_images, preproc_images, get_raw_lines, assign_in_image_captions, identify_vertical_captions
from pdf_scraper.line_utils  import get_line_text
from pdf_scraper.clustering.cluster_utils import find_y0_dL

from pdf_scraper.image_utils import show_image, show_all_imgs

pd.set_option("display.float_format", "{:.2f}".format)
pd.set_option("display.max_colwidth", 200)


year=2019
doc    = open_exam(year, "english", "al",1)
df     = get_doc_line_df(doc)

images = get_images(doc)
images = preproc_images(images)
assign_in_image_captions(df,images)

doc_width     = doc[0].rect.width
middle        = doc_width/2
standard_font = df.mode_font.mode()[0]
median_font   = df.font_size.median()


df = clean_line_df(df)
identify_footers(df)
identify_instructions(df)
identify_section_headers(df)
identify_text_headers(df, doc_width)
identify_subtitles(df, doc_width)
identify_subsubtitles(df,doc_width)

for image in images:
    if image["page"] <2 or image["page"] >8:
        continue
    identify_vertical_captions(df, image)

## Now we will use dbscan to possibly de-categorise lines incorrectly categorised as
## captions.    
    

# Wisely determine dL
dL =find_y0_dL(df, "caption2")
print(dL)

line_scale = 1.15


page = np.unique(df[df.caption2==1].page)[0]
# DBSCAN to cluster doc page
clust_df = df[df.page==page].copy()
eps = dL*1.15; min_neighbs = 2
scan = DBSCAN(eps=eps, min_samples=min_neighbs)
scan.fit(clust_df[["y0"]])
clust_df["cluster"]=scan.labels_

# If the caption belongs to a contiguous block that is 100% not captions. Then make it not a caption as well.
for i, row in clust_df[clust_df.caption2==1].iterrows():
    i_clust = row.cluster
    if i_clust == -1: # We can have just a one line caption out somewhere on its own.
        continue
    clust_caption = np.unique(clust_df.loc[ (clust_df.index !=i) & (clust_df.cluster==i_clust) , "caption2" ])
    if len(clust_caption) == 1 and clust_caption[0]==0:
        clust_df.loc[i, "caption2"] = 0
        
        
clust_df.loc[clust_df.caption2==1, ["text","y0","cluster","caption2"]].head(45)

# Draw clusters on page
page = np.unique(df[df.caption2==1].page)[0]
rectangies = []
for i in np.unique(scan.labels_)[1:]:
    temp_df = clust_df[clust_df.cluster==i]
    rectangies.append( Rect(get_df_bbox(temp_df)) )
rectangies.append( Rect( (0, 0, 10, 10)))
doc_path = get_path_from_doc(doc)
draw_rectangles_on_page(doc_path, "out.pdf", int(page-1),rectangies)


