import numpy as np
import pandas as pd
import re
from scipy.stats import mode

def get_mode_font(fonts):
    font_counts = np.unique(fonts,return_counts=True)
    maxfontarg  = np.argmax(font_counts[1])
    return fonts[maxfontarg]

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


def get_line_text(line: dict) -> str:
    return "".join( [span["text"] for span in line["spans"] ] )

def get_line_words(line:dict) -> list:
    return re.findall(r'\b\w+\b', get_line_text(line) )

def line_is_empty(line):
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


def get_line_df(lines):
    coords         = [line['bbox'] for line in lines]
    x0             = [coord[0] for coord in coords]
    y0             = [coord[1] for coord in coords]
    dL             = [coords[i+1][1] - coords[i][1] for i in range(len(coords)-1)] + [np.nan]
    x1             = [coord[2] for coord in coords]
    y1             = [coord[3] for coord in coords]
    n_spans        = [len(line["spans"]) for line in lines]
    font_list      = [                [span["font"] for span in line["spans"]  ]  for line in lines]
    common_font    = [get_common_font([span["font"] for span in line["spans"]  ]) for line in lines]
    mode_font      = [get_mode_font(  [span["font"] for span in line["spans"]  ]) for line in lines]
    w              = [coord[2]-coord[0] for coord in coords]
    h              = [coord[3]-coord[1] for coord in coords]
    text           = [get_line_text(line)       for line in lines]
    n_words        = [len(get_line_words(line)) for line in lines ]
    font_size_list = [[span["size"] for span in line["spans"]  ]  for line in lines]
    mode_font_size = [ mode([span["size"] for span in line["spans"]  ]).mode for line in lines ]

    data_dict={"x0":x0,"y0":y0,"x1":x1,"y1":y1,"dL":dL, "n_spans":n_spans,"font_list":font_list,
    "common_font":common_font,"mode_font":mode_font,"n_words":n_words,"w":w,"h":h,
    "text":text, "font_sizes":font_size_list, "font_size":mode_font_size}
    return pd.DataFrame(data_dict)

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
