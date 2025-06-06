from pdf_scraper.doc_utils import open_exam, get_images
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

def check_year(year, expected_images):
    doc = open_exam(year, "English", "AL", 1)
    images = get_images(doc)
    assert len(images)== expected_images

def test_get_images():
    check_year(2025,6)
    check_year(2024,8)
    check_year(2023,17)
    check_year(2003,4)

def test_point_filter():
    check_year(2006,10)





if __name__=="__main__":
    test_open_doc()
