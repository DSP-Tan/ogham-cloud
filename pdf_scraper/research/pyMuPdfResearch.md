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



# PyMuPDF

This library is considered as an all round good pdf scraping library, and less prone to formatting errors
than pypdf.

Bullet points, question enumerations (i), (ii) all appear the line above the text
they are supposed to precede inline.

Extra newlines seem to be inesrted in question text.

There are always two spaces after full stops.

Questions appear before article text, even though in pdf they appear below.


Using Page.get_text(sorted=True) does not fix the mis-sorted column issue.

# Just using Page.get_text()

## Intro page 1

- Bullet points are printed in the line above the text that belongs to the bullet.

- There is no vertical space between any of the sentences, but the sentences appear all in the correct order.

- The pdf page header is printed last.


## Section I Pages 2 to 7

### Page 2 - Text 1

- Page footers printed first

- Heading of article, inside pink article box, appears after the article body 

- Many spaces printed when going from one column to another. Image is here. We have left column => right column: image => right column text
  - Dual column paragraph is split up.


### Page 3 - Text 1 - Continued

- Pager footer appears first in extracted text.

- Footer to article text appears next (even though it should be below the article text)

- The questions A and B appear before the article text. 

- Extra newlines appear in the text of the questions A and B. Question notations (i), (ii) appear a line before the questions
  they annotate, rather than on the same line.

- In the article text, an empty newline between two pargraphs is missing.
  - This could be detected by the fact that the line preceding the new paragraph ends early.
  - In addition, this last shorter line appears to have lots of white spaces appended to it.

- Dual column pargraph split up. Image at start of column 2.

### Page 4 - Text 2

- The footer of the whole page is again at the top.

- Headers of the article text are correctly before article body.

- The article text is all correctly separated into its paragraphs. 



### Page 5 - Text 2 - Continued

- Many extra newlines brought in, especially in questions.


### Page 6 - Text 3 - Just article and header


- A column ends mid paragraph, the continuation of this paragraph in the next column is given with
  a newline, unlike pypdf, no space before the first word in the extracted text. 

### Page 7

- Extra newlines everywhere in questions text.

- **There is a serious issue on the second paragraph. Here half way through the paragraph the text from the column to the right appears. This occurs at "It was 
undeniably romantic" : this sentence is cut in two and the next paragraph is pasted in.**
  - Note the place where the break in the order occurs "It was" is followed by two
    spaces. It seems double spaces that do not occur after a full stop are often an indication of an issue. Double spaces or single spaces where there should not be spaces. 
  - Also note that in this case the image in the second column is encroaching in the first column. This is no doubt what causes the mix up.


## Section II: Page 8 

No spaces are inserted into words. Improvement over pypdf.
  

## No exam material: pages 9 to 12

These from 9 to 11 we have "There is no examination material on this page". This is correclty 
extracted and can be used to stop reading from the pdf.

The final page is just the credits and I suppose we don't want it.

# Using Page.get_text("dict") with sorting

## Intro page 1

- No Bullet points

- There is no vertical space between any of the sentences, but the sentences appear all in the correct order.


## Section I Pages 2 to 7

### Page 2 - Text 1

- Text all in correct order. 

- Image is not appearing in correct position.


### Page 3 - Text 1 - Continued


- Extra newlines appear in the text of the questions A and B. Question notations (i), (ii) appear a line before the questions
  they annotate, rather than on the same line. The number of marks (15) appears after.

- In the article text, an empty newline between two pargraphs is missing.
  - This could be detected by the fact that the line preceding the new paragraph ends early.
  - In addition, this last shorter line appears to have lots of **white spaces appended to it**.

### Page 4 - Text 2

- The footer of the whole page is again at the top.

- Headers of the article text are correctly before article body.

- The article text is all correctly separated into its paragraphs. 



### Page 5 - Text 2 - Continued

- Many extra newlines brought in, especially in questions.


### Page 6 - Text 3 - Just article and header


- A column ends mid paragraph, the continuation of this paragraph in the next column is given with
  a newline, unlike pypdf, no space before the first word in the extracted text. 

### Page 7

- Extra newlines everywhere in questions text.

- **There is a serious issue on the second paragraph. Here half way through the paragraph the text from the column to the right appears. This occurs at "It was 
undeniably romantic" : this sentence is cut in two and the next paragraph is pasted in.**
  - Note the place where the break in the order occurs "It was" is followed by two
    spaces. It seems double spaces that do not occur after a full stop are often an indication of an issue. Double spaces or single spaces where there should not be spaces. 
  - Also note that in this case the image in the second column is encroaching in the first column. This is no doubt what causes the mix up.


## Section II: Page 8 

No spaces are inserted into words. Improvement over pypdf.
  

## No exam material: pages 9 to 12

These from 9 to 11 we have "There is no examination material on this page". This is correclty 
extracted and can be used to stop reading from the pdf.

The final page is just the credits and I suppose we don't want it.


# Note on bboxes

The bounding box of a text block is where that text block is created. People can create a text block and then 
do ten spaces, giving the impression that a given bit of text starts up much higher than it actually does.

Therefore, when ordering text, it should be ordered in accordance with the appearance of the first non-empty
line, which can be aquired here: 

non_empty_blocks[3]["lines"][5]['spans'][0]["bbox"]

print(table_non_empty)
x0       x1       y0       y1       dx       dy       type  number  first_word
--------------------------------------------------------------------------------
42.54    552.81   42.54    63.64    510.27   21.10    txt   1       SECTION I  
52.80    515.75   91.12    136.50   462.95   45.37    txt   6       TEXT 1 – FA
353.52   477.84   147.60   321.54   124.32   173.94   img   5       --        
47.94    278.85   81.24    767.04   230.91   685.80   txt   2       Parents – a
288.96   544.23   79.37    779.28   255.27   699.91   txt   3       1953.  The 
42.54    555.20   795.94   819.10   512.66   23.16    txt   0       Leaving Cer
--------------------------------------------------------------------------------



non_empty_blocks[0]["lines"][0]['spans'][0]["text"]
'SECTION I                       COMPREHENDING                    (100 marks) '

non_empty_blocks[1]["lines"][0]['spans'][0]["text"]
'TEXT 1 – FAMILY CONNECTIONS AND THE NATURAL WORLD'

ipdb> non_empty_blocks[3]["lines"][0]['spans'][0]["text"]
' '
ipdb> non_empty_blocks[3]["lines"][0]['spans'][1]["text"]
*** IndexError: list index out of range
ipdb> non_empty_blocks[3]["lines"][1]['spans'][0]["text"]
' '
ipdb> non_empty_blocks[3]["lines"][1]['spans'][1]["text"]
*** IndexError: list index out of range
ipdb> non_empty_blocks[3]["lines"][2]['spans'][0]["text"]
' '
ipdb> non_empty_blocks[3]["lines"][2]['spans'][1]["text"]
*** IndexError: list index out of range
ipdb> non_empty_blocks[3]["lines"][3]['spans'][0]["text"]
' '
ipdb> non_empty_blocks[3]["lines"][4]['spans'][0]["text"]
' '
ipdb> non_empty_blocks[3]["lines"][5]['spans'][0]["text"]
'Parents – at least those of my age – don’t like '
ipdb> non_empty_blocks[3]["lines"][5]['spans'][0]["bbox"]
(47.939998626708984, 147.11968994140625, 272.42156982421875, 159.11968994140625)

And it is this y0 , 147, which allows us to place this text after 
"TEXT 1 - ..." which has y0 of 91.12 in order.


you would see something similar for the 1953 block.
==> take the hbox for the first non-empty line.