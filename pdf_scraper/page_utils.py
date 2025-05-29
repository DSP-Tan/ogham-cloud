from fitz import Page
from pdf_scraper.line_utils import get_line_df

def get_page_line_df(page: Page):
    # get sorted blocks
    blocks = page.get_text("dict",sort=True)["blocks"]
    lines = [ line for  block in blocks for line in block["lines"] if not block["type"] ]
    return get_line_df(lines)
    # get all lines from all blocks

