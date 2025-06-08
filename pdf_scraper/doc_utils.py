import fitz
import pandas as pd
from pathlib import Path
from pdf_scraper.block_utils import clean_blocks
from pdf_scraper.line_utils import get_line_df

subject_code = {
    "irish": "001",
    "english":"002",
    "mathematics":"003",
    "history":"004",
    "applied_mathematics":"020"
}

lang_code = {"irish":"IV", "english":"EV"}

def open_exam(year:int, subject: str, level: str, paper=0):
    code = subject_code[subject.lower()]
    fname    = f"LC{code}{level.upper()}P{paper}00EV_{year}.pdf"
    examDir  = Path(__file__).parent.parent / "Exams"  / subject.lower() / level.upper()
    pdf_file = examDir / fname

    return fitz.open(pdf_file)

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
        text_blocks = clean_blocks(text_blocks)

        page_lines   = [ line for block in text_blocks for line in block["lines"]]
        page_df = get_line_df(page_lines)
        page_df["page"] = i+1
        page_df.sort_values("y0",inplace=True)
        dfs.append(page_df)
    doc_df = pd.concat(dfs,ignore_index=True)
    doc_df["dual_col"]=0

    return doc_df

def filter_point_images(images):
    def is_point_image(img, threshold=5):
        x0, y0, x1, y1 = img["bbox"]
        return (x1 - x0) < threshold and (y1 - y0) < threshold
    return [img for img in images if not is_point_image(img) ]

def get_images(doc):
    images = []
    for i, page in enumerate(doc):
        page_blocks  = page.get_text("dict",sort=True)["blocks"]

        image_blocks = [block for block in page_blocks if     block["type"]]
        for image_block in image_blocks:
            image_block["page"]= i+1
            image_block["caption"] = ""

        images.extend(image_blocks)

    if len(images) > 500:
        images=filter_point_images(images)

    return images


def get_in_image_captions(doc_df: pd.DataFrame, images: list[dict]) -> list[dict]:
    """
    Add captions to images based on overlapping boxes. For english paper one, we
    will not caption anything on the first page, or after the 8th
    """
    for image in images:
        if image["page"] == 1 or image["page"] >8:
            continue
        img_rect = fitz.Rect(*image["bbox"])

        # Filter all potentially overlapping rows using bounding box logic
        overlap_mask = (
            (doc_df["x1"] > img_rect.x0 + 0.2) &
            (doc_df["x0"] < img_rect.x1) &
            (doc_df["y1"] > img_rect.y0 + 0.2) &
            (doc_df["y0"] < img_rect.y1) &
            (doc_df["page"] == image["page"] )
        )
        overlapping_rows = doc_df[overlap_mask]

        if len(overlapping_rows) > 0 and image["page"]!=1 :
            print(overlapping_rows[["text","page"]].head(4))

        overlapping_rows = overlapping_rows.sort_values(by="y0")

        # Collect and join the text
        image["caption"] = " ".join(overlapping_rows["text"].astype(str)).strip()

    return images

def get_captions(doc_df: pd.DataFrame, images: list[dict]) -> list[dict]:
    """
    Add captions to images based on overlapping boxes. For english paper one, we
    will not caption anything on the first page, or after the 8th
    """
    images = get_in_image_captions(doc_df, images)
    # Captions to add manually
    # 2019 p6: 'Warstones\xa0Library\xa0'
    # 2014 p3: 'Canada by Richard Ford – book cover '
    # 2013

    return images
