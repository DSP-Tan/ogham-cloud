from pdf_scraper.clustering.customCluster import reblock_lines
from pdf_scraper.line_utils import line_is_empty, get_bbox, get_line_df, count_vert_space_discont
from fitz import Rect
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks
import numpy as np

def clean_blocks(blocks: list[dict]):
    '''
    This function removes all empty blocks from a list of blocks, and within a given
    block it removes all empty lines. Empty here means consisting of only empty space text. 

    It will not do anything to image blocks. 
    '''
    non_empty_blocks      = [block for block in blocks if not is_empty_block(block)]
    non_empty_text_blocks = [block for block in blocks if not block["type"]]
    for block in non_empty_text_blocks:
        block["lines"] = [line for line in block["lines"] if not line_is_empty(line)]
    return non_empty_blocks

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

def get_block_table(blocks: list[dict]):
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
    table.extend( ["--"*40,"\n"*2] )
    block_table = "\n".join(table)
    return block_table

def print_block_table(blocks: list[dict]):
    print(get_block_table(blocks))
    return None

def in_the_pink(block: dict, king_pink: Rect):
    x0, y0, x1, y1 = block['bbox']
    block_rect = Rect(x0,y0,x1,y1)
    return  king_pink.contains(block_rect)

def isColumnSize(block: dict, page_width:float):
    x0, y0, x1, y1 = block['bbox']
    col_width = x1 - x0
    return col_width <= page_width/2

def is_empty_block(block: dict):
    if block["type"]:
        return 0
    return 0 if get_block_text(block) else 1


# To Do: you should also check to see that there are some blocks in the pink of column size at the
# left, and some at the right. I.e. there will be a bunch of blocks with one kind of x0, and a bunch
# with antoher kind of x0
def identify_dual_column(blocks: list[dict], page_width: float, king_pink: Rect):
    possiBlocks     = [block for block in blocks      if isColumnSize(    block,page_width) ]   
    possiPinks      = [block for block in possiBlocks if in_the_pink(     block,king_pink) ]   
    dual_col_blocks = [block for block in possiPinks  if not is_empty_block(block)]

    return dual_col_blocks


def sort_dual_column_blocks(blocks: list[dict]):
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


def find_width_peaks(lines):
    df = get_line_df(lines)
    df = df[df.n_words > 4]
    w  = np.array(df.w)
    if len(w)==0:
        return []
    elif len(w) <=2:
        return [w.mean()]
    x_grid = np.linspace(w.min()-50, w.max()+50,1000)
    kde=gaussian_kde(w,bw_method='silverman')
    kde_vals = kde(x_grid)
    peaks, _ = find_peaks(kde_vals, prominence = 0.0001)
    return peaks


def detect_bad_block(block: dict,king_pink: Rect):
    '''
    This function
    '''
    lines=[line for line in block["lines"] if not line_is_empty(line)]
    df = get_line_df(lines)
    pink = in_the_pink(block, king_pink)
    n_base_fonts  = len(df.common_font.value_counts()) >= 2
    n_width_modes = len(find_width_peaks(lines)) >=2
    space_discont = count_vert_space_discont(lines) >=1
    two_o_three   = [n_base_fonts, n_width_modes, space_discont]

    if pink and sum(two_o_three) >=2:
        return True
    return False

def split_block(block: dict):
    """
    Splits block according to text formatting and removes any blank lines if they exist.
    """
    number = block["number"]
    type   = block["type"]
    lines   = [line for line in block["lines"] if not line_is_empty(line)]
    block_labels = reblock_lines(lines)


    lines0=[]
    lines1=[]
    for i, block in enumerate(block_labels):
        if block==0:
            lines0.append(lines[i])
        if block ==1:
            lines1.append(lines[i])

    bbox0 = get_bbox(lines0)
    bbox1 = get_bbox(lines1)
    block0 = {'number':number, 'type':type, 'bbox':bbox0 ,'lines':lines0}
    block1 = {'number':number, 'type':type, 'bbox':bbox1 ,'lines':lines1}
    return (block0, block1)


def preproc_blocks(blocks: list[dict], king_pink):
    blocks = clean_blocks(blocks)
    if not king_pink:
        return blocks
    new_blocks = []
    for i, block in enumerate(blocks):
        if block["type"]:
            new_blocks.append(block)
            continue
        if len(block["lines"]) <=1:
            new_blocks.append(block)
            continue
        if detect_bad_block(block,king_pink):
            two_blocks = split_block(block)
            new_blocks.extend(two_blocks)
            continue
        new_blocks.append(block)
    return new_blocks