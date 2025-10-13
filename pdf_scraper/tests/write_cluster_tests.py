import pandas as pd
import numpy as np
from pathlib import Path
from fitz import Rect

from pdf_scraper.doc_utils   import (open_exam, get_doc_line_df, 
                                     get_images, preproc_images,  assign_in_image_captions, 
                                     identify_all_page_clusters, enrich_doc_df_with_images)
from pdf_scraper.line_utils import clean_line_df


paper=1
level="al"
subject="english"


year=2001
page = 4

# (2001,6) This is not really a good clustering. The dual cols are split as we would like, but the title and the subtitle
# are grouped together because the eps_y obtained from this page is too small. A solution is to determine a font-based eps_y,
# or a document wide eps_y.
# (2011, 6) Image causes problems, but excluding image fixes. Title and subtitle together. Otherwise good.
# See notebook difficult_cases.ipynb for other test choices.
# (2025, 6) This is bad clustering caused by invisible lines. We include here just to fix current behaviour.
# For the likes of (2025, 6) this script will need to be re-run when the issue is fixed.
for year, page in [(2001,2), (2001,3), (2001,4), (2001,6), (2011, 6), (2024,4), (2025, 6)]:
    doc = open_exam(year, subject, level,paper)
    df = get_doc_line_df(doc)
    images = get_images(doc)
    images = preproc_images(images)
    assign_in_image_captions(df,images)
    df = clean_line_df(df)
    df = enrich_doc_df_with_images(df,images)
    identify_all_page_clusters(df,2.0/3.0, 1.15, True)
    
    page_df = df[df.page==page].copy()
    test_df = page_df[["text","cluster"]].sort_values(by="cluster")
    out_dir = Path(__file__).parent.resolve() / Path(f"resources/expected_clusters")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{subject}_{level}_{paper}_{year}_{page}.csv"
    test_df.to_csv(out_file)

