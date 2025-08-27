import numpy as np
import pandas as pd
import re, fitz
from scipy.stats import mode
from pdf_scraper.general_utils import bbox_distance, bbox_vert_dist


def common_font_elems(s1,s2):
    L1, L2 = len(s1), len(s2)
    L = L1 if L1 < L2 else L2
    s3 = ""
    for i in range(L):
        if s1[i]!=s2[i]:
            return s3
        s3 += s1[i]
    return s3

def get_common_font(fonts):
    common_font=fonts[0]
    for font in fonts[1:]:
        common_font =common_font_elems(common_font,font)
    return "".join(common_font)

def get_span_mode_font(fonts):
    font_counts = np.unique(fonts,return_counts=True)
    maxfontarg  = np.argmax(font_counts[1])
    return fonts[maxfontarg]

def get_mode_font(line):
    """
    Because we will often have a line composed of many spans some of which have different
    fonts, this function will return the font used for the most characters of the line.
    """
    spans          = line["spans"]
    n_spans        = len(spans)
    if n_spans ==1:
        return line["spans"][0]["font"]
    fonts = [span["font"] for span in spans]
    font_count = {font:0 for font in fonts}
    for span in spans:
        n_chars = len(span["text"])
        font_count[span["font"]] += n_chars
    return max(font_count, key=font_count.get)


def get_line_text(line: dict) -> str:
    return "".join( [span["text"] for span in line["spans"] ] )

def get_line_words(line:dict) -> list:
    return re.findall(r'\b\w+\b', get_line_text(line) )

def line_is_empty(line: dict) -> bool:
    return all( [span["text"].isspace() for span in line["spans"]] )

def get_line_table(lines: dict):
    '''
    This function outputs a string which will list all the blocks in the page along with their coordinates, their
    type, and the first word if it's a text block.
    '''
    table=[f"{'x0':8} {'x1':8} {'y0':8} {'y1':8} {'dx':8} {'dy':8} {'fonts':36} {'beginning':25}", "--"*60]
    for line in lines:
        font           = line["spans"][0]["font"]
        font_list      = list(set(span["font"] for span in line["spans"] ) )
        x0, y0, x1, y1 = line['bbox']
        beginning      = line["spans"][0]["text"][:25]
        line=f"{x0:<8.2f} {x1:<8.2f} {y0:<8.2f} {y1:<8.2f} {x1-x0:<8.2f} {y1-y0:<8.2f} {' '.join(font_list):36} {beginning:<25}"
        table.append(line)
    table.extend( ["--"*60,"\n"*2] )
    line_table = "\n".join(table)
    return line_table

def print_line_table(lines:dict):
    print(get_line_table(lines))
    return None

def get_all_lines(blocks: list[dict]):
    lines=[]
    for block in blocks:
        if not block["type"]:
            lines.extend(block["lines"])
    return lines

def get_font_size(line):
    """
    Because we will often have a line composed of many spans some of which have different
    font sizes, we need a way to decide which of these font sizes to use.

    We could use the mode of the font sizes of each span. However, when there are
    just two spans this is ambiguous.

    When there are two spans, we take the font size to be the font size used for
    the most characters. So we will need the size of the spans.
    """
    spans          = line["spans"]
    n_spans        = len(spans)
    if n_spans ==1:
        return line["spans"][0]["size"]
    font_sizes = [span["size"] for span in spans]
    size_count = {font_size:0 for font_size in font_sizes}
    for span in spans:
        n_chars = len(span["text"].strip())
        size_count[span["size"]] += n_chars
    return max(size_count, key=size_count.get)


def get_line_df(lines):
    coords         = [line['bbox'] for line in lines]
    x0             = [coord[0] for coord in coords]
    y0             = [coord[1] for coord in coords]
    dL             = [coords[i+1][1] - coords[i][1] for i in range(len(coords)-1)] + [np.nan] if len(lines)>0 else []
    x1             = [coord[2] for coord in coords]
    y1             = [coord[3] for coord in coords]
    n_spans        = [len(line["spans"]) for line in lines]
    font_list      = [                [span["font"] for span in line["spans"]  ]  for line in lines]
    common_font    = [get_common_font([span["font"] for span in line["spans"]  ]) for line in lines]
    mode_font      = [get_mode_font( line ) for line in lines]
    w              = [coord[2]-coord[0] for coord in coords]
    h              = [coord[3]-coord[1] for coord in coords]
    text           = [get_line_text(line)       for line in lines]
    n_words        = [len(get_line_words(line)) for line in lines ]
    font_size_list = [[span["size"] for span in line["spans"]  ]  for line in lines]
    mode_font_size = [ mode([span["size"] for span in line["spans"]  ]).mode for line in lines ]
    font_size      = [get_font_size(line) for line in lines]
    dual_col       = [0]*len(lines)
    caption        = [0]*len(lines)
    instruction    = [0]*len(lines)
    footer         = [0]*len(lines)
    section        = [0]*len(lines)
    title          = [0]*len(lines)
    subtitle       = [0]*len(lines)
    subsubtitle    = [0]*len(lines)


    data_dict={"x0":x0,"y0":y0,"x1":x1,"y1":y1,"dL":dL, "n_spans":n_spans,"font_list":font_list,
    "common_font":common_font,"mode_font":mode_font,"n_words":n_words,"w":w,"h":h,
    "text":text, "font_sizes":font_size_list, "mode_font_size":mode_font_size,
    "font_size":font_size, "dual_col":dual_col, "caption":caption,
    "instruction":instruction, "footer":footer, "section":section,
    "title":title, "subtitle":subtitle, "subsubtitle":subsubtitle}
    return pd.DataFrame(data_dict)

def get_level_line_counts(df, overlap_factor):
    """
    This will count the number of lines which have a y0 which is within
    overlap_factor of a given line. 
    
    It can be used to detect dual column text etc.
    """
    temp_df = df[['y0', 'h', 'page']].copy()
    temp_df["index_col"] = temp_df.index

    new_df = temp_df.merge(temp_df, on="page", suffixes=("", "_other"))
    new_df = new_df[new_df.index_col != new_df.index_col_other].copy()

    new_df["y_diff"] = abs(new_df["y0"] - new_df["y0_other"])
    new_df = new_df[new_df["y_diff"] <= new_df["h"] * overlap_factor]

    counts_per_index = new_df.groupby("index_col").size()
    counts_series = df.index.map(counts_per_index).fillna(0).astype(int)

    return counts_series

def clean_line_df(df):
    buff_mask = is_buffered_line(df, 6)
    df.loc[buff_mask, ["x0", "x1", "text"]] = df.loc[buff_mask].apply(re_box_line, axis=1)
    return df

def get_clean_bins(x:pd.Series,bin_width:float):
    '''
    The purpose of this function is to create bints for the x0 and x1 values found
    in line df. So we will pass df.x0 or df.x1 to it, and it will return to us binned
    values of the x0 and x1. These can be used to see if a line is a member of a certain
    column or not.
    '''
    min = x.min()
    max = x.max()

    bins = np.arange(start=min-bin_width/2, stop=max + 2*bin_width, step=bin_width)

    x_binned = pd.cut(x, bins=bins).apply(lambda i: i.mid).value_counts()

    return x_binned[x_binned !=0]

def get_bbox(lines):
    line_df = get_line_df(lines)
    x0 = line_df.x0.min()
    y0 = line_df.y0.min()
    x1 = line_df.x1.max()
    y1 = line_df.y1.max()
    return tuple( float(i) for i in [x0,y0,x1,y1] )

def get_df_bbox(line_df):
    x0 = line_df.x0.min()
    y0 = line_df.y0.min()
    x1 = line_df.x1.max()
    y1 = line_df.y1.max()
    return tuple( float(i) for i in [x0,y0,x1,y1] )


def is_buffered_line(df: pd.DataFrame, threshold: int = 3) -> pd.Series:
    """
    Returns a boolean Series where 'text' starts or ends with at least <threshold> spaces.
    use:
    mask=  is_buffered_line(df, 6)
    buffered_lines = df.loc[ mask ]
    """
    return df.text.str.endswith(" " * threshold ) | df.text.str.startswith(" "* threshold )


FONT_MAP = {
    'TimesNewRomanPSMT': 'Times-Roman',
    'TimesNewRomanPS'  : 'Times-Roman',
    'TimesNewRoman'    : 'Times-Roman',
    'TimesNewRomanPS-BoldMT': 'Times-Bold',
    'TimesNewRomanPS-BoldItal' : 'Times-BoldItalic',
    'TimesNewRoman,Bold': 'Times-Bold',
    'TimesNewRomanPS-Bold': 'Times-Bold',
    'TimesNewRomanPS-ItalicMT': 'Times-Italic',
    'TimesNewRomanPS-BoldItalicMT': 'Times-BoldItalic',
    'ArialMT': 'Helvetica',
    'Arial-BoldMT': 'Helvetica-Bold',
    'CourierNewPSMT': 'Courier',
    'Cambria': 'Times-Roman',
    'Cambria-Bold': 'Times-Bold',
    'Cambria-Italic': 'Times-Italic',
    'Cambria-BoldItalic': 'Times-BoldItalic',
    'Calibri': 'Helvetica',
    'Calibri-Bold': 'Helvetica-Bold',
    'Calibri,Bold': 'Helvetica-Bold',
    'Calibri-Italic': 'Helvetica-Oblique',
    'Calibri-BoldItalic': 'Helvetica-BoldOblique',
    }

def re_box_line(row: pd.Series) -> pd.Series:
    """
    This functino removes leading and trailing whitespace in a line, and adjusts the
    bounding box of the line to be only around the non-whitespace text.
    
    Motivated by strings like:
    '                                      hello'
    Which is actually centred but which will have a bbox that says left-aligned.

    Use: 
    buffered_lines.update(buffered_lines.apply(re_box_line_partial, axis=1))
    or
    fixed_lines.loc[:,["x0","x1","text"]] = buffered_lines.apply(re_box_line_partial, axis=1)
    """
    font_name = FONT_MAP[row.mode_font]
    #try:
    #    font_name = FONT_MAP[row.mode_font]
    #except:
    #    font_name = FONT_MAP[row.common_font]

    font = fitz.Font(font_name)  
    txt = row.text
    l_spaces = len(txt) - len(txt.lstrip() )
    r_spaces = len(txt) - len(txt.rstrip() )
        
    space_advance = font.glyph_advance(ord(' '))  
    l_width = l_spaces * space_advance * row.font_size
    r_width = r_spaces * space_advance * row.font_size
    
    x0 = row.x0 + l_width
    x1 = row.x1 - r_width
    text = txt.strip()

    return pd.Series({"x0":x0,"x1":x1, "text":text })

from scipy.stats import gaussian_kde
from scipy.signal import find_peaks
def count_vert_space_discont(lines):
    lines = [line for line in lines if not line_is_empty(line)]
    df = get_line_df(lines)
    dLs = np.array(df.dL[:-1])
    median = np.median(df.dL[:-1])

    count=0
    for i, val in enumerate(dLs):
        temp = np.delete(dLs, i, 0)
        if val>1.45*median:
            count +=1
    return count

def line_space_discont(lines):
    lines = [line for line in lines if not line_is_empty(line)]
    df = get_line_df(lines)

    dLs = np.array(df.dL[:-1])
    median = np.median(df.dL[:-1])

    for i, val in enumerate(dLs):
        temp = np.delete(dLs, i, 0)
        if val > 1.45*median:
            #print(i, all(val > temp*1.6) )
            return True
    return False


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


def closest_image(bbox:tuple[float,float,float,float], images:list[dict], n_page:int )-> tuple[dict,float]:
    dist = 100000
    page_images = [img for img in images if img["page"]==n_page]
    for image in page_images:
        bbox_dist = bbox_distance(bbox,image["bbox"])
        if bbox_dist < dist:
            closest=image
            dist   =bbox_dist
    return (image, dist)

def closest_line(bbox:tuple[float,float,float,float], doc_df: pd.DataFrame, n_page:int)->tuple[int,float]:
    """
    Finds the closest bbox contained in doc_df to the given bbox, excluding exactly
    overlapping bboxes.
    """
    right_page = doc_df.page == n_page
    not_same   = (
        ( doc_df.x0 != bbox[0] ) &
        ( doc_df.y0 != bbox[1] ) &
        ( doc_df.x1 != bbox[2] ) &
        ( doc_df.y1 != bbox[3] )
    )
    dists=doc_df[right_page & not_same ].apply(
        lambda row: bbox_distance((row["x0"], row["y0"], row["x1"], row["y1"]), bbox),
        axis=1
    )
    return (dists.idxmin(), dists.min() )

def closest_vertical_line(bbox:tuple[float,float,float,float], df: pd.DataFrame, n_page:int)->tuple[int,float]:
    """
    Finds the closest bbox contained in Dataframe df to the given bbox, excluding exactly
    overlapping bboxes.
    """
    right_page = df.page == n_page
    not_same = ~(
        (df.x0 == bbox[0]) &
        (df.y0 == bbox[1]) &
        (df.x1 == bbox[2]) &
        (df.y1 == bbox[3])
    )
    dists=df[right_page & not_same ].apply(
        lambda row: bbox_vert_dist((row["x0"], row["y0"], row["x1"], row["y1"]), bbox),
        axis=1
    )
    return (dists.idxmin(), dists.min() )
