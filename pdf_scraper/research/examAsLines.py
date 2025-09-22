import pandas as pd

from pdf_scraper.doc_utils import open_exam, get_doc_line_df
from pdf_scraper.block_utils import clean_blocks
from pdf_scraper.line_utils import print_line_table, get_line_df

# 1. Get all images.
# 2. Get all text lines.
# 3. Identify and Remove captions from text lines.
# 4. Identify and resort dual column text.

def setDualCols(doc_df: pd.DataFrame, page_num:int, bookends: tuple[str]):
    page_df = doc_df[doc_df.page==page_num].copy()
    print("here is page_df")
    print(page_df[["text","x0","y0"]].head(30))
    print("--"*20, "\n\n")
    l1, r1, l2, r2 = bookends
    for line in bookends:
        print(page_df[page_df.text.str.contains(line)].index)
    indices = [page_df[page_df.text.str.contains(line)].index for line in bookends]
    top    = min(indices).values[0]
    bottom = max(indices).values[0]
    dual_cols = page_df.loc[top:bottom].copy()
    dual_cols.sort_values(["x0","y0"],inplace=True)
    dual_cols["category"]="dual_col"
    print("Here are the dual cols")
    print("top")
    print(dual_cols[["text","x0","y0"]].head(10))
    print("bottom")
    print(dual_cols[["text","x0","y0"]].tail(10))
    print("--"*20, "\n\n")
    dual_cols.index = range(top, bottom + 1)

    doc_df.loc[top:bottom] = dual_cols

    return doc_df

year=2001
doc = open_exam(year,"english","al",1)

#import ipdb; ipdb.set_trace()
doc_df = get_doc_line_df(doc)

print(doc_df["text"].iloc[20:50].head(30))

## page 2
#line_l1 = "I flit anxious"
#line_r1 = "yourself be led by the child"
#line_lf = "imagination had not abandoned me"
#line_rf = "lose almost all the time"
#bookends = [line_l1,line_r1, line_lf, line_rf]
#
#doc_df = setDualCols(doc_df, 2, bookends)
#
#print(doc_df["text"].iloc[20:50].head(30))
#
## page 4
#line_l1 = "I had called upon my friend"
#line_r1 = "Peterson was left in possesion"
#line_lf = "streets. The roughs had also fled"
#line_rf = "to be deduced from his hat."
#bookends = [line_l1,line_r1, line_lf, line_rf]
#
#doc_df = setDualCols(doc_df, 4, bookends)
#
## page 5
#line_l1 = "'You are certainly joking, Holmes"
#line_r1 = "ago, and has had no hat since, then he has"
#line_lf = "could afford to buy so expensive a hat three years"
#line_rf = "cheeks, dazed with astonishment"
#bookends = [line_l1,line_r1, line_lf, line_rf]
#
#doc_df = setDualCols(doc_df, 4, bookends)
#
#
## page 6
#line_l1 = "My name is Ariadne"
#line_r1 = "Inflatable habitat modules"
#line_lf = "have as minimal an impact"
#line_rf = "rewards: Quiet. Beauty. Understanding"
#bookends = [line_l1,line_r1, line_lf, line_rf]
#
#doc_df = setDualCols(doc_df, 4, bookends)
