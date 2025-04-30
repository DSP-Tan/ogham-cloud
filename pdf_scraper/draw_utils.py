import fitz
from fitz import Rect
import pandas as pd
from pathlib import Path
import numpy as np

def draw_rectangle_on_page(pdf_path: str, output_pdf: str,  page_index: int, rect: Rect):
    """
    Opens a PDF, draws a dark blue rectangle on the specified page, and saves the modified PDF.
    :param pdf_path: input pdf path; param output_pdf: output pdf path
    :param page_index: index of page you want to draw rect on. (from 0)
    :param Rect -> fitz.Rect object rectangle you want to draw on page
    """
    doc  = fitz.open(pdf_path)
    page = doc[page_index]
    page.draw_rect(rect, color=(0, 0, 0.5), width=3)

    out_doc = fitz.open()
    out_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)
    out_doc.save(output_pdf)
    out_doc.close()
    doc.close()


def get_fill_df(drawings):
    draws = [ draw for draw in drawings if draw["type"]=="f"]
    #n_items       = [len(draw['items']) for draw in draws]  # fills are generally just one rectangle
    item_types    = [ [item[0] for item in draw["items"] ] for draw in draws ]
    type          = [draw['type'] for draw in draws]
    fill_opacity  = [draw['fill_opacity'] for draw in draws]
    r             = [draw['fill'][0] for draw in draws]
    b             = [draw['fill'][1] for draw in draws]
    g             = [draw['fill'][2] for draw in draws]
    x0            = [draw['rect'].x0 for draw in draws]
    y0            = [draw['rect'].y0 for draw in draws]
    x1            = [draw['rect'].x1 for draw in draws]
    y1            = [draw['rect'].y1 for draw in draws]
    fill          = [draw['fill'] for draw in draws]
    #even_odd      = [draw['even_odd'] for draw in draws]
    #seqno         = [draw['seqno'] for draw in draws]
    #layer         = [draw['layer'] for draw in draws]
    #stroke_opacity= [draw['stroke_opacity'] for draw in draws]

    draw_dict = {'item_types':item_types,
    'fill_opacity':fill_opacity,"fill":fill, "r":r,
    "g":g, "b":b, 'x0':x0, 'y0':y0,'x1':x1,'y1':y1 }
    draw_df=pd.DataFrame(draw_dict)
    draw_df["w"] = draw_df.x1 - draw_df.x0
    draw_df["h"] = draw_df.y1 - draw_df.y0

    return pd.DataFrame(draw_dict)


def check_year_fills(examDir: Path):
    '''
    This is a function to confirm that there have not been subtle colour or form changes
    in the drawings over the years which might disrupt the extraction processes.
    '''
    dfs = []
    for year in  range(2005,2025):
        fname = f"LC002ALP100EV_{year}.pdf"
        pdf_file = examDir / fname
        page2 = fitz.open(pdf_file)[1]
        page_drawings    = page2.get_drawings()
        df = get_fill_df(page_drawings)[[ "fill_r","fill_g","fill_b"]]
        df = df.drop_duplicates()
        df.index = [f"{year}_{i}" for i in range(len(df.index))]
        df["year"] = [year]*len(df.index)
        dfs.append(df)
    bigDf = pd.concat(dfs)
    return bigDf

def in_the_pink(bbox: tuple, fill_rectangle: Rect):
    x0, y0, x1, y1 = bbox
    block_rect = Rect(x0,y0,x1,y1)
    return  fill_rectangle.contains(block_rect)

def get_fill_colours(doc):
    '''
    This checks the pages of english paper 1 where the texts are, and finds
    all the unique colours used for the bounding boxes of the articles.
    '''
    fill_colours=[]
    for i in range(1,7):
        page_drawings   = doc[i].get_drawings()
        fill_df = get_fill_df(page_drawings)
        if len(fill_df)==0:
            continue
        fill_colour      = fill_df.fill.mode().values[0]
        fill_colours.append(fill_colour)

    return np.unique(fill_colours,axis=0)

def approx_fill(fill1, fill2):
    '''
    This will check if a fill colour is equal to another with a 0.004 tolerance
    for each colour chanel.
    '''
    r1,b1,g1 = fill1
    r2,b2,g2 = fill2
    red   = r1 > r2 -0.004 and r1 < r2 + 0.004
    blue  = b1 > b2 -0.004 and b1 < b2 + 0.004
    green = g1 > g2 -0.004 and g1 < g2 + 0.004
    return red and blue and green
# To Do: confirm the colours for a variety of papers.
# Here is an example of where you could get the colour for the pink background colour.
# drawings  = page.get_drawings()
# pink_fill = drawings[0]['fill']
def get_pink_boundary(drawings, pink_fills):
    """
    Return one rectangle pink fill box in the page, by joining together other overlapping rectangle pink boxes.

    :param drawings: List of drawing objects from get_drawings()
    :param pink_fill: tuple specifying pink colour. (1.0, 0.8980000019073486, 0.9490000009536743) for 2024 P1
    :return: fitz.Rect of pink boundary or None
    """
    # To Do:
    # Only look at pink fill objects which are rectangles
    pinks = [d for d in drawings if d["type"] == "f" and d["fill"] in pink_fills ]

    if not pinks:
        return None

    def in_the_stink(pink):
        '''
        returns True if the given pink is contained in any other pink on the page.
        '''
        return any( other["rect"].contains(pink["rect"])  for other in pinks if other != pink )

    filtered_pinks = [p for p in pinks if not in_the_stink(p)]

    # we subtract (add) 4 to x0 (x1) to account for leading (trailing) whitespace
    x0 = min([p['rect'].x0 for p in filtered_pinks] ) - 4
    y0 = min([p['rect'].y0 for p in filtered_pinks] )
    x1 = max([p['rect'].x1 for p in filtered_pinks] ) + 4
    y1 = max([p['rect'].y1 for p in filtered_pinks] )
    king_pink = fitz.Rect(x0,y0,x1,y1)

    return king_pink
