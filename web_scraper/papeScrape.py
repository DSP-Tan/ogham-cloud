import sys, os
from pathlib import Path
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
            select.select_by_visible_text(selection) ; sleep(3)

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
