import pandas as pd

from pdf_scraper.doc_utils import open_exam
from pdf_scraper.block_utils import clean_blocks
from pdf_scraper.line_utils import print_line_table, get_line_df

# 1. Get all images.
# 2. Get all text lines.
# 3. Identify and Remove captions from text lines.
# 4. Identify and resort dual column text.

def get_doc_line_df(doc):
    dfs = []
    for i, page in enumerate(doc):
        page_blocks  = page.get_text("dict",sort=True)["blocks"]

        text_blocks  = [block for block in page_blocks if not block["type"]]
        text_blocks = clean_blocks(text_blocks)

        page_lines   = [ line for block in text_blocks for line in block["lines"]]
        page_df = get_line_df(page_lines)
        page_df["page"] = i+1
        page_df.sort_values("y0",inplace=True)
        dfs.append(page_df)
    doc_df = pd.concat(dfs,ignore_index=True)
    doc_df["dual_col"]=0

    return doc_df


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
    dual_cols["dual_col"]=1
    print("Here are the dual cols")
    print("top")
    print(dual_cols[["text","x0","y0"]].head(10))
    print("bottom")
    print(dual_cols[["text","x0","y0"]].tail(10))
    print("--"*20, "\n\n")
    dual_cols.index = range(top, bottom + 1)

    doc_df.loc[top:bottom] = dual_cols

    return doc_df

year=2020
doc = open_exam(year,"english","al",1)
doc_df = get_doc_line_df(doc)

import ipdb; ipdb.set_trace()
print(doc_df["text"].iloc[20:50].head(30))

line_l1 = "I flit anxious"
line_r1 = "yourself be led by the child"
line_lf = "imagination had not abandoned me"
line_rf = "lose almost all the time"
bookends = [line_l1,line_r1, line_lf, line_rf]

doc_df = setDualCols(doc_df, 2, bookends)

print(doc_df["text"].iloc[20:50].head(30))
