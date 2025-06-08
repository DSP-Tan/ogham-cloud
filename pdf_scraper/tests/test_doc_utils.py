from pdf_scraper.doc_utils import open_exam, get_images, get_doc_line_df
from pdf_scraper.doc_utils import get_captions
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

def test_point_filter():
    doc = open_exam(2006, "English", "AL", 1)
    images = get_images(doc)
    assert len(images)== 10

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
    check_nth_caption(2023,'Abdulrazak  Gurnah',0)
    check_nth_caption(2020, '', 0)






if __name__=="__main__":
    test_open_doc()
