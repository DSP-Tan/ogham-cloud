import fitz
from pathlib import Path
from fitz import Rect
from itertools import takewhile
from itertools import dropwhile
from pdf_scraper.block_utils import get_block_text, print_block_table, detect_bad_block
from pdf_scraper.block_utils import preproc_blocks, get_dual_col_blocks, sort_dual_column_blocks
from pdf_scraper.draw_utils  import get_pink_boundary, draw_rectangle_on_page, get_fill_df, get_fill_colours



def parse_page(page, king_pink=None):
    page_dict  = page.get_text("dict",sort=True)

    page_width  = page_dict["width"]   # This is a document wide thing doesn't need to be per page.
    raw_blocks  = page_dict["blocks"]

    blocks = preproc_blocks(raw_blocks, king_pink)

    print(f"There are {len(blocks)} blocks on this page")
    print(f"page_width/2 = {page_width/2}")

    print(f"Here are all {len(blocks)} non-empty blocks")
    print_block_table(blocks)

    img_txt = "--"*40+"\n"+"Image"+"\n"+"--"*40
    # If there is no enclosing pink box, then there is no dual column
    if not king_pink:
        txt_img_blocks = [get_block_text(block) if block["type"]==0 else img_txt for block in blocks]
        return "\n\n".join(txt_img_blocks)


    dual_col_blocks   = get_dual_col_blocks(blocks, king_pink)
    # Somtimes there is an enclosing pink box but still no dual column.
    if not dual_col_blocks:
        txt_img_blocks = [get_block_text(block) if block["type"]==0 else img_txt for block in blocks]
        return "\n\n".join(txt_img_blocks)

    sorted_duals      = sort_dual_column_blocks(dual_col_blocks)

    print(f"Here are {len(sorted_duals)} sorted dual-column blocks:\n")
    print_block_table(sorted_duals)

    first_col = dual_col_blocks[0 ]["number"]
    last_col  = dual_col_blocks[-1]["number"]

    blocks_before = list(takewhile(lambda block: block["number"] != first_col, blocks))
    blocks_after  = list(dropwhile(lambda block: block["number"] != last_col,  blocks))[1:]

    final_blocks = blocks_before + sorted_duals + blocks_after
    print("Here are the before blocks:\n")
    print_block_table(blocks_before)

    print("Here are the final blocks:\n")
    print_block_table(final_blocks)

    txt_img_blocks = [get_block_text(block) if block["type"]==0 else img_txt for block in final_blocks ]
    page_text = "\n\n".join(txt_img_blocks)

    return page_text

if __name__=="__main__":
    # This is LC, english, higher level, Paper 1, English Version,  2024
    year=2016
    level = "AL"
    fname =  f"LC002ALP100EV_{year}.pdf"
    examDir = Path(__file__).parent.parent / "Exams" / "english" / level
    pdf = examDir / fname


    doc = fitz.open(pdf)

    # There should be 12 pages in our test file here.
    print(f"There are {len(doc)} pages")

    page2_drawings   = doc[1].get_drawings()
    fill_colour      = get_fill_df(page2_drawings).fill.mode().values[0]
    fill_colours     = get_fill_colours(doc)

    out_dir = "scrapedPages"
    for n_page, page in enumerate(doc):
        #if n_page !=5:
        #    continue
        print(f"Page {n_page+1}\n")
        print(f"--"*20)
        page_draws = page.get_drawings()

        king_pink = get_pink_boundary(page_draws,fill_colours)
        if king_pink:
            pdf_box_out = Path(__file__).parent / out_dir / f"bound_box_page_{n_page+1}.pdf"
            draw_rectangle_on_page(pdf, pdf_box_out ,n_page,  king_pink)

        page_text = parse_page(page, king_pink)

        text_out = Path(__file__).parent / out_dir / f"MuPdfPage{n_page+1}.txt"
        with open(text_out, "w") as o:
            o.write(page_text)
