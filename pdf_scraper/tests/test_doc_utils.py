from pdf_scraper.doc_utils import open_exam, get_images, get_doc_line_df, filter_images
from pdf_scraper.doc_utils import get_captions, identify_footers, identify_section_headers, identify_text_headers
from pdf_scraper.line_utils import clean_line_df
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


def test_identify_text_headers_length():
    for year in range(2001,2026):
        doc = open_exam(year,"english","al",1)
        width = doc[0].rect.width
        doc_df = get_doc_line_df(doc)
        doc_df = clean_line_df(doc_df)

        identify_section_headers(doc_df)
        identify_text_headers(doc_df, width)
        heads = doc_df[doc_df.title==1].copy()
        if year ==2001:
            assert len(heads)==8
        elif year >2001 and year <= 2004:
            assert len(heads)==6
        elif year == 2005:        
            assert len(heads)==6  
        elif year == 2006:        
            assert len(heads)==6
        elif year == 2007:        
            assert len(heads)==6
        elif year == 2008:        # This is 4 because text 3 is all image.
            assert len(heads)==4
        elif year == 2009:        # This year has lots of problems but this is the current behaviour
            assert len(heads)==7, f"Year {year}, {len(heads)} instead of 7"  
        elif year ==2010 or year == 2012 or year == 2014 or year == 2015:
            assert len(heads)==6
        elif year ==2011 or year == 2013:
            assert len(heads)==3
        elif year >2015 and year <= 2025:
            assert len(heads)==3


def test_identify_text_headers_content():
    for year in range(2001,2026):
        doc = open_exam(year,"english","al",1)
        width = doc[0].rect.width
        doc_df = get_doc_line_df(doc)
        doc_df = clean_line_df(doc_df)

        identify_section_headers(doc_df)
        identify_text_headers(doc_df, width)
        test_df = doc_df[doc_df.title==1].copy()
        if year==2001:
            assert test_df.loc[33].text=='TEXT 1'
            assert test_df.loc[34].text=='BEING IRISH'
            assert test_df.loc[158].text=='TEXT 2'
            assert test_df.loc[159].text=='A NEW IRELAND'
            assert test_df.loc[249].text=='TEXT 3'
            assert test_df.loc[250].text=='AN IRISH SENSE OF HUMOUR'
            assert test_df.loc[356].text=='TEXT 4'
            assert test_df.loc[357].text=='IMAGES OF IRELAND'
        elif year==2002:
            assert test_df.loc[25].text=='TEXT 1 '
            assert test_df.loc[26].text=='THE FAMILY OF MAN '
            assert test_df.loc[105].text=='TEXT 2 '
            assert test_df.loc[106].text=='FAMILY HOME FOR SALE '
            assert test_df.loc[191].text=='TEXT 3 '
            assert test_df.loc[192].text=='FAMILIES IN A TIME OF CRISIS '
        elif year==2003:
            assert test_df.loc[26].text=='TEXT 1'
            assert test_df.loc[27].text=='THE FIRST GREAT JOURNEY'
            assert test_df.loc[179].text=='TEXT 2'
            assert test_df.loc[180].text=='A STRANGE COMPANION'
            assert test_df.loc[316].text=='TEXT 3'
            assert test_df.loc[317].text=='DESTINATIONS'
        elif year==2004:
            assert test_df.loc[26].text=='TEXT 1 '
            assert test_df.loc[27].text=='THE IMPORTANCE OF PLAY '
            assert test_df.loc[144].text=='TEXT 2 '
            assert test_df.loc[145].text=='PAUL’S FIRST DAY AT WORK '
            assert test_df.loc[288].text=='TEXT 3 '
            assert test_df.loc[289].text=='WORK AND PLAY '
        elif year==2005:
            assert test_df.loc[26].text=='TEXT 1 '
            assert test_df.loc[27].text=='AN ORDINARY LIFE '
            assert test_df.loc[171].text=='TEXT 2 '
            assert test_df.loc[172].text=='ORDINARY LIVES IN WAR TIME '
            assert test_df.loc[246].text=='TEXT 3 '
            assert test_df.loc[247].text=='PUBLIC LIVES '
            #assert test_df.loc[251].text=='World exclusive ! Irish Rock Diva speaks to readers from '  # This is not correct but it is current behaviour
            #assert test_df.loc[252].text=='her Italian villa. '                                        # This is not correct but it is current behaviour
        elif year==2006:
            assert test_df.loc[26].text=='TEXT I '
            assert test_df.loc[27].text=='“WHAT SEEMS TO BE THE PROBLEM, LADY SARAH?” '
            assert test_df.loc[153].text=='TEXT 2 '
            assert test_df.loc[154].text=='GHOST WRITING    '
            assert test_df.loc[278].text=='TEXT 3 '
            assert test_df.loc[279].text=='PRETENCE '
        elif year==2007:
            assert test_df.loc[26].text=='TEXT 1 '
            assert test_df.loc[27].text=='FILMS TO CHANGE YOUR LIFE '
            assert test_df.loc[155].text=='TEXT 2 '
            assert test_df.loc[156].text=='LONDON, PAST AND PRESENT '
            assert test_df.loc[297].text=='TEXT 3 '
            assert test_df.loc[298].text=='FORCES FOR CHANGE? '
        elif year==2008:   # Text 3 is all image.
            assert test_df.loc[26].text=='TEXT 1 '
            assert test_df.loc[27].text=='TEENAGE IDENTITY '
            assert test_df.loc[166].text=='TEXT 2 '
            assert test_df.loc[167].text=='FALSE IDENTITY? '
        elif year==2009:
            assert test_df.loc[26].text=='TEXT 1 '
            assert test_df.loc[27].text=='Decisions for Society'
            #assert test_df.loc[30].text=='Should Zoos be Closed? '
            assert test_df.loc[173].text=='TEXT 2 '
            assert test_df.loc[174].text=='Personal Decisions '
            assert test_df.loc[323].text=='TEXT 3 '
            assert test_df.loc[324].text=='The Decisive Moment '
            assert test_df.loc[329].text=='Creating the Decisive Moment '   # This appears at the top of the second page of Text3, we can still call it a title.
        elif year==2010:
            assert test_df.loc[26].text=='TEXT 1 '
            assert test_df.loc[27].text=='A Personal Future '
            assert test_df.loc[156].text=='TEXT 2 '
            assert test_df.loc[157].text=='A Global Future'
            assert test_df.loc[286].text=='TEXT 3 '
            assert test_df.loc[287].text=='An Imagined Future '
        elif year==2011:
            assert test_df.loc[26].text=='TEXT 1'
            assert test_df.loc[149].text=='TEXT 2 '
            assert test_df.loc[267].text=='TEXT 3 '
        elif year==2012:
            assert test_df.loc[25].text=='TEXT 1 '
            assert test_df.loc[26].text=='Personal Memories  '
            assert test_df.loc[174].text=='TEXT 2 '
            assert test_df.loc[175].text=='Shared Memories  '
            assert test_df.loc[298].text=='TEXT 3 '
            assert test_df.loc[299].text=='A journey remembered and revisited  '
        elif year==2013:
            assert test_df.loc[25].text=='TEXT 1 '
            assert test_df.loc[161].text=='TEXT 2  '
            assert test_df.loc[288].text=='TEXT 3 '
        elif year==2014:
            assert test_df.loc[25].text=='TEXT 1'
            assert test_df.loc[26].text=='AN INFLUENTIAL EVENT '
            assert test_df.loc[167].text=='TEXT 2'
            assert test_df.loc[168].text=='CULTURAL INFLUENCES '
            assert test_df.loc[311].text=='TEXT 3'
            assert test_df.loc[312].text=='THE INFLUENCE OF THE PAST '
        elif year==2015:
            assert test_df.loc[25].text=='TEXT 1 '
            assert test_df.loc[26].text=='BECAUSE WE CAN, WE MUST '
            assert test_df.loc[176].text=='TEXT 2 '
            assert test_df.loc[177].text=='GHOSTS DON’T SHOW UP ON CCTV '
            assert test_df.loc[317].text=='TEXT 3 '
            assert test_df.loc[318].text=='A LIFE IN TIME '
        elif year==2016:
            assert test_df.loc[25].text=='TEXT 1 – A DRAMATIC JOURNEY '
            assert test_df.loc[115].text=='TEXT 2 – A PERSONAL JOURNEY '
            assert test_df.loc[278].text=='TEXT 3 – JOURNEY INTO SPACE '
        elif year==2017:
            assert test_df.loc[26].text=='TEXT\xa01\xa0–\xa0THE\xa0WORLD\xa0OF\xa0POETRY\xa0'
            assert test_df.loc[104].text=='TEXT\xa02\xa0–\xa0A\xa0CONNECTED\xa0WORLD\xa0\xa0'
            assert test_df.loc[235].text=='TEXT\xa03\xa0–\xa0THE\xa0WORLD\xa0OF\xa0CHILDHOOD\xa0'
        elif year==2018:
            assert test_df.loc[25].text=='TEXT\xa01\xa0–\xa0ADVICE\xa0TO\xa0YOUNG\xa0WRITERS\xa0'
            assert test_df.loc[165].text=='TEXT\xa02\xa0–\xa0A\xa0SUCCESSFUL\xa0YOUNG\xa0WRITER\xa0\xa0'
            assert test_df.loc[306].text=='TEXT\xa03\xa0–\xa0A\xa0TRAGIC\xa0YOUNG\xa0POET\xa0'
        elif year==2019:
            assert test_df.loc[26].text=='TEXT\xa01\xa0–\xa0WHAT\xa0IS\xa0ART\xa0FOR?\xa0'
            assert test_df.loc[162].text=='TEXT\xa02\xa0–\xa0A\xa0PHOTOGRAPHER’S\xa0PERSPECTIVE\xa0'
            assert test_df.loc[276].text=='TEXT\xa03\xa0–\xa0LIBRARIES:\xa0CATHEDRALS\xa0OF\xa0OUR\xa0SOULS\xa0'
        elif year==2020:
            assert test_df.loc[25].text=='TEXT 1 – FROM GENRE to GENRE '
            assert test_df.loc[137].text=='TEXT 2 – DETECTIVE FICTION '
            assert test_df.loc[266].text=='TEXT 3 – SCIENCE FICTION (SCI-FI) '
        elif year==2021:
            assert test_df.loc[25].text=='TEXT 1 – TIME PIECES   '
            assert test_df.loc[158].text=='TEXT 2 – DAYDREAMING BACK IN TIME '
            assert test_df.loc[289].text=='TEXT 3 – THIS IS YOUR TIME '
        elif year==2022:
            assert test_df.loc[36].text=='TEXT 1 – A YOUNG POET’S POWERFUL VOICE '
            assert test_df.loc[185].text=='TEXT 2 – THE POWERFUL VOICE OF MUSIC  '
            assert test_df.loc[321].text=='TEXT 3 – THE POWERFUL VOICE OF BOOKS '
        elif year==2023:
            assert test_df.loc[31].text=='TEXT 1 – BETWEEN TWO WORLDS: VILLAGE AND CITY '
            assert test_df.loc[167].text=='TEXT 2 – BETWEEN TWO WORLDS: THROUGH WORDS AND PICTURES '
            assert test_df.loc[284].text=='TEXT 3 – BETWEEN TWO WORLDS: HUMAN AND TECHNOLOGICAL '
        elif year==2024:
            assert test_df.loc[25].text=='TEXT 1 – FAMILY CONNECTIONS AND THE NATURAL WORLD '
            assert test_df.loc[160].text=='TEXT 2 – FRIENDSHIP, THE HUMAN CONNECTION '
            assert test_df.loc[313].text=='TEXT 3 – CONNECTING THROUGH TRAVEL '
        elif year==2025:
            assert test_df.loc[30].text=='TEXT 1 – The Underdog Effect – Changing Perspectives '
            assert test_df.loc[180].text=='TEXT 2 – The Perspective of a ‘Wise Old Counsellor’ '
            assert test_df.loc[332].text=='TEXT 3 – Planet Earth from the Perspective of Space '


def test_identify_section_headers_content():
    for year in range(2001,2026):
        doc = open_exam(year,"english","al",1)
        width = doc[0].rect.width
        doc_df = get_doc_line_df(doc)
        doc_df = clean_line_df(doc_df)

        identify_section_headers(doc_df)
        test_df = doc_df[doc_df.section==1].copy()
    if year==2001:
        assert test_df.loc[31].text=='SECTION I'
        assert test_df.loc[32].text=='COMPREHENDING (100 marks)'
        assert test_df.loc[381].text=='SECTION II'
        assert test_df.loc[382].text=='COMPOSING (100 marks) '
    if year==2002:
        assert test_df.loc[23].text=='SECTION I '
        assert test_df.loc[24].text=='COMPREHENDING (100 marks) '
        assert test_df.loc[290].text=='SECTION II '
        assert test_df.loc[291].text=='COMPOSING (100 marks) '
    if year==2003:
        assert test_df.loc[24].text=='SECTION I'
        assert test_df.loc[25].text=='COMPREHENDING (100 marks)'
        assert test_df.loc[340].text=='SECTION II'
        assert test_df.loc[341].text=='COMPOSING (100 marks)'
    if year==2004:
        assert test_df.loc[24].text=='SECTION I '
        assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
        assert test_df.loc[369].text=='SECTION II '
        assert test_df.loc[370].text=='COMPOSING (100 marks) '
    if year==2005:
        assert test_df.loc[24].text=='SECTION I '
        assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
        assert test_df.loc[422].text=='SECTION II '
        assert test_df.loc[423].text=='COMPOSING (100 marks) '
    if year==2006:
        assert test_df.loc[24].text=='SECTION I '
        assert test_df.loc[25].text=='COMPREHENDING (100 Marks) '
        assert test_df.loc[347].text=='SECTION II '
        assert test_df.loc[348].text=='COMPOSING (100 marks) '
    if year==2007:
        assert test_df.loc[24].text=='SECTION I '
        assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
        assert test_df.loc[324].text=='SECTION II '
        assert test_df.loc[325].text=='COMPOSING (100 marks) '
    if year==2008:
        assert test_df.loc[24].text=='SECTION 1 '
        assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
        assert test_df.loc[317].text=='SECTION II '
        assert test_df.loc[318].text=='COMPOSING (100 marks) '
    if year==2009:
        assert test_df.loc[24].text=='SECTION I '
        assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
        assert test_df.loc[415].text=='SECTION II '
        assert test_df.loc[416].text=='COMPOSING (100 marks) '
    if year==2010:
        assert test_df.loc[24].text=='SECTION 1 '
        assert test_df.loc[25].text=='COMPREHENDING (100 marks) '
        assert test_df.loc[413].text=='SECTION II '
        assert test_df.loc[414].text=='COMPOSING (100 marks) '
    if year==2011:
        assert test_df.loc[24].text=='SECTION 1 '
        assert test_df.loc[25].text==' COMPREHENDING (100 marks) '
        assert test_df.loc[412].text=='SECTION II '
        assert test_df.loc[413].text=='COMPOSING (100 marks) '
    if year==2012:
        assert test_df.loc[24].text=='SECTION 1                     COMPREHENDING                      (100 marks) '
        assert test_df.loc[430].text=='SECTION II                            COMPOSING                          (100 marks) '
    if year==2013:
        assert test_df.loc[24].text=='SECTION 1                       COMPREHENDING                        (100 marks) '
        assert test_df.loc[440].text=='SECTION II                            COMPOSING                        (100 marks) '
    if year==2014:
        assert test_df.loc[24].text=='SECTION 1                        COMPREHENDING                       (100 marks) '
        assert test_df.loc[455].text=='SECTION II                            COMPOSING                        (100 marks) '
    if year==2015:
        assert test_df.loc[24].text=='SECTION I                        COMPREHENDING                       (100 marks) '
        assert test_df.loc[463].text=='SECTION II                               COMPOSING                           (100 marks) '
    if year==2016:
        assert test_df.loc[24].text=='SECTION 1                  COMPREHENDING               (100 marks) '
        assert test_df.loc[453].text=='SECTION II                               COMPOSING                           (100 marks) '
    if year==2017:
        assert test_df.loc[25].text=='SECTION I                   COMPREHENDING               (100 marks) '
        assert test_df.loc[377].text=='SECTION II                           COMPOSING                    (100 marks) '
    if year==2018:
        assert test_df.loc[24].text=='SECTION I                       COMPREHENDING                    (100 marks) '
        assert test_df.loc[347].text=='SECTION II                                COMPOSING                        (100 marks) '
    if year==2019:
        assert test_df.loc[25].text=='SECTION I                       COMPREHENDING                    (100 marks) '
        assert test_df.loc[410].text=='SECTION II                                COMPOSING                        (100 marks) '
    if year==2020:
        assert test_df.loc[24].text=='SECTION I                       COMPREHENDING                    (100 marks) '
        assert test_df.loc[375].text=='SECTION II                                COMPOSING                        (100 marks) '
    if year==2021:
        assert test_df.loc[24].text=='SECTION I                       COMPREHENDING                    (40 marks) '
        assert test_df.loc[424].text=='SECTION II                                COMPOSING                        (100 marks) '
    if year==2022:
        assert test_df.loc[35].text=='SECTION I                         COMPREHENDING                    (40 marks) '
        assert test_df.loc[461].text=='SECTION II                                COMPOSING                        (100 marks) '
    if year==2023:
        assert test_df.loc[28].text=='SECTION I'
        assert test_df.loc[29].text=='COMPREHENDING'
        assert test_df.loc[30].text=='(100 marks) '
        assert test_df.loc[428].text=='SECTION II                                COMPOSING                         (100 marks) '
    if year==2024:
        assert test_df.loc[24].text=='SECTION I                       COMPREHENDING                    (100 marks) '
        assert test_df.loc[462].text=='SECTION II                          COMPOSING                              (100 marks) '
    if year==2025:
        assert test_df.loc[27].text=='SECTION I '
        assert test_df.loc[28].text=='COMPREHENDING '
        assert test_df.loc[29].text=='(100 marks) '
        assert test_df.loc[481].text=='SECTION II                          COMPOSING                        (100 marks) '




if __name__=="__main__":
    test_open_doc()
