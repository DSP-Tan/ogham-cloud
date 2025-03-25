# Irregularities in exam archives for different subjects
So far we have only seen the irregularities between maths and applied maths. The first quick and dirty solution as
we progress towards an mvp will be to have two different scripts on for maths and one for applied maths, which can 
be refactored into one script later on. The differences are in how the papers are named in the archive, and how many
papers there are to download.


## Presence of two papers
There is a paper 1 and paper 2 in maths (and english also as far as I know) but not for applied
mathematics.

This is why a screenshot of the exam paper download drop down will be useful (driver.print_screen) , as it will show up
any aberrations from what we have expected.

These irregularities in the structures of the exam format are a reason to very carefully do the error handling and reporting on the "find_element" part of the code.

## Project maths
Over the last 10+ years there was a change to the maths syllabus with the introduction of project maths.
This changes how the papers are presented in examinations.ie. In 2014 there is both project maths and normal
maths papers. In 2015 there is just project. 

These differences must be examined to see what it means. Was project maths introduced, trialled, and then dropped?
Or was it maintained forever, and referred to as simply maths since it's official adoption.

# Archive function

At the moment we are storing the files locally. But we will want to have them on google cloud storage for convenience
and safety and remote accessibility. We can have an archive function which takes a variable set to cloud or local 
which will save them to the cloud or save them locally.

We will also want a function which check what papers are already downloaded, and if they are already downloaded to
not download them again. 

# Error handling and waiting

With Selenium it seems it is very important to wait for the pages to load before you try to find a given
element. I have implemented this with just sleeps, but there are selenium native ways of doing it that
must be more appropriate. In addition to that, if we put our find_elements inside a while loop with a try
except, we can perhaps keep trying to get the element until we find it or a certain number of tries is exceeded.