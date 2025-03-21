import os, sys
import undetected_chromedriver as uc
from   selenium.webdriver.common.by import By
from selenium.webdriver.support.ui  import Select
from time import sleep
import psutil
from papeScrape import close_adobe

def getPaper(driver, year: str , exam: str, subject: str, searchString:str):
    print(driver.title)

    dropDowns = [("MaterialArchive__noTable__sbv__ViewType"         , "Exam Papers" ), 
                 ("MaterialArchive__noTable__sbv__YearSelect"       , year ), 
                 ("MaterialArchive__noTable__sbv__ExaminationSelect", exam),
                 ("MaterialArchive__noTable__sbv__SubjectSelect"    , subject )
                ]
    
    # Do clicking and drop down selection
    for menu, selection in dropDowns:
        print(f"{menu}: {selection}")
        dropdown = driver.find_element(By.ID, menu)
        select   = Select(dropdown)
        select.select_by_visible_text(selection) ; sleep(3)

    # Find correct paper link and download
    paper = driver.find_element(By.XPATH, f"//tr[td[contains(text(), '{searchString}')]]/td[2]//a")
    paperLink = paper.get_attribute("href")
    driver.get(paperLink); sleep(3)
    close_adobe(); sleep(3)
    return driver

def moveFreshFiles(year: str , dl_dir: str, dest: str):
    pdfs =       [i for i in os.listdir(dl_dir) if i.endswith(".pdf")]
    LC_pdfs =    [i for i in pdfs if ("LC" in i) and ("EV" in i)]
    latestPaper = sorted(LC_pdfs, key = lambda x: os.path.getctime(dl_dir+x),reverse=True )[0]   

    file_dest = dest + f"\\{latestPaper.rstrip('.pdf')}_{year}.pdf"
    os.rename(dl_dir + latestPaper, file_dest)
    return 0


if __name__=="__main__":
    if len(sys.argv) < 2:
        print("Provide year or year range:")
        print(f"Example use:\npython {sys.argv[0]} 2014 2016")
        sys.exit(1)
    
    if len(sys.argv) == 2:
        year2 = year1 = sys.argv[1]
    else:
        year1 = sys.argv[1] if sys.argv[1] < sys.argv[2] else sys.argv[2]
        year2 = sys.argv[2] if sys.argv[2] > sys.argv[1] else sys.argv[1]
    
    
    print(f"Downloading papers from {year1} to {year2}")
    url     = "https://www.examinations.ie"
    exam    = "Leaving Certificate"
    subject = "Applied Mathematics"
    dl_dir  = r'C:\Users\DELL\Downloads\\'
    dest    = rf"C:\Users\DELL\Desktop\Exams\applied_maths_h"
    
    
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
    
    
    driver.get(url)                                                                 ; sleep(20)
    driver.get(url+"/exammaterialarchive")                                          ; sleep(5)
    driver.find_element(By.ID, "MaterialArchive__noTable__cbv__AgreeCheck").click() ; sleep(3)
    
    searchString="Higher Level (EV)"
    for year in range(int(year1), int(year2)+1):
        print(f"year: {year}")
        getPaper(driver, str(year), exam, subject,searchString) 
        moveFreshFiles(year, dl_dir, dest)
        
    
    try:
        driver.close()
        sleep(5)
    except(OSError):
        sleep(1)
    sleep(5)






