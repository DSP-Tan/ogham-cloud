
# label dual column text
# Page two of year ?

grand_df[grand_df.page==2].text.head(15)


# function
# - takes in 4 lines: top left, top right, bottom left, bottom right
# - makes copy of data frame
# - identifies all lines between these. (max and min index)
# - sorts this part of the data frame
# - returns tuple (sorted data frame, indices)
#
# Then you can reassign this sorted data frame to the original data frame between
# the provided indices.
#
# Or else it can change the passed data frame in place which would be as useufl.


def setDualCols(grand_df: pd.DataFrame, page_num:int, bookends: tuple[str]):
    page_df = grand_df[grand_df.page==page_num].copy()
    l1, r1, l2, r2 = bookends
    for line in bookends:
        print(page_df[page_df.text.str.contains(line)].index)
    indices = [page_df[page_df.text.str.contains(line)].index for line in bookends]
    top    = min(indices).values[0]
    bottom = max(indices).values[0]
    dual_cols = page_df[top:bottom+1].copy()
    dual_cols.sort_values(["x0","y0"],inplace=True)
    dual_cols["daul_col"]=1

    grand_df.loc[top:bottom+1] = dual_cols

    return grand_df


grand_df[grand_df.page==2].text.head(40)


line_l1 = "I flit anxious"
line_r1 = "yourself be led by the child"
line_lf = "imagination had not abandoned me"
line_rf = "lose almost all the time"

bookends = [line_l1,line_r1, line_lf, line_rf]

grand_df = setDualCols(grand_df, 2, bookends)



page2_df = grand_df[grand_df.page==2].copy()
line_l1 = "I flit anxious"
line_r1 = "yourself be led by the child"

line_lf = "imagination had not abandoned me"
line_rf = "lose almost all the time"

bookends = [line_l1,line_r1, line_lf, line_rf]
for line in bookends:
    print(page2_df[page2_df.text.str.contains(line)].index)
indices = [page2_df[page2_df.text.str.contains(line)].index for line in bookends]
top = min(indices)
bottom = max(indices)


page2_text = page2_df[top.values[0]:bottom.values[0]+1].sort_values(["x0","y0"])
page2_text["dual_col"]=1
