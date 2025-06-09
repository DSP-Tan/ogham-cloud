import pandas as pd
from fitz import Rect

import numpy as np


from pdf_scraper.doc_utils import open_exam, get_images, filter_point_images
from pdf_scraper.doc_utils import get_doc_line_df
from pdf_scraper.doc_utils import get_captions
from pdf_scraper.block_utils import clean_blocks
from pdf_scraper.line_utils import print_line_table, get_line_df
from pdf_scraper.image_utils import is_point_image, is_horizontal_strip,filter_point_images, filter_horizontal_strips
from pdf_scraper.image_utils import filter_horizontal_strips,get_stripped_images,stitch_strips, reconstitute_strips

year=2013
doc = open_exam(year,"english","al",1)
doc_df = get_doc_line_df(doc)
images = get_images(doc)

print(f"number of raw images                : {len(images):10}")
images = filter_point_images(images)
print(f"number of images after  point filter: {len(images):10}")
strips = get_stripped_images(images)
print(f"number of stripped images: {len(stripped):10}")
import ipdb; ipdb.set_trace()

images = get_captions(doc_df, images)
