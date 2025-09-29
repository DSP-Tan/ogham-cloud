import sys, os
from pathlib import Path
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by  import By
from selenium.webdriver.support.ui import Select
import undetected_chromedriver as uc
from time import sleep
from web_scraper.utils import close_adobe, moveFreshPapers

def find_papers(driver):
    rows = driver.find_elements(By.XPATH, "//tr[td[@class='materialbody']]")
    # <input type="hidden" name="fileid" value="LC003ALP100EV.pdf">
    file_names = [ i.get_attribute("value") for i in driver.find_elements(By.XPATH, "//input[@type='hidden'][@name='fileid']") ]
    papers=[]
    for fname, row in zip(file_names, rows):
        paper_desc   = row.find_element(By.XPATH, "./td[1]").text
        link_element = row.find_element(By.XPATH, "./td[2]/a")
        paperLink = link_element.get_attribute("href")


        papers.append((fname, paper_desc,paperLink) )

        print(f"{paper_desc:50} - {fname:25}")
    return papers

valid_subjects = [
    'Accounting', 'Agricultural Economics', 'Agricultural Science', 
    'Ancient Greek', 'Applied Mathematics', 'Arabic', 'Art', 'Biology', 
    'Bulgarian', 'Business', 'Chemistry', 'Classical Studies', 
    'Construction Studies', 'Czech', 'Danish', 'Design & Communication Graphics', 
    'Dutch', 'Economics', 'Engineering', 'English', 'Estonian', 'Finnish', 'French', 
    'Geography', 'German', 'Hebrew Studies', 'History', 'History (Early Modern)', 
    'Home Economics S & S', 'Hungarian', 'Irish', 'Italian', 'Japanese', 'Latin', 
    'Latvian', 'Link Modules', 'Lithuanian', 'Mathematics', 'Modern Greek', 'Music', 
    'Physics', 'Physics & Chemistry', 'Polish', 'Portuguese', 'Religious Education', 
    'Romanian', 'Russian', 'Slovakian', 'Spanish', 'Swedish', 'Technology']

def check_input(argv):
    if len(argv) < 4:
        print("Provide year range and subject:")
        print(f"Example use:\npython {argv[0]} 2014 2016 History")
        sys.exit(1)

    arg1 = int(argv[1])
    arg2 = int(argv[2])
    year1 = arg1 if arg1 < arg2 else arg2
    year2 = arg2 if arg2 > arg1 else arg1
    subject = argv[3]

    if subject.title() not in valid_subjects:
        print("Invalid subject chosen. Possible options:")
        for sub in valid_subjects: print(sub)
        print(f"Usage:\npython {argv[0]} year1 year2 subject")
        print(f"Example use:\npython {argv[0]} 2014 2016 History")
        sys.exit(1)
    
    return year1, year2, subject.title()
    

if __name__=="__main__":
    year1, year2, subject = check_input(sys.argv)

    print(f"Downloading {subject} papers from {year1} to {year2}")

    url      = "https://www.examinations.ie"
    exam     = "Leaving Certificate"
    dl_dir   = Path.home() / 'Downloads'
    exam_dir = Path(__file__).parent.parent / "Exams"
    exam_dir.mkdir(parents=True, exist_ok=True)
    #browse_exe = Path(os.environ["BROWSER"])


    options = uc.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": str(dl_dir),
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
    })
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    #options.binary_location = str(browse_exe)
    driver = uc.Chrome(options=options)

    print(f"Get {url}")
    driver.get(url)                                                                 ; sleep(13)
    driver.get(url+"/exammaterialarchive")                                          ; sleep(5)
    driver.find_element(By.ID, "MaterialArchive__noTable__cbv__AgreeCheck").click() ; sleep(5)

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
            try:
                select.select_by_visible_text(selection) ; sleep(3)
            except NoSuchElementException:
                print(f"Invalid {menu} option {selection}. Possible options:")
                print([option.text for option in select.options])
                raise
                

        papers= find_papers(driver)
        # Download all papers of all levels for this subject for this year. Organise and log.
        for fname, paperDesc, paperLink in papers:
            # Let's just ignore orals for now
            if ".mp3" in fname:
                continue

            level = fname[5:7]
            levels      = { "AL":"Higher", "GL":"Ordinary", "CL":"Common","BL":"Foundation", "ZL":"Sound file"}
            dest        = exam_dir / subject.lower().replace(' ','_') / level
            file_dest   = dest / f"{fname.rstrip('.pdf')}_{year}.pdf"
            file_source = dl_dir / fname
            uri= "N/A"

            # Download only if If you don't already have the file in the downloads folder or the destination folder
            if not ( file_source.exists() or file_dest.exists() ) :
                print(f"Downloading: {paperDesc:35} - {fname:25} to {file_dest}")
                driver.get(paperLink); sleep(3)
                close_adobe(); sleep(3)
                # Write to download ledger
                with open(exam_dir / "download_table.txt", "a") as file:
                    file.write(f"{subject},{level},{year},{paperDesc},{fname}, {paperLink}, {uri}, {str(file_dest)}\n")

            # Organise, rename, upload downloaded files
            dest.mkdir(parents=True, exist_ok=True)
            if file_dest.exists() and file_source.exists():
                file_source.unlink()
            elif file_source.exists() and not file_dest.exists():
                file_source.rename(file_dest)


    driver.close()
    sleep(4)
