import os
import undetected_chromedriver as uc
from   selenium.webdriver.common.by import By
from selenium.webdriver.support.ui  import Select
from time import sleep

import psutil

def close_adobe():
    # Loop through all running processes and kill Adobe Reader (Acrobat)
    for proc in psutil.process_iter(['pid', 'name']):
        if 'Acrobat' in proc.info['name']:
            proc.kill()


options = uc.ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": r"C:\Users\DELL\Desktop",  # Set your download directory
    "download.prompt_for_download": False,  # Don't ask where to save
    "plugins.always_open_pdf_externally": True,  # Prevent Chrome from opening PDFs
})
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)


url = "https://www.examinations.ie"
dest= rf"C:\Users\DELL\Desktop\Exams\maths_h"

year = "2014"
exam = "Leaving Certificate"
subject = "Mathematics"

driver.get(url)                                                                 ; sleep(20)
 
for year in [  2015, 2017, 2018, 2019, 2020, 2021, 2022]:
    for paper in [1,2]:

        print(f"Year: {year}\nPaper {paper}")

        file_dest = dest + f"\\{year}_p{paper}.pdf"
        paper_url = url  + f"/archive/exampapers/{year}/LC003ALP{paper}00EV.pdf"
        print(f"Checking url: {paper_url}")
        driver.get(paper_url)  
        sleep(10)
        if "404 Not Found" in driver.title:
            print(driver.title)
            continue
        print("Close adobe")
        close_adobe()
        sleep(10)
        print(f"Move file to {file_dest}")
        os.rename(rf"C:\Users\DELL\Downloads\LC003ALP{paper}00EV.pdf", file_dest)
            
# Paper 1 2014: 2014/LC003ALP130EV.pdf
# Paper 2 2014: 2014/LC003ALP230EV.pdf


driver.quit()
sleep(4)