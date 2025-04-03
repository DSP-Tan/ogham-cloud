import fitz  
from fitz import Rect
import sys

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
    table.extend( ["--"*40,"\n"*2] )
    block_table = "\n".join(table)
    print(block_table)
    return block_table

def split_block(block):
    # if a block is comprised of several lines, and all the spans of some lines have
    # a typical width and a typical font, and then subsequent lines have different widths
    # and different fonts, make me two blocks of this block.
    """
    Splits a block into two if there is a significant change in text style or width.
    
    :param block: A dictionary containing a block of text from PyMuPDF's get_text("dict")
    :return: A list of one or two blocks, depending on whether a split is detected.
    """
    lines = block.get("lines", [])
    
    if not lines:
        return [block]
    
    first_line_spans = lines[0].get("spans", [])
    if not first_line_spans:
        return [block]
    
    reference_width = first_line_spans[0].get("width", 0)
    reference_font = first_line_spans[0].get("font", "")
    
    split_index = -1
    
    for i, line in enumerate(lines[1:], start=1):
        for span in line.get("spans", []):
            if span.get("width", 0) != reference_width or span.get("font", "") != reference_font:
                split_index = i
                break
        if split_index != -1:
            break
    
    if split_index == -1:
        return [block]  # No split needed
    
    block_1 = {**block, "lines": lines[:split_index]}
    block_2 = {**block, "lines": lines[split_index:]}
    
    return [block_1, block_2]
