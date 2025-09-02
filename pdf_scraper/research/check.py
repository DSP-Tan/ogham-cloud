import pandas as pd
from fitz import Rect

import numpy as np


from pdf_scraper.doc_utils     import open_exam, get_images, filter_point_images
from pdf_scraper.doc_utils     import get_doc_line_df 
from pdf_scraper.line_utils    import clean_line_df
from pdf_scraper.doc_utils     import identify_footers, identify_instructions
from pdf_scraper.doc_utils     import identify_section_headers, identify_text_headers, identify_subtitles, identify_subsubtitles
from pdf_scraper.doc_utils     import get_captions, filter_images, assign_in_image_captions
from pdf_scraper.image_utils   import is_point_image, is_horizontal_strip,filter_point_images, filter_horizontal_strips
from pdf_scraper.image_utils   import filter_horizontal_strips,get_stripped_images,stitch_strips, reconstitute_strips
from pdf_scraper.line_utils    import closest_vertical_line
from pdf_scraper.general_utils import bbox_horiz_dist, shared_centre

def closest_line_closest_thing(image,doc_df):
    n_page   = image["page"]
    img_bbox = image["bbox"]
    page_df = doc_df[doc_df.page==image["page"]].copy()
    # I think just centred would be better to have here. There can be a caption which
    # wider than the image.
    overlap = page_df.apply(lambda row: bbox_horiz_dist((row["x0"],row["y0"],row["x1"],row["y1"] ),image["bbox"])==0, axis=1 )
    overlap_df = page_df[overlap]
    centred = page_df.apply(lambda row: shared_centre( (row["x0"],row["y0"],row["x1"],row["y1"] ),image["bbox"]) , axis=1 )
    centred_df = page_df[overlap & centred]
    if len(centred_df) ==0:
        return None
    idx, dist = closest_vertical_line(img_bbox, centred_df, n_page)
    line_bbox = tuple(centred_df.loc[idx, ["x0","y0","x1","y1"] ])

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

def identify_vertical_captions(image, df):
    """
    This function will identify any captions to image contained in df. 
    It will look for captions vertically above or below the image.
    """
    i_x0, i_y0, i_x1, i_y1 = image["bbox"]
    img_centre = (i_x0 + i_x1)/2
    within_image_frame = (df.x0 >= i_x0) & (df.x1 <= i_x1)
    centred = df.apply( lambda row: shared_centre( (row["x0"],row["y0"],row["x1"],row["y1"] ),image["bbox"]) , axis=1 )
    uncategorised    = (df.section==0) & (df.caption1 ==0) & (df.instruction==0) & (df.title ==0 ) & (df.footer==0) & (df.subtitle ==0 )
    above_top        = (i_y0 - df.y1) <= df.h*4
    below_bottom     = (df.y0 -i_y1)  <= df.h*4
    mask = within_image_frame & centred &  uncategorised & (above_top | below_bottom)

    df.loc[mask, "caption2"] = 1
    return df


year=2011
doc = open_exam(year,"english","al",1)
df = get_doc_line_df(doc)
images = get_images(doc)
print(f"number of raw images                : {len(images):10}")
images = filter_images(images)
print(f"number of filtered/fixed images     : {len(images):10}")

doc_width     = doc[0].rect.width

images = get_images(doc)
images = filter_images(images)
assign_in_image_captions(df,images)

df = clean_line_df(df)

identify_footers(df)
identify_instructions(df)
identify_section_headers(df)
identify_text_headers(df, doc_width)
identify_subtitles(df, doc_width)
identify_subsubtitles(df, doc_width)

caption_indices, n_img = assign_in_image_captions(df, images)


import ipdb; ipdb.set_trace()
fart = closest_line_closest_thing(images[2],df)

print(fart)


print(fart)
