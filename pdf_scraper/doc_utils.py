import fitz
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import re
from pdf_scraper.block_utils import clean_blocks
from pdf_scraper.line_utils  import get_line_df, get_line_text
from pdf_scraper.image_utils import is_point_image, is_horizontal_strip,filter_point_images, filter_horizontal_strips
from pdf_scraper.image_utils import filter_horizontal_strips,get_stripped_images,stitch_strips, reconstitute_strips
from pdf_scraper.image_utils import get_in_image_lines, get_in_image_captions

subject_code = {
    "irish": "001",
    "english":"002",
    "mathematics":"003",
    "history":"004",
    "applied_mathematics":"020"
}

lang_code = {"irish":"IV", "english":"EV"}

def open_exam(year:int, subject="english", level="al", paper=1):
    code = subject_code[subject.lower()]
    fname    = f"LC{code}{level.upper()}P{paper}00EV_{year}.pdf"
    examDir  = Path(__file__).parent.parent / "Exams"  / subject.lower() / level.upper()
    pdf_file = examDir / fname

    return fitz.open(pdf_file)

def get_doc_year(doc):
    """Returns year of exam of document using file path."""
    year = int(str(doc).split("_")[1][:4])
    return year

def extract_and_print_page(input_pdf:str, output_pdf:str, n_page:int):
    doc = fitz.open(input_pdf)

    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=n_page-1, to_page=n_page-1)  # 7th page (0-based index)
    new_doc.save(output_pdf)
    new_doc.close()
    doc.close()

def get_doc_line_df(doc):
    """
    Returns a data frame of all lines in the document with the page numbers added
    and all lines sorted vertically per page.
    """
    dfs = []
    for i, page in enumerate(doc):
        page_blocks  = page.get_text("dict",sort=True)["blocks"]

        text_blocks  = [block for block in page_blocks if not block["type"]]
        text_blocks  = clean_blocks(text_blocks)

        page_lines   = [ line for block in text_blocks for line in block["lines"]]
        page_df = get_line_df(page_lines)
        page_df["page"] = i+1
        page_df.sort_values("y0",inplace=True)
        dfs.append(page_df)
    doc_df = pd.concat(dfs,ignore_index=True)
    doc_df["dual_col"]=0

    return doc_df

def get_raw_lines(doc, row: pd.Series):
    n_page = row.page
    page = doc[n_page -1]
    page_blocks  = page.get_text("dict",sort=True)["blocks"]
    text_blocks  = [block for block in page_blocks if not block["type"]]
    text_blocks  = clean_blocks(text_blocks)
    page_lines   = [ line for block in text_blocks for line in block["lines"]]
    line_texts   = [get_line_text(line) for line in page_lines]
    raw_line_index  = [ i for i, text in enumerate(line_texts) if text == row.text]
    raw_lines = [ page_lines[i] for i in raw_line_index]
    return raw_lines


def get_images(doc):
    images = []
    for i, page in enumerate(doc):
        page_blocks  = page.get_text("dict",sort=True)["blocks"]

        image_blocks = [block for block in page_blocks if     block["type"]]
        for image_block in image_blocks:
            image_block["page"]= i+1
            image_block["caption"] = ""

        images.extend(image_blocks)

    return images

def filter_images(images):
    if len(images) > 100:
        images=filter_point_images(images)
    if len(images) > 100:
        images = reconstitute_strips(images)
    return images

def assign_in_image_captions(doc_df: pd.DataFrame, images: list[dict]) -> list[dict]:
    """
    Add captions to images based on overlapping boxes. For english paper one, we
    will not caption anything on the first page, or after the 8th
    """
    caption_line_indices=pd.Index([])
    count=0
    for image in images:
        if image["page"] == 1 or image["page"] >8:
            image["caption"]=""
            continue
        indices=get_in_image_lines(image,doc_df)
        doc_df.loc[indices]["caption"]=1
        if len(indices)>0:
            caption_line_indices.append(indices)
            captions = get_in_image_captions(image,doc_df, indices)
            image["caption"] = captions
            count+=1
        else:
            image["caption"] = ""

    return caption_line_indices, count

def get_captions(doc_df: pd.DataFrame, images: list[dict]) -> list[dict]:
    """
    Add captions to images based on overlapping boxes. For english paper one, we
    will not caption anything on the first page, or after the 8th
    """
    caption_indices, n_img = assign_in_image_captions(doc_df, images)
    # Captions to add manually
    # 2019 p6: 'Warstones\xa0Library\xa0'
    # 2014 p3: 'Canada by Richard Ford – book cover '
    # 2013 p4:
    # 2013 p6:
    # 2013 p7:

    return images

def identify_instructions(doc_df):
    page = (doc_df.page != 1)
    pattern1 = doc_df.text.str.lstrip().str.contains(r"^N\.B\.")
    pattern2 = doc_df.text.str.contains(r"^Candidates may NOT")
    pattern3 = doc_df.text.str.contains(r"^Questions.*A.*and.*B.*carry.*50.*marks.*each")
    mask = page & (pattern1 | pattern2 | pattern3)
    doc_df.loc[mask, "instruction"] = 1
    return doc_df

def identify_footers(doc_df):
    doc_df['rank'] = doc_df.groupby('page')['y0'].rank(method='first', ascending=False)

    n_page_regex= r'page[ \xa0]*?(?:1[0-2]|[1-9])[ \xa0]of[ \xa0](?:1[0-2]|[1-9])'
    n_page_regex= r'page[\xa0 ]*?(?:1[0-2]|[1-9])[\xa0 ]*?of[\xa0 ]*?(?:1[0-2]|[1-9])'
    lc_regex    = r'leaving[ \xa0]certificate[ \xa0]examination[ \xa0]20[0-9][0-9]'
    eng_regex   = r'english[ \xa0]–[ \xa0]higher[ \xa0]level[ \xa0]–[ \xa0]paper[ \xa0]1'
    num_regex   = r'^(?:1[0-2]|[1-9])$'

    pattern1 = doc_df.text.str.lower().str.contains(n_page_regex, regex=True)
    pattern2 = doc_df.text.str.lower().str.contains(lc_regex, regex=True)
    pattern3 = doc_df.text.str.lower().str.contains(eng_regex, regex=True)
    pattern4 = doc_df.text.str.strip().str.contains(num_regex, regex=True)
    bottom   = doc_df['rank'] <= 3

    mask = bottom & (pattern1 | pattern2 | pattern3 | pattern4 )

    doc_df.loc[mask, "footer"] = 1
    doc_df.drop(columns=["rank"],inplace=True)

    return doc_df

def identify_section_headers(doc_df):
    """
    Section Titles will have the following properties:
    - Centred
    - Larger than the median text size on page.
    - Near top?
    """
    doc_df['rank'] = doc_df.groupby('page')['y0'].rank(method='first', ascending=True)

    section_regex= r'section[\xa0 ]*(?:I{1,2}|[1-2])'
    compre_regex = r'comprehending'
    compos_regex = r'composing'
    marks_regex  = r'\(\d{1,3}\)\s*marks'

    pattern1 = doc_df.text.str.contains(section_regex,flags=re.IGNORECASE, regex=True)
    pattern2 = doc_df.text.str.lower().str.contains(compre_regex, regex=True)
    pattern3 = doc_df.text.str.lower().str.contains(compos_regex, regex=True)
    pattern4 = doc_df.text.str.strip().str.contains(marks_regex, regex=True)
    top = doc_df['rank'] <= 4

    mask = top & (pattern1 | pattern2 | pattern3 | pattern4 )

    doc_df.loc[mask, "section"] = 1
    doc_df.drop(columns=["rank"],inplace=True)

    return doc_df
