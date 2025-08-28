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
        foots = doc_df[doc_df.footer==1].copy()
        if year ==2001:
            assert len(foots)==10
        elif year >2001 and year <= 2009:
            assert len(foots)==8
        elif year >2009 and year <= 2017:
            assert len(foots)==12
        else:
            assert len(foots)== 21



def test_identify_text_titles():
    for year in range(2001,2026):
        doc = open_exam(year,"english","al",1)
        width = doc[0].rect.width
        doc_df = get_doc_line_df(doc)
        doc_df = clean_line_df(doc_df)

        identify_section_headers(doc_df)
        identify_text_headers(doc_df, width)
        test_df = doc_df[doc_df.title==1].copy()
        if year==2001:
            assert len(test_df)==8
            assert test_df.iloc[0].text=='TEXT 1'
            assert test_df.iloc[1].text=='BEING IRISH'
            assert test_df.iloc[2].text=='TEXT 2'
            assert test_df.iloc[3].text=='A NEW IRELAND'
            assert test_df.iloc[4].text=='TEXT 3'
            assert test_df.iloc[5].text=='AN IRISH SENSE OF HUMOUR'
            assert test_df.iloc[6].text=='TEXT 4'
            assert test_df.iloc[7].text=='IMAGES OF IRELAND'
        elif year==2002:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='THE FAMILY OF MAN '
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='FAMILY HOME FOR SALE '
            assert test_df.iloc[4].text=='TEXT 3 '
            assert test_df.iloc[5].text=='FAMILIES IN A TIME OF CRISIS '
        elif year==2003:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT 1'
            assert test_df.iloc[1].text=='THE FIRST GREAT JOURNEY'
            assert test_df.iloc[2].text=='TEXT 2'
            assert test_df.iloc[3].text=='A STRANGE COMPANION'
            assert test_df.iloc[4].text=='TEXT 3'
            assert test_df.iloc[5].text=='DESTINATIONS'
        elif year==2004:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='THE IMPORTANCE OF PLAY '
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='PAUL’S FIRST DAY AT WORK '
            assert test_df.iloc[4].text=='TEXT 3 '
            assert test_df.iloc[5].text=='WORK AND PLAY '
        elif year==2005:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='AN ORDINARY LIFE '
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='ORDINARY LIVES IN WAR TIME '
            assert test_df.iloc[4].text=='TEXT 3 '
            assert test_df.iloc[5].text=='PUBLIC LIVES '
        elif year==2006:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT I '
            assert test_df.iloc[1].text=='“WHAT SEEMS TO BE THE PROBLEM, LADY SARAH?” '
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='GHOST WRITING    '
            assert test_df.iloc[4].text=='TEXT 3 '
            assert test_df.iloc[5].text=='PRETENCE '
        elif year==2007:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='FILMS TO CHANGE YOUR LIFE '
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='LONDON, PAST AND PRESENT '
            assert test_df.iloc[4].text=='TEXT 3 '
            assert test_df.iloc[5].text=='FORCES FOR CHANGE? '
        elif year==2008:
            assert len(test_df)==4                             # text 3 is all image
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='TEENAGE IDENTITY '
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='FALSE IDENTITY? '
        elif year==2009:
            assert len(test_df)==7
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='Decisions for Society'
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='Personal Decisions '
            assert test_df.iloc[4].text=='TEXT 3 '
            assert test_df.iloc[5].text=='The Decisive Moment '
            assert test_df.iloc[6].text=='Creating the Decisive Moment '  # This appears at the top of the second page of Text3, we can still call it a title. 
        elif year==2010:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='A Personal Future '
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='A Global Future'
            assert test_df.iloc[4].text=='TEXT 3 '
            assert test_df.iloc[5].text=='An Imagined Future '
        elif year==2011:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT 1'
            assert test_df.iloc[1].text=='TEXT 2 '
            assert test_df.iloc[2].text=='TEXT 3 '
        elif year==2012:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='Personal Memories  '
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='Shared Memories  '
            assert test_df.iloc[4].text=='TEXT 3 '
            assert test_df.iloc[5].text=='A journey remembered and revisited  '
        elif year==2013:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='TEXT 2  '
            assert test_df.iloc[2].text=='TEXT 3 '
        elif year==2014:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT 1'
            assert test_df.iloc[1].text=='AN INFLUENTIAL EVENT '
            assert test_df.iloc[2].text=='TEXT 2'
            assert test_df.iloc[3].text=='CULTURAL INFLUENCES '
            assert test_df.iloc[4].text=='TEXT 3'
            assert test_df.iloc[5].text=='THE INFLUENCE OF THE PAST '
        elif year==2015:
            assert len(test_df)==6
            assert test_df.iloc[0].text=='TEXT 1 '
            assert test_df.iloc[1].text=='BECAUSE WE CAN, WE MUST '
            assert test_df.iloc[2].text=='TEXT 2 '
            assert test_df.iloc[3].text=='GHOSTS DON’T SHOW UP ON CCTV '
            assert test_df.iloc[4].text=='TEXT 3 '
            assert test_df.iloc[5].text=='A LIFE IN TIME '
        elif year==2016:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT 1 – A DRAMATIC JOURNEY '
            assert test_df.iloc[1].text=='TEXT 2 – A PERSONAL JOURNEY '
            assert test_df.iloc[2].text=='TEXT 3 – JOURNEY INTO SPACE '
        elif year==2017:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT\xa01\xa0–\xa0THE\xa0WORLD\xa0OF\xa0POETRY\xa0'
            assert test_df.iloc[1].text=='TEXT\xa02\xa0–\xa0A\xa0CONNECTED\xa0WORLD\xa0\xa0'
            assert test_df.iloc[2].text=='TEXT\xa03\xa0–\xa0THE\xa0WORLD\xa0OF\xa0CHILDHOOD\xa0'
        elif year==2018:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT\xa01\xa0–\xa0ADVICE\xa0TO\xa0YOUNG\xa0WRITERS\xa0'
            assert test_df.iloc[1].text=='TEXT\xa02\xa0–\xa0A\xa0SUCCESSFUL\xa0YOUNG\xa0WRITER\xa0\xa0'
            assert test_df.iloc[2].text=='TEXT\xa03\xa0–\xa0A\xa0TRAGIC\xa0YOUNG\xa0POET\xa0'
        elif year==2019:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT\xa01\xa0–\xa0WHAT\xa0IS\xa0ART\xa0FOR?\xa0'
            assert test_df.iloc[1].text=='TEXT\xa02\xa0–\xa0A\xa0PHOTOGRAPHER’S\xa0PERSPECTIVE\xa0'
            assert test_df.iloc[2].text=='TEXT\xa03\xa0–\xa0LIBRARIES:\xa0CATHEDRALS\xa0OF\xa0OUR\xa0SOULS\xa0'
        elif year==2020:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT 1 – FROM GENRE to GENRE '
            assert test_df.iloc[1].text=='TEXT 2 – DETECTIVE FICTION '
            assert test_df.iloc[2].text=='TEXT 3 – SCIENCE FICTION (SCI-FI) '
        elif year==2021:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT 1 – TIME PIECES   '
            assert test_df.iloc[1].text=='TEXT 2 – DAYDREAMING BACK IN TIME '
            assert test_df.iloc[2].text=='TEXT 3 – THIS IS YOUR TIME '
        elif year==2022:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT 1 – A YOUNG POET’S POWERFUL VOICE '
            assert test_df.iloc[1].text=='TEXT 2 – THE POWERFUL VOICE OF MUSIC  '
            assert test_df.iloc[2].text=='TEXT 3 – THE POWERFUL VOICE OF BOOKS '
        elif year==2023:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT 1 – BETWEEN TWO WORLDS: VILLAGE AND CITY '
            assert test_df.iloc[1].text=='TEXT 2 – BETWEEN TWO WORLDS: THROUGH WORDS AND PICTURES '
            assert test_df.iloc[2].text=='TEXT 3 – BETWEEN TWO WORLDS: HUMAN AND TECHNOLOGICAL '
        elif year==2024:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT 1 – FAMILY CONNECTIONS AND THE NATURAL WORLD '
            assert test_df.iloc[1].text=='TEXT 2 – FRIENDSHIP, THE HUMAN CONNECTION '
            assert test_df.iloc[2].text=='TEXT 3 – CONNECTING THROUGH TRAVEL '
        elif year==2025:
            assert len(test_df)==3
            assert test_df.iloc[0].text=='TEXT 1 – The Underdog Effect – Changing Perspectives '
            assert test_df.iloc[1].text=='TEXT 2 – The Perspective of a ‘Wise Old Counsellor’ '
            assert test_df.iloc[2].text=='TEXT 3 – Planet Earth from the Perspective of Space '


def test_identify_section_headers():
    for year in range(2001,2026):
        doc = open_exam(year,"english","al",1)
        width = doc[0].rect.width
        doc_df = get_doc_line_df(doc)
        doc_df = clean_line_df(doc_df)

        identify_section_headers(doc_df)
        test_df = doc_df[doc_df.section==1].copy()
        if year==2001:
            assert len(test_df)==4
            assert test_df.loc[31].text=='SECTION I'
            assert test_df.loc[32].text=='COMPREHENDING (100 marks)'
            assert test_df.loc[381].text=='SECTION II'
            assert test_df.loc[382].text=='COMPOSING (100 marks) '
        elif year==2002:
            assert len(test_df)==4
            assert test_df.loc[23].text=='SECTION I '
            assert test_df.loc[24].text=='COMPREHENDING (100 marks) '
            assert test_df.loc[290].text=='SECTION II '
            assert test_df.loc[291].text=='COMPOSING (100 marks) '
        elif year==2003:
            assert len(test_df)==4
            assert test_df.loc[24].text=='SECTION I'
            assert test_df.loc[25].text=='COMPREHENDING (100 marks)'
            assert test_df.loc[340].text=='SECTION II'
            assert test_df.loc[341].text=='COMPOSING (100 marks)'
        elif year==2004:
            assert len(test_df)==4
            assert test_df.loc[24].text=='SECTION I '
            assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
            assert test_df.loc[369].text=='SECTION II '
            assert test_df.loc[370].text=='COMPOSING (100 marks) '
        elif year==2005:
            assert len(test_df)==4
            assert test_df.loc[24].text=='SECTION I '
            assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
            assert test_df.loc[422].text=='SECTION II '
            assert test_df.loc[423].text=='COMPOSING (100 marks) '
        elif year==2006:
            assert len(test_df)==4
            assert test_df.loc[24].text=='SECTION I '
            assert test_df.loc[25].text=='COMPREHENDING (100 Marks) '
            assert test_df.loc[347].text=='SECTION II '
            assert test_df.loc[348].text=='COMPOSING (100 marks) '
        elif year==2007:
            assert len(test_df)==4
            assert test_df.loc[24].text=='SECTION I '
            assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
            assert test_df.loc[324].text=='SECTION II '
            assert test_df.loc[325].text=='COMPOSING (100 marks) '
        elif year==2008:
            assert len(test_df)==4
            assert test_df.loc[24].text=='SECTION 1 '
            assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
            assert test_df.loc[317].text=='SECTION II '
            assert test_df.loc[318].text=='COMPOSING (100 marks) '
        elif year==2009:
            assert len(test_df)==4
            assert test_df.loc[24].text=='SECTION I '
            assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
            assert test_df.loc[415].text=='SECTION II '
            assert test_df.loc[416].text=='COMPOSING (100 marks) '
        elif year==2010:
            assert len(test_df)==4
            assert test_df.loc[24].text=='SECTION 1 '
            assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
            assert test_df.loc[413].text=='SECTION II '
            assert test_df.loc[414].text=='COMPOSING (100 marks) '
        elif year==2011:
            assert len(test_df)==4
            assert test_df.loc[24].text=='SECTION 1 '
            assert test_df.loc[25].text==' COMPREHENDING (100 marks) '
            assert test_df.loc[412].text=='SECTION II '
            assert test_df.loc[413].text=='COMPOSING (100 marks) '
        elif year==2012:
            assert len(test_df)==2
            assert test_df.loc[24].text=='SECTION 1                     COMPREHENDING                      (100 marks) '
            assert test_df.loc[430].text=='SECTION II                            COMPOSING                          (100 marks) '
        elif year==2013:
            assert len(test_df)==2
            assert test_df.loc[24].text=='SECTION 1                       COMPREHENDING                        (100 marks) '
            assert test_df.loc[440].text=='SECTION II                            COMPOSING                        (100 marks) '
        elif year==2014:
            assert len(test_df)==2
            assert test_df.loc[24].text=='SECTION 1                        COMPREHENDING                       (100 marks) '
            assert test_df.loc[455].text=='SECTION II                            COMPOSING                        (100 marks) '
        elif year==2015:
            assert len(test_df)==2
            assert test_df.loc[24].text=='SECTION I                        COMPREHENDING                       (100 marks) '
            assert test_df.loc[463].text=='SECTION II                               COMPOSING                           (100 marks) '
        elif year==2016:
            assert len(test_df)==2
            assert test_df.loc[24].text=='SECTION 1                  COMPREHENDING               (100 marks) '
            assert test_df.loc[453].text=='SECTION II                               COMPOSING                           (100 marks) '
        elif year==2017:
            assert len(test_df)==2
            assert test_df.loc[25].text=='SECTION I                   COMPREHENDING               (100 marks) '
            assert test_df.loc[377].text=='SECTION II                           COMPOSING                    (100 marks) '
        elif year==2018:
            assert len(test_df)==2
            assert test_df.loc[24].text=='SECTION I                       COMPREHENDING                    (100 marks) '
            assert test_df.loc[347].text=='SECTION II                                COMPOSING                        (100 marks) '
        elif year==2019:
            assert len(test_df)==2
            assert test_df.loc[25].text=='SECTION I                       COMPREHENDING                    (100 marks) '
            assert test_df.loc[410].text=='SECTION II                                COMPOSING                        (100 marks) '
        elif year==2020:
            assert len(test_df)==2
            assert test_df.loc[24].text=='SECTION I                       COMPREHENDING                    (100 marks) '
            assert test_df.loc[375].text=='SECTION II                                COMPOSING                        (100 marks) '
        elif year==2021:
            assert len(test_df)==2
            assert test_df.loc[24].text=='SECTION I                       COMPREHENDING                    (40 marks) '
            assert test_df.loc[424].text=='SECTION II                                COMPOSING                        (100 marks) '
        elif year==2022:
            assert len(test_df)==2
            assert test_df.loc[35].text=='SECTION I                         COMPREHENDING                    (40 marks) '
            assert test_df.loc[461].text=='SECTION II                                COMPOSING                        (100 marks) '
        elif year==2023:
            assert len(test_df)==4
            assert test_df.loc[28].text=='SECTION I'
            assert test_df.loc[29].text=='COMPREHENDING'
            assert test_df.loc[30].text=='(100 marks) '
            assert test_df.loc[428].text=='SECTION II                                COMPOSING                         (100 marks) '
        elif year==2024:
            assert len(test_df)==2
            assert test_df.loc[24].text=='SECTION I                       COMPREHENDING                    (100 marks) '
            assert test_df.loc[462].text=='SECTION II                          COMPOSING                              (100 marks) '
        elif year==2025:
            assert len(test_df)==4
            assert test_df.loc[27].text=='SECTION I '
            assert test_df.loc[28].text=='COMPREHENDING '
            assert test_df.loc[29].text=='(100 marks) '
            assert test_df.loc[481].text=='SECTION II                          COMPOSING                        (100 marks) '


def load_expected(year: int, cat: str, subject: str, level: str, paper: int) -> list[str]:
    out_dir = Path(__file__).parent.resolve() / Path(f"resources/expected_{cat}s")
    path = out_dir/ f"{subject}_{level}_{paper}_{year}.txt"
    return path.read_text(encoding="utf-8").splitlines()

@pytest.mark.parametrize("year", range(2001, 2026))
def test_identify_text_subtitles(year):
    subject = "english"
    level   = "al"
    paper   = 1

    doc = open_exam(year, subject, level, paper)
    df = get_doc_line_df(doc)
    doc_width = doc[0].rect.width

    df = clean_line_df(df)
    identify_footers(df)
    identify_instructions(df)
    identify_section_headers(df)
    identify_text_headers(df, doc_width)
    identify_subtitles(df, doc_width)

    got = df[df.subtitle == 1].text.tolist()
    expected = load_expected(year, "subtitle",subject, level, paper)

    assert got == expected

    doc.close()


def test_identify_text_subtitles_old():
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
            assert len(test_df)==7  # Text three has no subtitles
        if year==2005:
            assert len(test_df)==9
            # These we will call subtile 2
            #assert test_df.loc[251].text=='World exclusive ! Irish Rock Diva speaks to readers from '   # if you incldue "starts_left" in conditions for subtitles this will not be captured.
            #assert test_df.loc[252].text=='her Italian villa. '
        if year==2007:
            assert len(test_df)==6  # Text 3 has no subtitles
        if year==2008:
            assert len(test_df)==6   # Text 3 is a big image, needs ocr
        if year==2019:
            assert len(test_df)==10
            assert test_df.iloc[0].text=='This\xa0edited\xa0piece\xa0is\xa0based\xa0on\xa0an\xa0article\xa0by\xa0Jeanette\xa0Winterson\xa0entitled,\xa0“What\xa0is\xa0Art\xa0for?”\xa0\xa0\xa0'
            assert test_df.iloc[1].text=='The\xa0writer\xa0uses\xa0the\xa0term\xa0“art”\xa0to\xa0include\xa0all\xa0artistic\xa0forms,\xa0e.g.\xa0painting,\xa0writing,\xa0music,\xa0etc.\xa0\xa0\xa0'
            assert test_df.iloc[2].text=='The\xa0original\xa0article\xa0appears\xa0on\xa0the\xa0writer’s\xa0website,\xa0jeanettewinterson.com.\xa0'
            assert test_df.iloc[3].text=='This\xa0text\xa0is\xa0composed\xa0of\xa0two\xa0elements.\xa0\xa0The\xa0first\xa0consists\xa0of\xa0a\xa0series\xa0of\xa0edited\xa0extracts\xa0from\xa0\xa0'
            assert test_df.iloc[4].text=='David\xa0Park’s\xa0novel,\xa0Travelling\xa0in\xa0a\xa0Strange\xa0Land.\xa0\xa0We\xa0meet\xa0the\xa0character\xa0Tom,\xa0a\xa0photographer,\xa0'
            assert test_df.iloc[5].text=='who\xa0is\xa0in\xa0a\xa0reflective\xa0mood\xa0as\xa0he\xa0undertakes\xa0a\xa0journey.\xa0\xa0The\xa0second\xa0is\xa0a\xa0photograph,\xa0taken\xa0from\xa0'
            assert test_df.iloc[6].text=='the\xa0Apollo\xa017\xa0spacecraft\xa0in\xa01972,\xa0that\xa0provided\xa0us\xa0with\xa0a\xa0startling\xa0new\xa0perspective\xa0on\xa0our\xa0world.\xa0'
            assert test_df.iloc[7].text=='The\xa0following\xa0text\xa0is\xa0adapted\xa0from\xa0Caitlin\xa0Moran’s\xa0essay,\xa0Libraries:\xa0Cathedrals\xa0of\xa0Our\xa0Souls.\xa0\xa0\xa0'
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
        if year==2025:                   # There is hidden text here. It will need to be removed by cross reference to ocr, or by another method.
            assert len(test_df)==12
            assert test_df.iloc[0].text=='This text is an edited article by David Robson entitled, ‘The Underdog’s Surprising Appeal’, '
            assert test_df.iloc[1].text=='published on 4th August 2024, in the BBC Essential newsletter.  It demonstrates how our '
            assert test_df.iloc[2].text=='perspectives can change with the “underdog effect”. '
            assert test_df.iloc[3].text=='TEXT 2 consists of a speech made by Margaret Atwood, author of The Handmaid’s Tale, at the One '
            assert test_df.iloc[4].text=='Young World Congress in Montreal in September 2024.  In her speech she gives advice to young '
            assert test_df.iloc[5].text=='people from the viewpoint of what she calls herself, “a wise old counsellor”. '
            assert test_df.iloc[6].text=='TEXT 3 consists of edited extracts from Samantha Harvey’s novel, Orbital, published in 2024.  It '
            assert test_df.iloc[7].text=='tells the story of six astronauts in a H-shaped spacecraft rotating above the earth.  They are there '
            assert test_df.iloc[8].text=='Text 3 consists of edited extracts from Samantha Harvey’s novel, Orbital, published in 2024. It tells '
            assert test_df.iloc[9].text=='to collect meteorological data and conduct scientific experiments.  But mostly they observe.   '
            assert test_df.iloc[10].text=='the story of six astronauts who rotate in a spacecraft above the earth. They are there to collect '
            assert test_df.iloc[11].text=='meteorological data and conduct scientific experiments. But mostly they observe. '

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
        test_df = df[df.subsubtitle==1].copy()
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
        

if __name__=="__main__":
    test_open_doc()
