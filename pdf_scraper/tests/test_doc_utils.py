from pdf_scraper.doc_utils import open_exam, get_images, get_doc_line_df, filter_images
from pdf_scraper.doc_utils import get_captions, identify_footers, identify_section_headers, identify_text_headers
from pdf_scraper.doc_utils import identify_instructions, identify_subtitles, identify_subsubtitles
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


def test_identify_text_subtitles():
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
        if year==2001:
            assert len(test_df)==9
            assert test_df.iloc[0].text=='The following extracts are adapted from the book, Being Irish, in which a number of contributors'
            assert test_df.iloc[1].text=='give their responses to the question ‘What does it mean to be Irish today?’ The book was'
            assert test_df.iloc[2].text=='published in 2000, and its editor is Paddy Logue.'
            assert test_df.iloc[3].text=='The following text is adapted from the inauguration speech of President Mary Robinson, the'
            assert test_df.iloc[4].text=='ﬁrst woman to hold the office of President of Ireland. The speech was delivered on December'
            assert test_df.iloc[5].text=='3rd, 1990.'
            assert test_df.iloc[6].text=='The following text is a narrative (in abridged form) taken from the poet Ciaran Carson’s book'
            assert test_df.iloc[7].text=='The Star Factory which tells the story of Ulster and its people. The author tells us he received'
            assert test_df.iloc[8].text=='this story from his father. The book was ﬁrst published in 1997.'
        if year==2002:
            assert len(test_df)==10
            assert test_df.iloc[0].text=='The following text consists of a written and a visual element.  The written part of this text is adapted  '
            assert test_df.iloc[1].text=='from  a  preface  by  the  American poet,  Carl  Sandburg,  to a collection of photographs entitled The '
            assert test_df.iloc[2].text=='Family of Man.  The  visual  images  are  taken from the  exhibition which  was  first  shown  in  the '
            assert test_df.iloc[3].text=='Museum of Modern Art, New York, in 1955. '
            assert test_df.iloc[4].text=='Novelist, Penelope Lively, remembers her family home through the wealth of little things it contained.  '
            assert test_df.iloc[5].text=='This article was published in The Sunday Times of August 26, 2001. '
            assert test_df.iloc[6].text=='This text is an extract from the novel, The Grapes of Wrath, by the American writer, John Steinbeck.  '
            assert test_df.iloc[7].text=='The novel tells the story of poor farming families who are forced to travel hundreds of miles across '
            assert test_df.iloc[8].text=='America in search of a living.  In this extract we learn how the desire of families to support one '
            assert test_df.iloc[9].text=='another leads to the setting up of a society in itself.  The novel was first published in 1939. '
        if year==2003:
            assert len(test_df)==7  # Text three has no subtitles
            assert test_df.iloc[0].text=='The following is an extract from The Jason Voyage in which the author, Tim Severin, sets out to test'
            assert test_df.iloc[1].text=='whether the legendary journey of Jason’s search for the Golden Fleece could have happened in fact.'
            assert test_df.iloc[2].text=='The book was published in 1985.'
            assert test_df.iloc[3].text=='This extract is adapted from The Golden Horde, Travels from the Himalaya to Karpathos,'
            assert test_df.iloc[4].text=='published in 1997, in which sixty-five year old Sheila Paine describes her travels through some of'
            assert test_df.iloc[5].text=='the turbulent territories of the former Soviet Union.  The extract begins at the point when Sheila'
            assert test_df.iloc[6].text=='returns to Saratov station to try once again to buy a ticket for a train journey.'
        if year==2004:
            assert len(test_df)==11
            assert test_df.iloc[0].text=='The following text is adapted from the writings of Vivian Paley, a teacher who has written over '
            assert test_df.iloc[1].text=='many years about the importance of play in the lives of small children. Paley’s books include '
            assert test_df.iloc[2].text=='descriptions of how children play and the stories they tell.  The extracts used in this text are '
            assert test_df.iloc[3].text=='taken from her books, The Boy Who Would Be a Helicopter (1990) and You Can’t Say You '
            assert test_df.iloc[4].text=='Can’t Play (1992). '
            assert test_df.iloc[5].text=='The following text is adapted from the novel, Sons and Lovers, by D.H. Lawrence, which tells '
            assert test_df.iloc[6].text=='the story of Paul Morel who, in this extract, begins work at Thomas Jordan & Son— suppliers of '
            assert test_df.iloc[7].text=='elasticated stockings. The novel was first published in 1913. '
            assert test_df.iloc[8].text=='The following text consists of a written and a visual element. The visual part of the text is a '
            assert test_df.iloc[9].text=='selection of images of people at work. The written element is an extract from a magazine article on '
            assert test_df.iloc[10].text=='the topic, Work and Play. '
        if year==2005:
            assert len(test_df)==9
            assert test_df.iloc[0].text=='Margaret Forster writes about her grandmother, Margaret Ann Hind, a domestic servant in '
            assert test_df.iloc[1].text=='Carlisle, a town in the north of England, in the 1890s. Her book is called Hidden Lives – A '
            assert test_df.iloc[2].text=='Family Memoir. '
            assert test_df.iloc[3].text=='The following text consists of a written and visual element. The written text is adapted from an '
            assert test_df.iloc[4].text=='introduction by documentary photographer, Jenny Matthews, to her book of photographs entitled '
            assert test_df.iloc[5].text=='Women and War. '
            assert test_df.iloc[6].text=='Some people’s lives seem far from ordinary. Modelled on articles from a number of celebrity '
            assert test_df.iloc[7].text=='magazines, the text below was written by a Leaving Certificate student. It offers a glimpse into the '
            assert test_df.iloc[8].text=='lifestyle of imaginary rock star, Eva Maguire. '
            # These we will call subtile 2
            #assert test_df.loc[251].text=='World exclusive ! Irish Rock Diva speaks to readers from '   # if you incldue "starts_left" in conditions for subtitles this will not be captured.
            #assert test_df.loc[252].text=='her Italian villa. '
        if year==2006:
            assert len(test_df)==8 
            assert test_df.iloc[0].text=='In this extract (adapted from A Border Station, by Shane Connaughton) a father and son are '
            assert test_df.iloc[1].text=='cutting down a tree.  The father, a garda sergeant, has been given permission by Lady Sarah, a '
            assert test_df.iloc[2].text=='member of the landed gentry, to cut down a small tree on her lands.  However, he decides to '
            assert test_df.iloc[3].text=='ignore her wishes and cut down a magnificent beech tree on the avenue leading to the Great '
            assert test_df.iloc[4].text=='House.  We join the story as the tree falls…  '
            assert test_df.iloc[5].text=='Jan Stevens is a ghost writer; that is, someone who writes books that are published as the work of '
            assert test_df.iloc[6].text=='someone else. '
            assert test_df.iloc[7].text=='The following text consists of a visual and a written element. '
        if year==2007:
            assert len(test_df)==6  # Text 3 has no subtitles
            assert test_df.iloc[0].text=='The following text is based on extracts from the recent publication, “1000 Films to Change your '
            assert test_df.iloc[1].text=='Life”, edited by Simon Cropper.  '
            assert test_df.iloc[2].text=='In 1930, wandering through London for a series of magazine articles, Virginia Woolf found a '
            assert test_df.iloc[3].text=='city alive with bustling activity and excitement.  Here, novelist Monica Ali takes a 21st century '
            assert test_df.iloc[4].text=='stroll in Woolf’s footsteps – and seventy-five years later finds London humming to a different '
            assert test_df.iloc[5].text=='tune.  '
        if year==2008:
            assert len(test_df)==6   # Text 3 is a big image, needs ocr
            assert test_df.iloc[0].text=='This text is adapted from Jon Savage’s book, “Teenage, the Creation of Youth, 1875 – 1945”,  '
            assert test_df.iloc[1].text=='in which he traces the history of the modern teenager. '
            assert test_df.iloc[2].text=='This text is taken from Clare Kilroy’s novel, “Tenderwire”, narrated in the voice of Eva  '
            assert test_df.iloc[3].text=='Tyne, an Irish violinist living and working in New York. The story involves Alexander who '
            assert test_df.iloc[4].text=='has offered Eva the opportunity to buy a rare violin, a Stradivarius, at a fraction of its market '
            assert test_df.iloc[5].text=='value. However, this violin comes without documents of identity or rightful ownership. '
        if year==2009:
            assert len(test_df)==9
            assert test_df.iloc[0].text=='This text is taken from Head to Head, a series of public debates, published in April 2008 in The '
            assert test_df.iloc[1].text=='Irish Times; it consists of two extracts in response to the question:  '
            assert test_df.iloc[2].text=='Should Zoos be Closed? '
            assert test_df.iloc[3].text=='This text is taken from a short story by Australian writer David Malouf entitled The Valley of '
            assert test_df.iloc[4].text=='Lagoons. In this extract, a bookish young teenager longs to join his mates on a hunting trip to '
            assert test_df.iloc[5].text=='the mysterious Valley of Lagoons. The story is set in Brisbane, Australia. '
            assert test_df.iloc[6].text=='The following text consists of a visual and written element. The visual part is a selection of '
            assert test_df.iloc[7].text=='photographs by Henri Cartier-Bresson. The written element is an extract from an essay entitled '
            assert test_df.iloc[8].text=='“Creating the Decisive Moment” by Frank Van Riper.   '
        if year==2010:
            assert len(test_df)==10
            assert test_df.iloc[0].text=='This text is a short extract adapted from Stepping Stones: Interviews with Seamus Heaney by '
            assert test_df.iloc[1].text=='Dennis O’Driscoll in which Heaney reflects on the impact of his childhood on his future life as '
            assert test_df.iloc[2].text=='a poet.  '
            assert test_df.iloc[3].text=='This text is adapted from Al Gore’s Nobel Prize Acceptance Speech delivered in Norway in '
            assert test_df.iloc[4].text=='2007. '
            assert test_df.iloc[5].text=='Ray Bradbury’s science fiction novel, Fahrenheit 451, describes a '
            assert test_df.iloc[6].text=='future in which books, considered to be the source of all unhappiness, '
            assert test_df.iloc[7].text=='are forbidden.  In this extract adapted from the novel, Guy Montag, a'
            assert test_df.iloc[8].text=='professional book-burner, has an unusual encounter with a young '
            assert test_df.iloc[9].text=='woman, Clarisse McClellan. '
        if year==2011:
            assert len(test_df)==12
            assert test_df.iloc[0].text=='This text is taken from An Irishwoman’s Diary by journalist, Lara Marlowe. She was Irish Times '
            assert test_df.iloc[1].text=='correspondent in Beirut and Paris, and is now based in Washington. Here she responds to an '
            assert test_df.iloc[2].text=='article critical of cats written by her friend and fellow journalist, Rosita Boland. '
            assert test_df.iloc[3].text=='This edited extract is adapted from Colum McCann’s award-winning novel Let The Great World '
            assert test_df.iloc[4].text=='Spin.  The novel’s opening is based on the true story of Philippe Petit’s tight-rope walk between '
            assert test_df.iloc[5].text=='the twin towers of the World Trade Centre in New York on August 8th 1974.  The extract '
            assert test_df.iloc[6].text=='captures the mysterious presence of the tight-rope walker high above the city. '
            assert test_df.iloc[7].text=='This text is adapted from a short story,  '
            assert test_df.iloc[8].text=='The Wintersongs, in Kevin Barry’s award-winning  '
            assert test_df.iloc[9].text=='collection, There are Little Kingdoms.  In this extract  '
            assert test_df.iloc[10].text=='an old woman has a mysterious insight into the life  '
            assert test_df.iloc[11].text=='of a young girl, Sarah, whom she meets on a train.  '
        if year==2012:
            assert len(test_df)==13
            assert test_df.iloc[0].text=='This edited extract is adapted from “Where the World Began” by Canadian writer, Margaret '
            assert test_df.iloc[1].text=='Laurence, in which she remembers and reflects on the small prairie town where she grew up.  '
            assert test_df.iloc[2].text=='This text has been adapted from the original, for the purpose of assessment, without the '
            assert test_df.iloc[3].text=='author’s prior consent. '
            assert test_df.iloc[4].text=='This text consists of an edited extract from a speech, delivered by former President Mary '
            assert test_df.iloc[5].text=='Robinson to an international conference on hunger.  In it she considers the commemoration of the '
            assert test_df.iloc[6].text=='Irish famine of 1845 and explores how society’s memory of the past, our collective social memory, '
            assert test_df.iloc[7].text=='shapes our response to contemporary issues.  This text has been adapted from the original, for the '
            assert test_df.iloc[8].text=='purpose of assessment, without the author’s prior consent. '
            assert test_df.iloc[9].text=='This text is adapted from Paul Theroux’s book entitled Ghost Train to the Eastern Star. In this '
            assert test_df.iloc[10].text=='edited extract he describes travelling like a “ghost” through his own memories as he revisits '
            assert test_df.iloc[11].text=='places he had experienced earlier in his life.  This text has been adapted from the original, for the '
            assert test_df.iloc[12].text=='purpose of assessment, without the author’s prior consent. '
        if year==2013:
            assert len(test_df)==7 
            assert test_df.iloc[0].text=='This edited text is based on an article, entitled, Tune in Next Week – The Curious Staying Power of '
            assert test_df.iloc[1].text=='the Cliff-hanger.  It was written by Emily Nussbaum for The New Yorker magazine.  '
            assert test_df.iloc[2].text=='This edited text is based on an interview with Irish writer, William Trevor, on The Art of Fiction, '
            assert test_df.iloc[3].text=='conducted for the Paris Review by Mira Stout.   '
            assert test_df.iloc[4].text=='This edited text is based on an article from The Irish Times by Belinda McKeon entitled: “New '
            assert test_df.iloc[5].text=='York Stories on a Perfect Platform”.  It celebrates the hundredth anniversary of the opening of '
            assert test_df.iloc[6].text=='New York’s Grand Central Station.  '
        if year==2014:
            assert len(test_df)==11
            assert test_df.iloc[0].text=='In the novel, Canada, Richard Ford tells how a bank robbery committed by Bev and Neeva '
            assert test_df.iloc[1].text=='Parsons influenced the lives of their children, Dell and his twin sister, Berner, who were fifteen '
            assert test_df.iloc[2].text=='years old at the time of the crime.  In this edited extract Dell remembers his escape to Canada '
            assert test_df.iloc[3].text=='with his mother’s friend, Mildred Remlinger.'
            assert test_df.iloc[4].text=='At an event entitled The Joy of Influence, organised by Andrew O’Hagan, six writers were asked '
            assert test_df.iloc[5].text=='to talk about an art-form, other than literature, that influenced them. This edited text, adapted '
            assert test_df.iloc[6].text=='from The Guardian newspaper, is based on the contributions of two writers, Alan Warner and '
            assert test_df.iloc[7].text=='John Lanchester.   '
            assert test_df.iloc[8].text=='Seamus Heaney is best remembered as a poet but he also enjoyed a distinguished career as an '
            assert test_df.iloc[9].text=='academic.  This edited text is based on an essay by Heaney entitled The Sense of the Past.  It '
            assert test_df.iloc[10].text=='appeared in the journal History Ireland.  In it he reflects on the influence of the past on our lives.  '
        if year==2015:
            assert len(test_df)==7
            assert test_df.iloc[0].text=='This edited text is based on a speech delivered by U2 front man and well-known humanitarian, '
            assert test_df.iloc[1].text=='Bono, to students graduating from the University of Pennsylvania. '
            assert test_df.iloc[2].text=='This edited text is based on an article which appeared in the Review Section of The Guardian '
            assert test_df.iloc[3].text=='newspaper in July, 2014.  In this article, author Joanna Briscoe discusses the challenges faced by '
            assert test_df.iloc[4].text=='writers of ghost literature in an age of reason. '
            assert test_df.iloc[5].text=='This edited text is based on Ammonites and Leaping Fish, a memoir by award-winning novelist, '
            assert test_df.iloc[6].text=='Penelope Lively.  In the text she reflects on youth and age and explores the challenges of ageing. '
        if year==2016:
            assert len(test_df)==9
            assert test_df.iloc[0].text=='This text consists of both visual images and an edited written extract.  The written text is adapted '
            assert test_df.iloc[1].text=='from Andrew Dickson’s book, Worlds Elsewhere – Journeys Around Shakespeare’s Globe. '
            assert test_df.iloc[2].text=='The following edited extract is adapted from Sara Baume’s award-winning debut novel, spill '
            assert test_df.iloc[3].text=='simmer falter wither.  Ray, the middle-aged, reclusive narrator and his beloved dog, One Eye, are '
            assert test_df.iloc[4].text=='on the run from the authorities.  One Eye attacked another dog and its owner and Ray fears his '
            assert test_df.iloc[5].text=='dog may be impounded.  In the extract below, Ray is talking to One Eye. '
            assert test_df.iloc[6].text=='This edited text is adapted from a speech delivered by President Barack Obama at the National '
            assert test_df.iloc[7].text=='Aeronautics and Space Administration (NASA), Kennedy Space Centre in Florida.  In this '
            assert test_df.iloc[8].text=='extract he acknowledges the history, and outlines the  future, of American space exploration.  '
        if year==2017:
            assert len(test_df)==8
            assert test_df.iloc[0].text=='This\xa0text\xa0is\xa0based\xa0on\xa0two\xa0images\xa0that\xa0incorporate\xa0work\xa0by\xa0the\xa0poet\xa0Robert\xa0Montgomery,\xa0and\xa0The\xa0'
            assert test_df.iloc[1].text=='Medium\xa0is\xa0the\xa0Message\xa0–\xa0The\xa0Power\xa0of\xa0Public\xa0Poetry,\xa0an\xa0edited\xa0article\xa0from\xa0The\xa0Guardian\xa0newspaper,\xa0'
            assert test_df.iloc[2].text=='written\xa0by\xa0Marta\xa0Bausells.\xa0\xa0The\xa0images\xa0are\xa0from\xa0the\xa0website\xa0robertmontgomery.org.\xa0'
            assert test_df.iloc[3].text=='This\xa0text\xa0is\xa0based\xa0on\xa0edited\xa0extracts\xa0from\xa0Free\xa0Speech\xa0–\xa0Ten\xa0Principles\xa0for\xa0a\xa0Connected\xa0World\xa0by\xa0Oxford\xa0'
            assert test_df.iloc[4].text=='Professor,\xa0Timothy\xa0Garton\xa0Ash.\xa0\xa0Professor\xa0Garton\xa0Ash\xa0writes\xa0about\xa0free\xa0speech,\xa0also\xa0termed\xa0“freedom\xa0'
            assert test_df.iloc[5].text=='of\xa0expression”,\xa0in\xa0the\xa0digital\xa0global\xa0city\xa0or\xa0“virtual\xa0cosmopolis”\xa0which\xa0we\xa0all\xa0now\xa0inhabit.\xa0'
            assert test_df.iloc[6].text=='This\xa0 edited\xa0 text\xa0 is\xa0 adapted\xa0 from\xa0 a\xa0 memoir\xa0 entitled\xa0 Report\xa0 from\xa0 the\xa0 Interior\xa0 by\xa0 American\xa0 writer\xa0\xa0'
            assert test_df.iloc[7].text=='Paul\xa0Auster.\xa0\xa0In\xa0this\xa0extract\xa0he\xa0focuses\xa0on\xa0the\xa0world\xa0of\xa0childhood.\xa0'
        if year==2018:
            assert len(test_df)==7
            assert test_df.iloc[0].text=='Award‐winning\xa0writer,\xa0Colum\xa0McCann,\xa0teaches\xa0creative\xa0writing\xa0in\xa0Hunter\xa0College,\xa0New\xa0York.\xa0\xa0\xa0'
            assert test_df.iloc[1].text=='This\xa0text\xa0is\xa0based\xa0on\xa0edited\xa0extracts\xa0from\xa0Colum\xa0McCann’s\xa0book,\xa0Letters\xa0to\xa0a\xa0Young\xa0Writer.\xa0'
            assert test_df.iloc[2].text=='This\xa0text\xa0is\xa0based\xa0on\xa0edited\xa0extracts\xa0from\xa0Fiona\xa0Mozley’s\xa0debut\xa0novel,\xa0Elmet.\xa0\xa0Fiona\xa0Mozley\xa0was\xa0'
            assert test_df.iloc[3].text=='the\xa0youngest\xa0writer\xa0nominated\xa0for\xa0the\xa0Man\xa0Booker\xa0Prize\xa0in\xa02017.\xa0\xa0\xa0\xa0\xa0'
            assert test_df.iloc[4].text=='TEXT\xa03\xa0is\xa0adapted\xa0from\xa0Above\xa0the\xa0Dreamless\xa0Dead,\xa0a\xa0collection\xa0of\xa0illustrated\xa0songs\xa0and\xa0poems\xa0from\xa0'
            assert test_df.iloc[5].text=='World\xa0War\xa01.\xa0\xa0The\xa0poetic\xa0extract\xa0which\xa0forms\xa0part\xa0of\xa0the\xa0text\xa0is\xa0from\xa0“Dead\xa0Man’s\xa0Dump”,\xa0a\xa0poem\xa0by\xa0'
            assert test_df.iloc[6].text=='Isaac\xa0Rosenberg,\xa0a\xa0young\xa0poet\xa0killed\xa0in\xa0action\xa0in\xa01918.\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0'
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
        if year==2020:
            assert len(test_df)==7
            assert test_df.iloc[0].text=='This text consists of two elements: firstly, edited extracts adapted from Alan McMonagle’s essay, '
            assert test_df.iloc[1].text=='The Misadventures of a Dithering Writer in Thirteen and A Half Fragments, in which he discusses '
            assert test_df.iloc[2].text=='writing in different genres.  The second element is a genre-related cartoon by Tom Gauld. '
            assert test_df.iloc[3].text=='This text is based on edited extracts adapted from Sherlock Holmes and the Adventure of the '
            assert test_df.iloc[4].text=='Blue Carbuncle, a short story by Arthur Conan Doyle, originally published in 1892. '
            assert test_df.iloc[5].text=='Text 3 consists of two elements: edited extracts adapted from Becky Chambers’ recent science '
            assert test_df.iloc[6].text=='fiction novella, To be Taught, if Fortunate, and a sci-fi magazine cover from the 1950s. '
        if year==2021:
            assert len(test_df)==8
            assert test_df.iloc[0].text=='Text 1 is based on edited extracts from Time Pieces – A Dublin Memoir by John Banville.  In this '
            assert test_df.iloc[1].text=='text the writer reflects on some childhood memories and shares his thoughts on the past. '
            assert test_df.iloc[2].text=='This text is adapted from poet Doireann Ní Ghríofa’s award-winning prose debut, A Ghost in the '
            assert test_df.iloc[3].text=='Throat.  In this edited extract the writer reflects on how the past and the present come together   '
            assert test_df.iloc[4].text=='in her garden.   '
            assert test_df.iloc[5].text=='TEXT 3 is based on edited extracts from the transcript of a graduation speech delivered in 2018 '
            assert test_df.iloc[6].text=='by American actor, Chadwick Boseman, at Howard University.  In this text Mr Boseman reflects '
            assert test_df.iloc[7].text=='on the time he spent at Howard and how it influenced him. '
        if year==2022:
            assert len(test_df)==9
            assert test_df.iloc[0].text=='This text is adapted from a feature article by Meadhbh McGrath entitled, Poet. Fashion icon. '
            assert test_df.iloc[1].text=='Future president?.  It originally appeared in the magazine section of a weekend newspaper.  '
            assert test_df.iloc[2].text=='This text is based on edited extracts from a book compiled by Tom Gatti entitled, Long Players. '
            assert test_df.iloc[3].text=='The book is a collection of personal essays in which writers share their thoughts on the albums '
            assert test_df.iloc[4].text=='that helped to shape them.  Extract Two features Man Booker prize winner, Nigerian, Ben Okri.  '
            assert test_df.iloc[5].text=='TEXT 3 is based on edited extracts from Hugo Hamilton’s novel, The Pages.  Hamilton uses a '
            assert test_df.iloc[6].text=='book – the novel, Rebellion, by Jewish writer Joseph Roth – as the narrator.  In these extracts, '
            assert test_df.iloc[7].text=='we witness the book telling its own story, including its rescue from the Nazi book burning in '
            assert test_df.iloc[8].text=='1933. '
            # assert test_df.loc[189].text=='Extract 1: Tom Gatti from the introduction to '  # These are "column titles"
            # assert test_df.loc[190].text=='his book, Long Players. '
        if year==2023:
            assert len(test_df)==12
            assert test_df.iloc[0].text=='This text is based on an edited extract from Gravel Heart, a novel by Abdulrazak Gurnah, 2021 '
            assert test_df.iloc[1].text=='Nobel Prize winner for literature.  In this extract Salim, from a small island village in Zanzibar, '
            assert test_df.iloc[2].text=='comes to stay with his uncle in London to further his education.  He doesn’t know how to belong '
            assert test_df.iloc[3].text=='in this strange city and feels cut off from the world he has left behind.'
            assert test_df.iloc[4].text=='Text 2 consists of two elements.  The first is an edited text by Henry Eliot entitled, This Must be the '
            assert test_df.iloc[5].text=='Place which focuses on literary locations.  The second is an iconic photograph, taken in 1907 and '
            assert test_df.iloc[6].text=='published in Time magazine’s 100 most influential, historical pictures.  Both elements illustrate '
            assert test_df.iloc[7].text=='how we can experience different worlds through words and pictures.    '
            assert test_df.iloc[8].text=='TEXT 3 consists of two edited articles on the subject of Artificial Intelligence (AI) published in '
            assert test_df.iloc[9].text=='July 2022: an introduction from Patricia Scanlon, Ireland’s first Artificial Intelligence '
            assert test_df.iloc[10].text=='Ambassador, published in The Irish Times and a feature by Ben Spencer printed in The Sunday '
            assert test_df.iloc[11].text=='Times magazine entitled, “I’m better than the Bard.”   '
            #assert test_df.loc[289].text=='Patricia Scanlon: ' # Shouldn't be there.
            #assert test_df.loc[290].text=='Ben Spencer: '      # Shouldn't be there.
        if year==2024:
            assert len(test_df)==8
            assert test_df.iloc[0].text=='This text is an edited article from The Irish Times, by Fintan O’Toole entitled, ‘We have taken '
            assert test_df.iloc[1].text=='flight from our deep link with birds.’  It was published in January 2023. '
            assert test_df.iloc[2].text=='TEXT 2 is an edited extract from the opening of Paul Murray’s novel, The Bee Sting, shortlisted '
            assert test_df.iloc[3].text=='for the 2023 Booker Prize.  The novel tells the tragi-comic story of the Barnes family, set in '
            assert test_df.iloc[4].text=='contemporary Ireland.  In this extract we meet the teenage daughter, Cass, and her best friend, '
            assert test_df.iloc[5].text=='Elaine. '
            assert test_df.iloc[6].text=='TEXT 3 is an edited article from the travel section of the Financial Times by Monisha Rajesh, '
            assert test_df.iloc[7].text=='journalist and travel writer, entitled To Istanbul by Train.  It was published in March 2023. '
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
    
        df = clean_line_df(df)
        identify_footers(df)
        identify_instructions(df)
        identify_section_headers(df)
        identify_text_headers(df, doc_width)
        identify_subtitles(df,doc_width)
        identify_subsubtitles(df)
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
        elif year==2006:
            assert len(test_df)==1
            assert test_df.iloc[0].text=='On Ghost Writing '
        else:
            assert len(test_df) == 0
        

if __name__=="__main__":
    test_open_doc()
