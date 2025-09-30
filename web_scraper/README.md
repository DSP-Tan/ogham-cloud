In this package, the module papeScrape will take an input of a year range and a subject 
name and use Selenium and undetected_chromedriver to scrape all the leaving cert papers 
of this subject within this year range.

The papers will be stored in the directory "Exams" in the parent directory of this one.

The code can work with python 13 and the versions of the packages specified in "../requirements.txt",
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

It is more difficult to run this code from a virtual machine hosted inside of another computer. This is because
communicating with the chrome driver in the host windows environment from the wsl is more complicated. For this
reason, when running this code on a windows computer with wsl, I just use git bash on the windows side.

Depending on the latency of the website server, or your internet connection to it, different wait times are appropriate.
If a wait time is too short this will cause the programme to crash. Careful error handling could manage retries in this
case.
