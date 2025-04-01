import fitz
from fitz import Rect
from itertools import takewhile
from itertools import dropwhile
import os, sys

def get_block_text(block_dict: dict ):
    '''
    For a given block dictionary element, as output by Page.get_text("dict")["blocks"], this 
    function will return the text of all the lines, joined by a "\n", and with the spans on 
    each line joined with a space. 
    
    The result is one string with newline separtaed lines and space
    separated spans.
    '''
    block_lines = block_dict["lines"]
    line_texts = [" ".join([ span["text"] for span in line["spans"] ]) for line in block_lines ]
    block_text="\n".join( [ i for i in line_texts if not i.isspace() ])
    return block_text


def get_block_table(blocks: dict):
    '''
    This function outputs a string which will list all the blocks in the page along with their coordinates, their
    type, and the first word if it's a text block.
    '''
    table=[f"{'x0':8} {'x1':8} {'y0':8} {'y1':8} {'dx':8} {'dy':8} {'type':5} {'number':7} {'first_word':10}", "--"*40]
    for block in blocks:
        type = "img" if block["type"] else "txt" 
        x0, y0, x1, y1 = block['bbox']
        beginning=get_block_text(block)[:11] if type =="txt" else "--"
        line=f"{x0:<8.2f} {x1:<8.2f} {y0:<8.2f} {y1:<8.2f} {x1-x0:<8.2f} {y1-y0:<8.2f} {type:5} {block['number']:<7} {beginning:<10}"
        table.append(line)
    return "\n".join(table)

    
def get_pink_boundary(drawings, pink_fill):
    """
    Return one rectangle pink fill box in the page, by joining together other overlapping rectangle pink boxes.

    :param drawings: List of drawing objects from get_drawings()
    :param pink_fill: tuple specifying pink colour. (1.0, 0.8980000019073486, 0.9490000009536743) for 2024 P1
    :return: fitz.Rect of pink boundary or None
    """
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



if __name__=="__main__":
    # This is LC, english, higher level, Paper 1, English Version,  2024
    pdf = "LC002ALP100EV_2024.pdf" 
    
    doc = fitz.open(pdf)
    
    # There should be 12 pages in our test file here.
    print(f"There are {len(doc)} pages")
    
    # We will look at page 7 as this is the only one which poses ordering problems
    n_page=7
    page = doc[n_page-1]

    page_dict  = page.get_text("dict",sort=True)
    page_draws = page.get_drawings()
    
    page_width  = page_dict["width"]
    page_height = page_dict["height"]
    blocks      = page_dict["blocks"]
    
    print(f"There are {len(blocks)} blocks in page {n_page}")

    print("Here all all the blocks:")
    table_raw=get_block_table(blocks)
    print(table_raw,"\n"*3)

    print("Here all all non-empty blocks:")
    non_empty_blocks = [ block for block in blocks if not isEmptyBlock(block) ]
    table_non_empty=get_block_table(non_empty_blocks)
    print(table_non_empty,"\n"*3)

    #pink_fill = (1.0, 0.8980000019073486, 0.9490000009536743)
    pink_fill = page_draws[0]["fill"]
    king_pink = get_pink_boundary(page_draws,pink_fill)

    if not king_pink:
        for block in non_empty_blocks:
            block_text = get_block_text(block)
            print(block_text,"\n")
        sys.exit(1)
        

    dual_col_blocks   = identify_dual_column(blocks, page_width, king_pink)
    table_dual_blocks = get_block_table(dual_col_blocks)
    print("Here are the dual-column blocks:\n",table_dual_blocks,"\n"*3)

    sorted_duals      = sort_dual_column_blocks(dual_col_blocks)
    sorted_cols_table = get_block_table(sorted_duals)
    print("Here are sorted dual-column blocks:\n",sorted_cols_table,'\n'*3)

    first_col = dual_col_blocks[0]["number"]
    last_col  = dual_col_blocks[-1]["number"]

    blocks_before = list(takewhile(lambda block: block["number"] != first_col, non_empty_blocks))
    blocks_after  = list(dropwhile(lambda block: block["number"] != last_col,  non_empty_blocks))[1:]
    
    
    final_blocks = blocks_before + sorted_duals + blocks_after

    for block in final_blocks:
        if block["type"]!=1:
            block_text = get_block_text(block)
            print(block_text,"\n")
        else:
            print("--"*40)
            print("Image")
            print("--"*40)
        



        
    


