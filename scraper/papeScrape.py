import os, sys
import undetected_chromedriver as uc
from   selenium.webdriver.common.by import By
from selenium.webdriver.support.ui  import Select
from time import sleep
from utils import close_adobe, moveFreshFiles

if len(sys.argv) < 2:
    print("Provide year or year range:")
    print(f"Example use:\npython {sys.argv[0]} 2014 2016")
    sys.exit(1)

year = sys.argv[1]
url     = "https://www.examinations.ie"
exam    = "Leaving Certificate"
subject = "Mathematics"
dl_dir  = r'C:\Users\DELL\Downloads\\'
dest    = rf"C:\Users\DELL\Desktop\Exams\maths_h"

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

for pape in [1,2]:
    word = { 1:"One", 2:"Two"}[pape]
    paper = driver.find_element(By.XPATH, f"//tr[td[contains(text(), 'Paper {word}') and contains(text(), '/ Higher Level (EV)')]]/td[2]//a")
    paperLink = paper.get_attribute("href")
    driver.get(paperLink); sleep(3)
    close_adobe(); sleep(3)

    moveFreshFiles(year, dl_dir, dest)
    #for j in [i for i in os.listdir(r"C:\Users\DELL\Downloads") if f"LC003ALP{pape}" in i]:
    #    file_dest = dest + f"\\{j.rstrip('.pdf')}_{year}_{pape}.pdf"
    #    os.rename(r'C:\Users\DELL\Downloads\\' + j, file_dest)

driver.close()
sleep(4)