import pandas as pd
import pytest
from pdf_scraper.doc_utils   import open_exam, get_doc_line_df, get_images, preproc_images
from pdf_scraper.image_utils import (
    get_in_image_captions, get_in_image_lines, filter_low_res_doubles,
    filter_point_images, sort_and_rename_images
    )


def check_image_filter(year, n_expected_images_filtered, filter_func):
    doc      = open_exam(year, "English", "AL", 1)
    images   = get_images(doc)
    images   = sort_and_rename_images(images)
    n_before = len(images)
    images   = filter_func(images)
    n_after  = len(images)
    doc.close()
    assert n_before - n_after == n_expected_images_filtered, f"Expected {n_expected_images_filtered} images filtered, but got {n_before - n_after} for year {year}."


# only 2005, 2006, and 2007 have point images
point_image_years = [(2005, 18267, filter_point_images), (2006, 136801,filter_point_images), (2007, 15018,filter_point_images)]  
other_years       = [(year,0,filter_point_images) for year in range(2001,2026) if year not in (2005,2006,2007) ]
year_ndiff        = point_image_years + other_years

@pytest.mark.parametrize("year, expected, filter_func", year_ndiff)
def test_filter_point_images(year, expected, filter_func):
    check_image_filter(year,expected, filter_func) 

years_with_doubles    = [(year, 1,filter_low_res_doubles) for year in range(2008,2017)]
years_without_doubles = [(year, 0,filter_low_res_doubles) for year in range(2017,2026)]
low_res_double_params = years_with_doubles + years_without_doubles
@pytest.mark.parametrize("year, expected, filter_func", low_res_double_params)
def test_filter_low_res_double(year, expected, filter_func):
    check_image_filter(year, expected, filter_func)

# To Do: Rewrite this using pytest.mark.parameterise in the same way as the image filter functions above.
def test_preproc_images():
    def check_filter(year, im_before, im_after):
        doc = open_exam(year, "English", "AL", 1)
        images = get_images(doc)
        assert len(images)== im_before
        images = preproc_images(images)
        assert len(images)== im_after
    check_filter(2005,18280,5)
    check_filter(2006,136811,4)
    check_filter(2007,15052, 5 )
    check_filter(2008,10, 7)
    check_filter(2009,13, 5)
    check_filter(2010,10, 5)
    check_filter(2011,9, 5)
    check_filter(2013,260, 6)
    check_filter(2023,17, 9)
    check_filter(2024,8, 8)
    check_filter(2025,6, 5)


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

