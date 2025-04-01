In this document we will report on the efficacy of different pdf scraping python libraries
for different use cases.

# Bench mark tasks

- Extract each question and all its text. Importance here is separating out each question.
  - Will need to find where the actual questions start. Will need some marker for that.

- Are paragraphs properly separated? (Do they really need to be?)

- Are multi-column paragraphs correctly resolved? (When a paragraph continues from the end of one
  column to the start of the next.)

- Get all text and all images in a given question.

- Get text, image, and equation in a given question.



# PyPDF

This library is chosen because it was featured in the first python udemy course I ever did. "Zero to hero" python
with jose portilla. He ahd reccommended PyPDF2, which we used first, but actually the main development ant latest
version of this package is now in pypdf. Pypdf fixed many issues that we had encountered with pypdf2.

General remark: headers and footers of article text do not appear in the correct
order in the extracted text. All page footers are appearing first in the extracted
text. This is not too serious.

Article text headers/titles are appearing after the article column text.

There are two spaces after each fullstop.

- again the identification criterion for the article text would be **many** lines together all with a fixed max width;
  and also it would be useful to have an average minium width for each block, to account for half and ending sentences.

- Sentences at the end can be shorter.
- Text blocks all appear together.

## Intro page 1

Very well extracted. The only issue is that the very first bits of text at the top
of the pdf "2024.M.11                      2024L002A1EL" were printed as the last
line of the page 1.

- This is the last line. And it is a line prepended by two spaces.

## Section I Pages 2 to 7

### Page 2 - Text 1

- page footer printed first in extracted text

- Heading of article, appearing above in pdf, appears after the article in the extracted text.

- Many spaces printed when going from one column to another. Image is here. We have left column => right column: image => right column text
  - Dual column paragraph is split up.


### Page 3 - Text 1 - Continued

- Pager footer appears first in extracted text.

- Footer to article text appears next (even though it should be below the article text)

- The questions A and B appear before the article text. There are some extra spaces in the text of the questions.

- In the article text, an empty newline between two pargraphs is missing.
  - This could be detected by the fact that the line preceding the new paragraph ends early.
  - In addition, this last shorter line appears to have lots of white spaces appended to it.

- Dual column pargraph again split up. Image at start of column 2.

### Page 4 - Text 2

- The footer of the whole page is again at the top.

- Headers of the question text are correctly ordered.

- The article text is all correctly separated into its paragraphs. 




### Page 5 - Text 2 - Continued

- Page footer of pdf is at top of extracted text.

- The article footer is just underneath the page footers in the extracted text. ("N.B ...")

- Question A and Question B are in the correct order.

- Article text, which has one column continuing on next page, is all correctly extracted, an improvement on PyPDF2


### Page 6 - Text 3

- pdf page footer appears at top of extracted text file.

- A column ends mid paragraph, the continuation of this paragraph in the next column is given with
  a newline, and with a space before the first word in the extracted text. 

### Page 7

- pdf page footer appears at top of extracted text file. Second is article footer

- Questions appear before article text even though in pdf they appear after.

- **There is a serious issue on the second paragraph. Here half way through the paragraph the text from the column to the right appears. This occurs at "It was 
undeniably romantic" : this sentence is cut in two and the next paragraph is pasted in.**
  - Note the place where the break in the order occurs "It was" is followed by two
    spaces. It seems double spaces that do not occur after a full stop are often an indication of an issue. Double spaces or single spaces where there should not be spaces. 


## Section II: Page 8 

- pdf page footer appears at top of extracted text file. 

- Two instances where assignments are incorrectly filled with spaces, and at one point a space appears in a word:
          Write a pe rsonal essay in which you reflect on some of the aspects of life you find puzzling. 
  

### No exam material: pages 9 to 12

These from 9 to 11 we have "There is no examination material on this page". This is correclty 
extracted and can be used to stop reading from the pdf.

The final page is just the credits and I suppose we don't want it.
