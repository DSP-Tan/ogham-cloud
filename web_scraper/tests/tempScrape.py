import sys,os
import undetected_chromedriver as uc
from   selenium.webdriver.common.by import By
from selenium.webdriver.support.ui  import Select
from time import sleep
from utils import close_adobe, moveFreshPapers

def find_papers(driver):
    rows = driver.find_elements(By.XPATH, "//tr[td[@class='materialbody']]")
    file_names = [ i.get_attribute("value") for i in driver.find_elements(By.XPATH, "//input[@type='hidden'][@name='fileid']") ]
    papers=[]
    for fname, row in zip(file_names, rows):
        paper_name= row.find_element(By.XPATH, "./td[1]").text
        print(paper_name)
        link_element = row.find_element(By.XPATH, "./td[2]/a")  
        paperLink = link_element.get_attribute("href")  
        transTab = str.maketrans({" ":"_","/":"_", ",":"_", "(":"", ")":""})
        cleanName = paper_name.lower().translate( transTab )
        papers.append((fname, cleanName,paperLink) )
    return papers


# <input type="hidden" name="fileid" value="LC003ALP100EV.pdf">
# inputs = driver.find_elements(By.XPATH, "//input[@type='hidden'][@name='fileid']")
# inputs[0].get_attribute("value")



if __name__=="__main__":
    if len(sys.argv) < 3:
        print("Provide year range and subject:")
        print(f"Example use:\npython {sys.argv[0]} 2014 2016 History")
        sys.exit(1)

    #To Do: test for valid year input, and test for valid subject against list of subjects.
    year1 = sys.argv[1] if sys.argv[1] < sys.argv[2] else sys.argv[2]
    year2 = sys.argv[2] if sys.argv[2] > sys.argv[1] else sys.argv[1]
    subject = sys.argv[3]
    
    print(f"Downloading papers from {year1} to {year2}")
    
    url     = "https://www.examinations.ie"
    exam    = "Leaving Certificate"
    dl_dir  = r'C:\Users\DELL\Downloads\\'
    dest    = rf"C:\Users\DELL\Desktop\Exams\{subject.lower().replace(' ','_')}_h"
    
    options = uc.ChromeOptions()
    options.binary_location = os.environ["BROWSER"]  
    options.add_experimental_option("prefs", {
        "download.default_directory": r"C:\Users\DELL\Desktop",  
        "download.prompt_for_download": False,  
        "plugins.always_open_pdf_externally": True,  
    })
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    
    print(f"Get {url}")
    driver.get(url)                                                                 ; sleep(20)
    driver.get(url+"/exammaterialarchive")                                          ; sleep(5)
    driver.find_element(By.ID, "MaterialArchive__noTable__cbv__AgreeCheck").click() ; sleep(3)
    
    for year in range(int(year1), int(year2)+1):
        dropDowns = [("MaterialArchive__noTable__sbv__ViewType","Exam Papers" ), 
                     ("MaterialArchive__noTable__sbv__YearSelect",str(year) ), 
                     ("MaterialArchive__noTable__sbv__ExaminationSelect",exam),
                     ("MaterialArchive__noTable__sbv__SubjectSelect", subject )
                    ]
    
        # Do clicking and drop down selection
        for menu, selection in dropDowns:
            print(f"{menu}: {selection}")
            dropdown = driver.find_element(By.ID, menu)
            select   = Select(dropdown)
            select.select_by_visible_text(selection) ; sleep(3)

        rows = driver.find_elements(By.XPATH, "//tr[td[@class='materialbody']]")
        for row in rows:
            paper_name= row.find_element(By.XPATH, "./td[1]").text
            print(paper_name)
            link_element = row.find_element(By.XPATH, "./td[2]/a")  
            paperLink = link_element.get_attribute("href")  
            if "Higher Level (EV)" in paper_name:
                cleanName = paper_name.lower().translate( {" ":"_","/":"_", ",":"_", "(":"", ")":""} )
                print(f"Downloading {cleanName}")
                #driver.get(paperLink); sleep(3)
                close_adobe(); sleep(3)
                moveFreshPapers(year, dl_dir, dest)
    
    driver.close()
    sleep(4)

