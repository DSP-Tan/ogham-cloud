In this package, the module papeScrape will take an input of a year range and a subject 
name and use Selenium and undetected_chromedriver to scrape all the leaving cert papers 
of this subject within this year range.

The papers will be stored in the directory "Exams" in the parent directory of this one.

The code can work with python 13 and the versions of the packages specified in ../requirements.txt,
and the version of chrome being driven of **Version 136.0.7103.114 (Build officiel) (64 bits)**

## Example Usage:

python papeSrcape.py 2015 2024 English

### Valid subject names
- English
- Applied Mathematics
- Mathematics
- Irish
... 

## Common issues

If you already have chrome browsers open this can interfere with the correct functioning of the code.

Sometimes the ports on which selenium will want to drive the browser are not available, perhaps for 
reasons above, perhaps for other reasons.