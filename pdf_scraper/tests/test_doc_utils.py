from pdf_scraper.doc_utils import open_exam, get_images, get_doc_line_df, filter_images, assign_in_image_captions
from pdf_scraper.doc_utils import get_captions, identify_footers, identify_section_headers, identify_text_headers
from pdf_scraper.doc_utils import identify_instructions, identify_subtitles, identify_subsubtitles
from pdf_scraper.line_utils import clean_line_df
from fitz import Document
from pathlib import Path
import pytest 


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
        foots = doc_df[doc_df.category=="footer"].copy()
        if year ==2001:
            assert len(foots)==10
        elif year >2001 and year <= 2009:
            assert len(foots)==8
        elif year >2009 and year <= 2017:
            assert len(foots)==12
        else:
            assert len(foots)== 21


def load_expected(year: int, cat: str, subject: str, level: str, paper: int) -> list[str]:
    out_dir = Path(__file__).parent.resolve() / Path(f"resources/expected_{cat}s")
    path = out_dir/ f"{subject}_{level}_{paper}_{year}.txt"
    return path.read_text(encoding="utf-8").splitlines()

def check_category(year, subject, level, paper, cat):
    doc = open_exam(year, subject, level, paper)
    df = get_doc_line_df(doc)
    doc_width = doc[0].rect.width

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

    got = df[df.category == cat].text.tolist()
    expected = load_expected(year, cat ,subject, level, paper)

    assert got == expected

    doc.close()
    

@pytest.mark.parametrize("year", range(2001, 2026))
def test_identify_text_section(year):
    check_category(year, "english","al",1,"section")

@pytest.mark.parametrize("year", range(2001, 2026))
def test_identify_text_titles(year):
    check_category(year, "english","al",1,"title")

@pytest.mark.parametrize("year", range(2001, 2026))
def test_identify_text_subtitles(year):
    check_category(year, "english","al",1,"subtitle")



def test_identify_text_subsubtitles():
    for year in range(2001,2026):
        doc = open_exam(year, "english", "al",1)
        df = get_doc_line_df(doc)
        doc_width     = doc[0].rect.width
        
        images = get_images(doc)
        images = filter_images(images)
        assign_in_image_captions(df,images)
    
        df = clean_line_df(df)
        identify_footers(df)
        identify_instructions(df)
        identify_section_headers(df)
        identify_text_headers(df, doc_width)
        identify_subtitles(df,doc_width)
        identify_subsubtitles(df,doc_width)
        test_df = df[df.category=="subsubtitle"].copy()
        if year==2003:
            assert len(test_df)==7
            assert test_df.iloc[0].text=='It was King Pelias who sent them out.  He had heard an oracle which warned him of a dreadful tale –'
            assert test_df.iloc[1].text=='death through the machinations of the man whom he should see coming from the town with one foot'
            assert test_df.iloc[2].text=='bare… The prophecy was soon confirmed.  Jason, fording the Anaurus in a winter spate, lost one of his'
            assert test_df.iloc[3].text=='sandals, which stuck in the bed of the flooding river, but saved the other from the mud and shortly'
            assert test_df.iloc[4].text=='appeared before the king.  And no sooner did the king see him than he thought of the oracle and'
            assert test_df.iloc[5].text=='decided to send him on a perilous adventure overseas.  He hoped that things might so fall out, either at'
            assert test_df.iloc[6].text=='sea or in outlandish parts, that Jason would never see his home again.'
        elif year==2005:
            assert len(test_df)==2
            assert test_df.iloc[0].text=='World exclusive ! Irish Rock Diva speaks to readers from '
            assert test_df.iloc[1].text=='her Italian villa. '
        else:
            assert len(test_df) == 0
        

def old_test_identify_text_titles_subtitles():
    # we are keeping these here only for the notes.
    for year in range(2001,2026):
        doc = open_exam(year, "english", "al",1)
        df = get_doc_line_df(doc)
        doc_width     = doc[0].rect.width
    
        df = clean_line_df(df)
        identify_footers(df)
        identify_instructions(df)
        identify_section_headers(df)
        identify_text_headers(df, doc_width)
        identify_subtitles(df,doc_width)
        test_df = df[df.subtitle==1].copy()
        if year==2003:
            assert len(test_df)==7  # Text 3 has no subtitles
        if year==2007:
            assert len(test_df)==6  # Text 3 has no subtitles
        if year==2008:
            assert len(test_df)==6   # Text 3 is a big image, needs ocr
        if year==2019:
            assert len(test_df)==10
            assert test_df.iloc[0].text=='This\xa0edited\xa0piece\xa0is\xa0based\xa0on\xa0an\xa0article\xa0by\xa0Jeanette\xa0Winterson\xa0entitled,\xa0“What\xa0is\xa0Art\xa0for?”\xa0\xa0\xa0'
            assert test_df.iloc[1].text=='The\xa0writer\xa0uses\xa0the\xa0term\xa0“art”\xa0to\xa0include\xa0all\xa0artistic\xa0forms,\xa0e.g.\xa0painting,\xa0writing,\xa0music,\xa0etc.\xa0\xa0\xa0'
            assert test_df.iloc[8].text=='The\xa0essay\xa0appears\xa0in\xa0a\xa0collection\xa0of\xa0her\xa0work\xa0entitled,\xa0Moranthology,\xa0and\xa0is\xa0also\xa0anthologised\xa0in\xa0'
            assert test_df.iloc[9].text=='The\xa0Library\xa0Book,\xa0a\xa0series\xa0of\xa0essays\xa0by\xa0well‐known\xa0writers\xa0in\xa0support\xa0of\xa0public\xa0libraries.\xa0'
        if year==2022:
            assert len(test_df)==9
            assert test_df.iloc[7].text=='we witness the book telling its own story, including its rescue from the Nazi book burning in '
            assert test_df.iloc[8].text=='1933. '
            # assert test_df.loc[189].text=='Extract 1: Tom Gatti from the introduction to '  # These are "column titles"
            # assert test_df.loc[190].text=='his book, Long Players. '
        if year==2023:
            assert len(test_df)==12
            assert test_df.iloc[9].text=='July 2022: an introduction from Patricia Scanlon, Ireland’s first Artificial Intelligence '
            assert test_df.iloc[10].text=='Ambassador, published in The Irish Times and a feature by Ben Spencer printed in The Sunday '
            assert test_df.iloc[11].text=='Times magazine entitled, “I’m better than the Bard.”   '
            #assert test_df.loc[289].text=='Patricia Scanlon: ' # Shouldn't be there.
            #assert test_df.loc[290].text=='Ben Spencer: '      # Shouldn't be there.
        if year==2025:           # There is hidden text here, which is causing repeated content. It will need to be removed, perhaps by cross reference to ocr.
            assert len(test_df)==12
            assert test_df.iloc[6].text=='TEXT 3 consists of edited extracts from Samantha Harvey’s novel, Orbital, published in 2024.  It '
            assert test_df.iloc[7].text=='tells the story of six astronauts in a H-shaped spacecraft rotating above the earth.  They are there '
            assert test_df.iloc[8].text=='Text 3 consists of edited extracts from Samantha Harvey’s novel, Orbital, published in 2024. It tells '
            assert test_df.iloc[9].text=='to collect meteorological data and conduct scientific experiments.  But mostly they observe.   '
            assert test_df.iloc[10].text=='the story of six astronauts who rotate in a spacecraft above the earth. They are there to collect '
            assert test_df.iloc[11].text=='meteorological data and conduct scientific experiments. But mostly they observe. '

        test_df = df[df.title==1].copy()
        if year==2008:
            assert len(test_df)==4                             # text 3 is all image
        elif year==2009:
            assert len(test_df)==7
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[5].text=='The Decisive Moment '
            assert test_df.iloc[6].text=='Creating the Decisive Moment '  # This appears at the top of the second page of Text3, we can still call it a title. 
        elif year==2017:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT\xa01\xa0–\xa0THE\xa0WORLD\xa0OF\xa0POETRY\xa0'
            assert test_df.iloc[1].text=='TEXT\xa02\xa0–\xa0A\xa0CONNECTED\xa0WORLD\xa0\xa0'
            assert test_df.iloc[2].text=='TEXT\xa03\xa0–\xa0THE\xa0WORLD\xa0OF\xa0CHILDHOOD\xa0'

if __name__=="__main__":
    test_open_doc()
