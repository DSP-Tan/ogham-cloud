from pdf_scraper.doc_utils   import open_exam
from pdf_scraper.block_utils import is_empty_block, clean_blocks, get_block_text
from pdf_scraper.line_utils import get_line_text, line_is_empty


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
    def clean_block_page_year( year,  n_page,n_block):
        """
        This can be used to check that the function clean_blocks functions correctly
        on blocks with at least two leading empty lines. Which is a common occurence across
        pdfs.
        """
        doc = open_exam(year, "English", "AL", 1)
        page = doc[n_page]
        page_dict  = page.get_text("dict",sort=True)
        blocks     = page_dict["blocks"]
        non_empty_blocks =[block for block in blocks if not is_empty_block(block)]
        
        block = non_empty_blocks[n_block]
        empty_lines = [line for line in block["lines"] if line_is_empty(line) ]
        assert len(empty_lines) > 0

        cleaned_blocks = clean_blocks(non_empty_blocks)
        clean_block = cleaned_blocks[n_block]
        empty_lines = [line for line in clean_block["lines"] if line_is_empty(line) ]
        assert len(empty_lines) == 0


    clean_block_page_year(2024, 1, 3)
    clean_block_page_year(2020, 0, 6)
    clean_block_page_year(2020, 4, 1)


    

if __name__=="__main__":
    #test_empty_block()
    test_clean_blocks_line_removal()