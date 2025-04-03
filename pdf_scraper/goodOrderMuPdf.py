import sys
import fitz
from fitz import Rect
from itertools import takewhile
from itertools import dropwhile
from utils import draw_rectangle_on_page, get_block_text, get_block_table

    
def get_pink_boundary(drawings, pink_fill):
    """
    Return one rectangle pink fill box in the page, by joining together other overlapping rectangle pink boxes.

    :param drawings: List of drawing objects from get_drawings()
    :param pink_fill: tuple specifying pink colour. (1.0, 0.8980000019073486, 0.9490000009536743) for 2024 P1
    :return: fitz.Rect of pink boundary or None
    """
    # To Do: 
    # Only look at pink fill objects which are rectangles
    pinks = [d for d in drawings if d["type"] == "f" and d["fill"]==pink_fill ]

    if not pinks:
        return None

    def in_the_stink(pink):
        '''
        returns True if the given pink is contained in any other pink on the page.
        '''
        return any( other["rect"].contains(pink["rect"])  for other in pinks if other != pink )

    filtered_pinks = [p for p in pinks if not in_the_stink(p)]

    x0 = min([p['rect'].x0 for p in filtered_pinks] )
    y0 = min([p['rect'].y0 for p in filtered_pinks] )
    x1 = max([p['rect'].x1 for p in filtered_pinks] )
    y1 = max([p['rect'].y1 for p in filtered_pinks] )
    king_pink = fitz.Rect(x0,y0,x1,y1)

    return king_pink

def in_the_pink(block: dict, king_pink: Rect):
    x0, y0, x1, y1 = block['bbox']
    block_rect = Rect(x0,y0,x1,y1)
    return  king_pink.contains(block_rect)
    

def isColumnSize(block, page_width):
    x0, y0, x1, y1 = block['bbox']
    col_width = x1 - x0
    return col_width <= page_width/2

def isEmptyBlock(block: dict):
    if block["type"]:
        return 0
    return 0 if get_block_text(block) else 1


def identify_dual_column(blocks, page_width, king_pink):
    possiBlocks     = [block for block in blocks      if isColumnSize(    block,page_width) ]   
    possiPinks      = [block for block in possiBlocks if in_the_pink(     block,king_pink) ]   
    dual_col_blocks = [block for block in possiPinks  if not isEmptyBlock(block)]

    return dual_col_blocks


def sort_dual_column_blocks(blocks: dict):
    coords = [block['bbox'] for block in blocks ] 
    x0_min = min(coord[0] for coord in coords)
    x0_max = max(coord[0] for coord in coords)
    x1_min = min(coord[1] for coord in coords)
    x1_max = max(coord[1] for coord in coords)

    vert_ordered = sorted(blocks, key = lambda block: block["bbox"][1])

    for block in vert_ordered:
        x0, y0, x1, y1 = block['bbox']
        dl = x0-x0_min
        dr = x0-x0_max
        block["col"] = 0 if abs(dl) < abs(dr) else 1
    
    col_ordered = sorted(vert_ordered,key = lambda x: x['col'])

    return col_ordered


def parse_page(page, king_pink=None):
    page_dict  = page.get_text("dict",sort=True)
    
    page_width  = page_dict["width"]   # This is a document wide thing doesn't need to be per page.
    blocks      = page_dict["blocks"]
    
    print(f"There are {len(blocks)} blocks on this page")
    print(f"page_width/2 = {page_width/2}")

    non_empty_blocks = [ block for block in blocks if not isEmptyBlock(block) ]
    #x_sorted_blocks  = sorted(non_empty_blocks, key = lambda x: x["bbox"][0])
    #sorted_blocks    = sorted(x_sorted_blocks,  key = lambda x: x["bbox"][1])
    #table_non_empty  = get_block_table(sorted_blocks)
    print(f"Here are all {len(non_empty_blocks)} non-empty blocks")
    table_non_empty  = get_block_table(non_empty_blocks)

    img_txt = "--"*40+"\n"+"Image"+"\n"+"--"*40
    # If there is no enclosing pink box, then there is no dual column 
    if not king_pink:
        txt_img_blocks = [get_block_text(block) if block["type"]==0 else img_txt for block in non_empty_blocks]
        return "\n\n".join(txt_img_blocks)
        

    dual_col_blocks   = identify_dual_column(non_empty_blocks, page_width, king_pink)
    sorted_duals      = sort_dual_column_blocks(dual_col_blocks)

    print(f"Here are {len(sorted_duals)} sorted dual-column blocks:\n")
    sorted_cols_table = get_block_table(sorted_duals)

    first_col = dual_col_blocks[0 ]["number"]
    last_col  = dual_col_blocks[-1]["number"]

    blocks_before = list(takewhile(lambda block: block["number"] != first_col, non_empty_blocks))
    blocks_after  = list(dropwhile(lambda block: block["number"] != last_col,  non_empty_blocks))[1:]
    
    final_blocks = blocks_before + sorted_duals + blocks_after
    print("Here are the before blocks:\n")
    before_table = get_block_table(blocks_before)

    print("Here are the final blocks:\n")
    final_table = get_block_table(final_blocks)
    
    txt_img_blocks = [get_block_text(block) if block["type"]==0 else img_txt for block in final_blocks ]
    page_text = "\n\n".join(txt_img_blocks)
    import ipdb; ipdb.set_trace()
        
    return page_text

if __name__=="__main__":
    # This is LC, english, higher level, Paper 1, English Version,  2024
    pdf = "test_pdfs/LC002ALP100EV_2024.pdf" 
    
    doc = fitz.open(pdf)
    
    # There should be 12 pages in our test file here.
    print(f"There are {len(doc)} pages")

    
    for n_page, page in enumerate(doc):
        if n_page !=3:
            continue
        print(f"Page {n_page+1}\n")
        print(f"--"*20)
        page_draws = page.get_drawings()
        pink_fill = (1.0, 0.8980000019073486, 0.9490000009536743) #page_draws[0]["fill"]
        king_pink = get_pink_boundary(page_draws,pink_fill)
        if king_pink:
            draw_rectangle_on_page(pdf, f"PyMuSortedPDF/bound_box_page_{n_page+1}.pdf",n_page,  king_pink)
        
        page_text = parse_page(page, king_pink)

        with open(f"PyMuSortedPDF/MuPdfPage{n_page+1}.txt", "w") as o:
            o.write(page_text)

        
    

