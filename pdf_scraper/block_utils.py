from pdf_scraper.clustering.customCluster import reblock_lines
from pdf_scraper.line_utils import line_is_empty, get_bbox, get_line_df, count_vert_space_discont
from pdf_scraper.draw_utils import in_the_pink
from fitz import Rect
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks
import numpy as np

def clean_blocks(blocks: list[dict]):
    '''
    This function removes all empty blocks from a list of blocks, and within a given
    block it removes all empty lines. Empty here means consisting of only white space text.

    It will not do anything to image blocks.
    '''
    non_empty_blocks      = [block for block in blocks if not is_empty_block(block)]
    non_empty_text_blocks = [block for block in non_empty_blocks if not block["type"]]
    for block in non_empty_text_blocks:
        block["lines"] = [line for line in block["lines"] if not line_is_empty(line)]
    return non_empty_blocks


def get_block_text(block_dict: dict ):
    '''
    For a given block dictionary element, as output by Page.get_text("dict")["blocks"][0], this
    function will return the text of all the lines, joined by a "\n", and with the spans on
    each line joined with a space.

    The result is one string with newline separtaed lines and space
    separated spans.
    '''
    lines     = block_dict["lines"]
    line_df   = get_line_df(lines)
    line_df.h  = line_df.h.map(lambda x: round(x,2))
    h = line_df.h.median()

    if len(lines)>1:
        line_df.dL = line_df.dL.map(lambda x: round(x,2))
        dL = line_df.dL.median()
    else:
        dL = h*1.04
    tol = 0.001

    block_text= " ".join([ span["text"] for span in lines[0]["spans"] ])
    for i, line in enumerate(lines[1:]):
        line_text = " ".join([ span["text"] for span in line["spans"] ])

        x00,y00,x01,y01   = lines[i]["bbox"]
        x10, y10,x11,y11  = line["bbox"]
        dy = abs(y10 - y00)
        if dy <= dL + tol and dy >= dL -tol: 
            block_text += "\n" + line_text
        elif dy <= 2*dL + tol and dy >= 2*dL -tol: 
            block_text += "\n\n" + line_text 
        elif dy <=  tol: 
            block_text += " " + line_text
        else: 
            block_text += "\n" + line_text
    if block_text.isspace():
        return ""
    return block_text

def get_block_text_old(block_dict: dict ):
    '''
    We'll hold on to this for a while then delete it later.
    For a given block dictionary element, as output by Page.get_text("dict")["blocks"][0], this
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
    table=[f"{'x0':8} {'x1':8} {'y0':8} {'y1':8} {'dx':8} {'dy':8} {'type':5} {'number':7} {'n_lines':7} {'first_word':10}", "--"*40]
    for block in blocks:
        type = "img" if block["type"] else "txt"
        x0, y0, x1, y1 = block['bbox']
        beginning=get_block_text(block)[:11] if type =="txt" else "--"
        n_lines = len(block["lines"])        if type =="txt" else 0
        line=f"{x0:<8.2f} {x1:<8.2f} {y0:<8.2f} {y1:<8.2f} {x1-x0:<8.2f} {y1-y0:<8.2f} {type:5} {block['number']:<7} {n_lines:<7} {beginning:<10}"
        table.append(line)
    table.extend( ["--"*40,"\n"*2] )
    block_table = "\n".join(table)
    return block_table

def print_block_table(blocks: list[dict]):
    print(get_block_table(blocks))
    return None


def isColumnSize(block: dict, page_width:float):
    x0, y0, x1, y1 = block['bbox']
    col_width = x1 - x0
    return col_width <= page_width/2

def is_empty_block(block: dict):
    if block["type"]:
        return 0
    empty_lines = [line_is_empty(line) for line in block["lines"]]

    return all(empty_lines )


# To Do: you should also check to see that there are some blocks in the pink of column size at the
# left, and some at the right. I.e. there will be a bunch of blocks with one kind of x0, and a bunch
# with antoher kind of x0
# - If you have short headers this will select them.
# - You should really put in a check on the common font of all lines within the pink.
# - This would mean writing a function which gets all blocks in the pink, concatenates their lines, and gets their common font.
#   - Then take median common font or mode common font.
def get_dual_col_blocks(blocks: list[dict], king_pink: Rect):

    return [block for block in blocks if identify_dual_column(block, king_pink)]

def identify_dual_column(block: dict, king_pink: Rect):

    x0, y0, x1, y1  = block["bbox"]
    pink_width      = king_pink.x1 - king_pink.x0
    pink_centre     = (king_pink.x0+king_pink.x1)/2
    line_centre     = (x0+x1)/2

    non_empty       = not is_empty_block(block)
    pink            = in_the_pink(     block["bbox"],king_pink) 
    col_sized       = isColumnSize(block, pink_width) 
    not_centred     = (line_centre < pink_centre-12) or (line_centre > pink_centre+12)

    return non_empty and pink and col_sized and not_centred

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
    """
    This functino will use a gaussian_kde to determine the modes
    in the distribution of widths of lines.
    
    Lines in a column shouldn't have two distinct peaks in their width 
    distribution. This would suggest that there is a group of long lines
    combined with columnar lines.
    """
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

def in_and_out_of_pink(bbox: tuple, king_pink: Rect):
    '''
    Returns True if there is a block which has a bounding box which overlaps
    but is not contained completely inside of the pink.

    Such blocks should not exist and this is definitely a clumped block.
    '''
    x0, y0, x1, y1 = bbox
    in_x = (x0 > king_pink.x0 and x1 < king_pink.x1)
    in_and_out_y = (y0 > king_pink.y0 and y1 > king_pink.y1)
    return in_x and in_and_out_y

def detect_bad_block(block: dict,king_pink: Rect):
    '''
    This function will detect if there are groups of text which are 
    very diverse and are yet grouped together.
    
    If there are many base fonts, two different modes in the distribution
    of widths of lines, and space discontinuities in the y direction, we 
    will consider these lines to be badly blocked together, and we will separte
    them into different blocks.
    '''
    lines=[line for line in block["lines"] if not line_is_empty(line)]
    bbox = block["bbox"]
    df = get_line_df(lines)
    pink = in_the_pink(bbox, king_pink) or in_and_out_of_pink(bbox,king_pink)
    n_base_fonts  = len(df.common_font.value_counts()) >= 2
    n_width_modes = len(find_width_peaks(lines)) >=2
    space_discont = count_vert_space_discont(lines) >=1
    two_o_three   = [n_base_fonts, n_width_modes, space_discont]

    if pink and sum(two_o_three) >=2:
        return True
    return False

def split_block(block: dict):
    """
    Splits block according to re-clustered lines and removes any blank lines if they exist.
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

def simple_multi_split(block: dict):
    number = block["number"]
    type   = block["type"]
    lines   = [line for line in block["lines"] if not line_is_empty(line)]
    df = get_line_df(lines)

    median = np.median(df.dL[:-1])
    indices = []
    for i, dL in enumerate(df.dL):
        if dL > 1.45*median:
            indices.append(i+1)
    split_lines = np.split(lines, indices, axis=0 )
    split_blocks = [{'number':number, 'type':type, 'bbox':get_bbox(lins) ,'lines':lins} for lins in split_lines]
    return split_blocks

def renumber_blocks(blocks: list[dict]):
    for i, block in enumerate(blocks):
        block["number"] = i
    return None

def sort_blocks_by_y0(blocks: list[dict]):
    return sorted(blocks, key = lambda block: block["bbox"][1])

def rebox_blocks(blocks: list[dict]):
    '''
    This will loop through all blocks, and set the bbox of the blocks according
    to the bbox of the lines. This is useful if for example you have removed all
    empty lines from the block and want the bbox to reflect only actual text, and
    not just empty newlines.
    '''
    for block in blocks:
        if block["type"]:
            continue
        block["bbox"] = get_bbox(block["lines"])
    return blocks


def preproc_blocks(blocks: list[dict], king_pink: Rect):
    """
    This function preprocesses the input list of blocks by:
    1. cleaning the blocks (remove empty blocks, and empty lines within blocks)
    2. re-boxes the blocks to account for removed whtiespace (re defines bbox)
    3. checks for blocks which are badly made by pymupdf blocking algorithm. (mix of dual col and non dual col) 
       Splits based on vertical space discontinuity.
    4. Splits any very long columnar blocks based on vertical line-space discontinuities.
    """
    blocks = clean_blocks(blocks)
    rebox_blocks(blocks)
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
            #split_blocks = split_block(block)
            split_blocks = simple_multi_split(block)
            new_blocks.extend(split_blocks)
            continue
        if col_block_is_too_big(block, king_pink):
            split_blocks = simple_multi_split(block)
            new_blocks.extend(split_blocks)
            continue
        new_blocks.append(block)
    re_sorted_blocks = sorted(new_blocks, key = lambda block: block["bbox"][1])
    renumber_blocks(re_sorted_blocks)
    return re_sorted_blocks



def col_block_is_too_big(block:dict, king_pink: Rect):
    '''
    This function is to identify if amongst the dual column blocks that have been
    identified, there is one that is too large and could be broken up.
    '''
    lines=[line for line in block["lines"] if not line_is_empty(line)]
    pink = in_the_pink(block["bbox"], king_pink)
    n_lines  = len(lines) >= 3
    space_discont = count_vert_space_discont(lines) >1
    too_big = all([n_lines, space_discont])
    return pink and too_big
