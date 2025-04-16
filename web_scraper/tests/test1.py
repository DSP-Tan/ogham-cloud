import sys, os
import undetected_chromedriver as uc
from   selenium.webdriver.common.by import By
from selenium.webdriver.support.ui  import Select
from time   import sleep
from web_scraper.papeScrape import find_papers

# We are going to look at maths 2020 exam material downloads table
subject ="Mathematics"
exam    = "Leaving Certificate"
url     = "https://www.examinations.ie"
dl_dir  = r'C:\Users\DELL\Downloads\\'
dest    = rf"C:\Users\DELL\Desktop\Exams\{subject.lower().replace(' ','_')}_h"

options = uc.ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": dl_dir,  
    "download.prompt_for_download": False,  
    "plugins.always_open_pdf_externally": True,  
})
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)

test_file= r"C:\Users\DELL\Desktop\Exams\temp\scraper\tests\maths_2020_example.html"
driver.get(test_file)
sleep(50)

papes=find_papers(driver)
print(papes)
sleep(50)
# rows = driver.find_elements(By.XPATH, "//tr[td[@class='materialbody']]")
# for row in rows:
#     paper_name= row.find_element(By.XPATH, "./td[1]").text
#     print(paper_name)
#     link_element = row.find_element(By.XPATH, "./td[2]/a")  
#     paperLink = link_element.get_attribute("href")  
#    if "Higher Level (EV)" in paper_name:
#        cleanName = paper_name.lower().translate( {" ":"_","/":"_", ",":"_", "(":"", ")":""} )
#        print(f"Downloading {cleanName}")
#        #driver.get(paperLink); sleep(3)
#        close_adobe(); sleep(3)
#        moveFreshPapers(year, dl_dir, dest)
#
#driver.close()
#sleep(4)
