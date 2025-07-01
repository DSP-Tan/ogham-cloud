import pandas as pd
from pdf_scraper.doc_utils   import open_exam, get_doc_line_df, get_images
from pdf_scraper.image_utils import get_in_image_captions, get_in_image_lines


def test_get_in_image_lines():
    def get_image_and_doc(year:int, page:int, n_image:int, expected_index:pd.Index):
        doc = open_exam(year, "English", "AL", 1)
        doc_df = get_doc_line_df(doc)
        images = get_images(doc)
        image = [img for img in images if img["page"]==page][n_image]
        index = get_in_image_lines(image,doc_df)
        assert all(index == expected_index)
    get_image_and_doc(2023,3,0,pd.Index([144,145]))
    get_image_and_doc(2025,2,0,pd.Index([43]))


def test_get_in_image_captions():
    def get_image_and_doc(year, page, n_image, expected_caption):
        doc = open_exam(year, "English", "AL", 1)
        doc_df = get_doc_line_df(doc)
        images = get_images(doc)
        image = [img for img in images if img["page"]==page][n_image]
        indices = get_in_image_lines(image, doc_df)
        caption = get_in_image_captions(image,doc_df, indices)
        assert caption == expected_caption
    get_image_and_doc(2023,3,0,'Abdulrazak \nGurnah')
    get_image_and_doc(2025,2,0,'Underdog Jamaican Bobsled Team')

# To Do: also test the not-in-image captions.
