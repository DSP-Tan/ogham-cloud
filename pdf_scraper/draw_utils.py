import fitz
from fitz import Rect

def draw_rectangle_on_page(pdf_path: str, output_pdf: str,  page_number: int, rect: Rect):
    """
    Opens a PDF, draws a dark blue rectangle on the specified page, and saves the modified PDF.
    :param pdf_path: input pdf path; param output_pdf: output pdf path
    :param Rect -> fitz.Rect object rectangle you want to draw on page
    """
    doc  = fitz.open(pdf_path)
    page = doc[page_number]
    page.draw_rect(rect, color=(0, 0, 0.5), width=3)

    out_doc = fitz.open()
    out_doc.insert_pdf(doc, from_page=page_number, to_page=page_number)  
    out_doc.save(output_pdf)
    out_doc.close()
    doc.close()

# To Do: confirm the colours for a variety of papers.
# Here is an example of where you could get the colour for the pink background colour.
# drawings  = page.get_drawings()
# pink_fill = drawings[0]['fill']
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