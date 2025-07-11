from pdf_scraper.doc_utils import open_exam, get_images, get_doc_line_df, filter_images
from pdf_scraper.doc_utils import get_captions, identify_footers
from fitz import Document


def test_open_doc():
    """
    Test pdfs can be opened, a page looked at, and .get_text method
    successfully run. Confirm type of document.
    """
    doc = open_exam(2016, "English", "AL", 1)
    page = doc[0]
    page_dict  = page.get_text("dict",sort=True)

    assert isinstance(doc, Document)


def test_get_images():
    def check_year(year, expected_images):
        doc = open_exam(year, "English", "AL", 1)
        images = get_images(doc)
        assert len(images)== expected_images
    check_year(2025,6)
    check_year(2024,8)
    check_year(2023,17)
    check_year(2003,4)

def test_filter_images():
    def check_filter(year, im_before, im_after):
        doc = open_exam(year, "English", "AL", 1)
        images = get_images(doc)
        assert len(images)== im_before
        images = filter_images(images)
        assert len(images)== im_after
    before = 136811
    after  = 10
    check_filter(2006,before,after)

def test_get_captions():
    def check_nth_caption(year, expected_caption,n):
        doc = open_exam(year, "English", "AL", 1)
        doc_df = get_doc_line_df(doc)
        images = get_images(doc)
        images = get_captions(doc_df, images)
        captioned_images = [img for img in images if img["caption"]]
        if captioned_images:
            caption = captioned_images[n]["caption"]
        else:
            caption=''
        assert caption == expected_caption
    check_nth_caption(2025, 'Underdog Jamaican Bobsled Team', 0)
    check_nth_caption(2024, '', 0)
    check_nth_caption(2023,'Abdulrazak \nGurnah',0)
    check_nth_caption(2022,'BOOKS ARE WEAPONS IN THE WAR OF IDEAS',0)
    check_nth_caption(2021, '', 0)
    check_nth_caption(2020, '', 0)

def test_identify_footers():
    for year in range(2001,2026):
        doc = open_exam(year,"english","al",1)
        doc_df = get_doc_line_df(doc)
        doc_df = identify_footers(doc_df)
        foots = doc_df[doc_df.footer==1].copy()
        if year ==2001:
            assert len(foots)==10
        elif year >2001 and year <= 2009:
            assert len(foots)==8
        elif year >2009 and year <= 2017:
            assert len(foots)==12
        else:
            assert len(foots)== 21








if __name__=="__main__":
    test_open_doc()
