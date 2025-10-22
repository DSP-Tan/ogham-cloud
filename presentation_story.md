1. Tried various pdf processing (pypdf, pypdf2, pymupdf, docling) , none of which output correctly ordered text, not even ocr.

2. Amongst all those tried, docling (ocr) and PyMuPdf performed the best. 
   - Both made errors in ordering of the text,  but pymupdf came with alot of accurate metadata for the lines (positions, font etc)
   - Because we have modern pdfs for which PyMuPdf is likely to be able to extract well this metadata, we choose PyMuPdf as primary too.
     - Many ocr libraries can give metadata too, but they are not giving exact numbers.
   - Docling will be used for pathological cases where there is aload of needed text contained in an image.
   - Docling can also be used to aid in the detection of hidden text. (This is text which appears in the extraction but which is not
     visible in the document.)

3. PyMuPdf has automatic text blocking.
   - These blocks can be used to id dual col text and then order
   - This oftent worked; often did not- failures due to incorrect blocking together of text lines.

