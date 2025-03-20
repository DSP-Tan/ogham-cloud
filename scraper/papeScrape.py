import os, sys
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


if len(sys.argv) < 2:
    print("Provide year or year range:")
    print(f"Example use:\npython {sys.argv[0]} 2014 2016")
    sys.exit(1)

#year = "2012"
year = sys.argv[1]
exam = "Leaving Certificate"
subject = "Mathematics"



options = uc.ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": r"C:\Users\DELL\Desktop",  
    "download.prompt_for_download": False,  
    "plugins.always_open_pdf_externally": True,  
})
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options)


url = "https://www.examinations.ie"
dest= rf"C:\Users\DELL\Desktop\Exams\maths_h"


driver.get(url)                                                                 ; sleep(20)
driver.get(url+"/exammaterialarchive")                                          ; sleep(5)


driver.find_element(By.ID, "MaterialArchive__noTable__cbv__AgreeCheck").click() ; sleep(3)

dropDowns = [("MaterialArchive__noTable__sbv__ViewType","Exam Papers" ), 
             ("MaterialArchive__noTable__sbv__YearSelect",year ), 
             ("MaterialArchive__noTable__sbv__ExaminationSelect",exam),
             ("MaterialArchive__noTable__sbv__SubjectSelect", subject )
            ]

# Do clicking and drop down selection
for menu, selection in dropDowns:
    print(f"{menu}: {selection}")
    dropdown = driver.find_element(By.ID, menu)
    select   = Select(dropdown)
    select.select_by_visible_text(selection) ; sleep(3)


paper1 = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Paper One') and contains(text(), '/ Higher Level (EV)')]]/td[2]//a")
paper1Link = paper1.get_attribute("href")
driver.get(paper1Link); sleep(3)
close_adobe(); sleep(3)

paper2 = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'Paper Two') and contains(text(), '/ Higher Level (EV)')]]/td[2]//a")
paper2Link = paper2.get_attribute("href")
driver.get(paper2Link); sleep(3)
close_adobe(); sleep(3)

for paper in [1,2]:
    for j in [i for i in os.listdir(r"C:\Users\DELL\Downloads") if f"LC003ALP{paper}" in i]:
        file_dest = dest + f"\\{j.rstrip(".pdf")}_{year}_{paper}.pdf"
        os.rename(r'C:\Users\DELL\Downloads\\' + j, file_dest)

driver.close()
sleep(4)