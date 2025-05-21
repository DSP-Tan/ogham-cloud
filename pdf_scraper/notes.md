When you get the bounding box of a block of text, and use that to sort the position of the text, sometimes
the text has loads of empty lines at the start, so that the bbox starts much higher up than the text. This 
gives a false sense of where the text should be in ordering. 

Perhaps you should redetermine the bboxes for each box to be the bboxes of the first and last non-empty lines. 

- loop through the cleaned blocks and re-run get_bbox on them. 

A function which works on "lines" rather than "line" is a block function and not a lines funciton. 

# Working with just lines

We encounter alot of problems because of bad blocking of the text, and bad definition of the bounding boxes of
this text. Perhaps we could just work purely with the non-empty-lines. 

# Separating dual column text and its header

- the dual column text could be better identified. 
- so far it checks just in_the_pink and column width. 
- If there is a short enough header this will be clumped in and cause problems downstream. 
- You could separate out these headers by looking at the font, text size, etc. 

## Print dual column text as dual column

We could consider doing this, could be done just with a print and an f string with width specifiers. 


# Organisation of utils

You need to really have a think about when something qualifies as a line function or a block
function. 

# Organisation of code 

As the code was developed as it was being tested, it is perhaps not being used in the most efficient
way. 

For example if all the lines and blocks were cleaned of empty lines and blocks, then the preceeding code
can be simplified. 

An assert check for only non-empty lines could be used in a function insteada if you want to do that, rather
than the current list comprehension that you use. 

# Short cuts taken

The major weakness of this code is how the dual column blocks are identified and sorted. This will break
if there is a short enough title in the pink box. (It does.)


# Bad blocking

Once the blocks are cleaned of empty lines, you can run over them and do a splitting anywhere there is
a discontinuity. 


# Using decision tree to clasify lines

We have already tried to use clustering to limited effect. But this however was when we were still focusing
on blocked text. 

1. Get for each page all lines. Maybe get all lines for all pages. 

2. Get the line_df, enriched with page number, as this is informative. 

3. Label the lines according to their entities for 3-5 exams. 

4. Train decision tree on this. 

5. Use decision tree to predict for other papers. 

- This is better as we simply let the decision tree learn all these rules
  and exceptions that we are running up against in the traditional programming approach. o

- This can then be more generalisable for the other papers. 
