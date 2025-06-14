import pandas as pd
from fitz import Rect

import numpy as np


from pdf_scraper.doc_utils import open_exam, get_images, filter_point_images
from pdf_scraper.doc_utils import get_doc_line_df
from pdf_scraper.doc_utils import get_captions, filter_images, assign_in_image_captions
from pdf_scraper.block_utils import clean_blocks
from pdf_scraper.line_utils import print_line_table, get_line_df
from pdf_scraper.image_utils import is_point_image, is_horizontal_strip,filter_point_images, filter_horizontal_strips
from pdf_scraper.image_utils import filter_horizontal_strips,get_stripped_images,stitch_strips, reconstitute_strips
from pdf_scraper.line_utils import closest_vertical_line
from pdf_scraper.general_utils import bbox_horiz_dist, shared_centre

def closest_line_closest_thing(image,doc_df):
    n_page   = image["page"]
    img_bbox = image["bbox"]
    page_df = doc_df[doc_df.page==image["page"]].copy()
    # I think just centred would be better to have here. There can be a caption which
    # wider than the image.
    overlap = page_df.apply(
        lambda row: bbox_horiz_dist((row["x0"],row["y0"],row["x1"],row["y1"] ),image["bbox"])==0,
        axis=1
        )
    overlap_df = page_df[overlap]
    centred = page_df.apply(
        lambda row: shared_centre( (row["x0"],row["y0"],row["x1"],row["y1"] ),image["bbox"]) ,
        axis=1
    )
    centred_df = page_df[overlap & centred]
    if len(centred_df) ==0:
        return None
    idx, dist = closest_vertical_line(img_bbox, centred_df, n_page)
    line_bbox = tuple(centred_df.loc[idx][["x0","y0","x1","y1"]])

    if (len(centred_df)==1):
        if dist > 30:
            return None
        else:
            return idx

    idx1, dist1 = closest_vertical_line(line_bbox, overlap_df, n_page)
    line1_bbox  = tuple(overlap_df.loc[idx1][["x0","y0","x1","y1"]])

    if dist < dist1:
        print("The line which is closest to this image is closer to the image than it's nearest line.")
        return idx
    return None

year=2025
doc = open_exam(year,"english","al",1)
doc_df = get_doc_line_df(doc)
images = get_images(doc)
print(f"number of raw images                : {len(images):10}")
images = filter_images(images)
print(f"number of filtered/fixed images     : {len(images):10}")


caption_indices, n_img = assign_in_image_captions(doc_df, images)


import ipdb; ipdb.set_trace()
#closest_line_closest_thing(images[2],doc_df)
