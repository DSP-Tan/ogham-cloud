import psutil
def close_adobe():
    # Loop through all running processes and kill Adobe Reader (Acrobat)
    for proc in psutil.process_iter(['pid', 'name']):
        if 'Acrobat' in proc.info['name']:
            proc.kill()


import os 
def moveFreshPapers(year: str , dl_dir: str, dest: str):
    pdfs =       [i for i in os.listdir(dl_dir) if i.endswith(".pdf")]
    LC_pdfs =    [i for i in pdfs if ("LC" in i) and ("EV" in i)]
    latestPaper = sorted(LC_pdfs, key = lambda x: os.path.getctime(dl_dir+x),reverse=True )[0]   

    os.makedirs(dest,exist_ok=True)
    file_dest = dest + f"\\{latestPaper.rstrip('.pdf')}_{year}.pdf"
    if os.path.exists(file_dest):
        os.remove(dl_dir + latestPaper)
    else:
        os.rename(dl_dir + latestPaper, file_dest)
    return 0