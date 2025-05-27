from pdf_scraper.doc_utils   import open_exam
from pdf_scraper.block_utils import is_empty_block, clean_blocks
from pdf_scraper.line_utils import get_line_text


    

def test_empty_block():
    """
    is_empty_block will be tested to see if it detects the 5 known empty
    blocks below.
    """
    doc = open_exam(2016, "English", "AL", 1)
    page = doc[0]
    page_dict  = page.get_text("dict",sort=True)
    blocks    = page_dict["blocks"]

    assert is_empty_block(blocks[0])
    assert is_empty_block(blocks[5])
    assert is_empty_block(blocks[7])
    assert is_empty_block(blocks[8])
    assert is_empty_block(blocks[11])
    assert is_empty_block(blocks[14])

def test_clean_blocks_block_removal():
    """
    Clean blocks should remove any empty blocks, and also within a given block,
    it should remove any empty lines.
    """
    doc = open_exam(2016, "English", "AL", 1)
    page = doc[0]
    page_dict  = page.get_text("dict",sort=True)
    blocks    = page_dict["blocks"]

    cleaned_blocks = clean_blocks(blocks)
    assert len(cleaned_blocks) == len(blocks) - 6
    
def test_clean_blocks_line_removal():
    """
    Clean blocks should remove any empty blocks, and also within a given block,
    it should remove any empty lines.

    The first text block of the 2024 pdf will contain several empty lines. These
    need to be removed so that the correct visual position of that text block may
    be achieved.
    """
    doc = open_exam(2024, "English", "AL", 1)
    page = doc[1]
    page_dict  = page.get_text("dict",sort=True)
    blocks    = page_dict["blocks"]
    non_empty_blocks =[block for block in blocks if not is_empty_block(block)]

    # looking at the lines of the 4th non empty block, we will see it begins with several
    # empty lines (\n)
    # print_block_table(non_empty_blocks)
    # print_line_table(non_empty_blocks[3]["lines"])
    
    assert get_line_text(non_empty_blocks[3]["lines"][0]).isspace()
    assert get_line_text(non_empty_blocks[3]["lines"][1]).isspace()

    cleaned_blocks = clean_blocks(non_empty_blocks)

    assert not get_line_text(cleaned_blocks[3]["lines"][0]).isspace()
    assert not get_line_text(cleaned_blocks[3]["lines"][1]).isspace()
    

if __name__=="__main__":
    test_empty_block()