import pandas as pd
import numpy  as np
from pdf_scraper.clustering.cluster_utils import preproc
from sklearn.cluster import DBSCAN
from pdf_scraper.doc_utils import open_exam, get_doc_line_df
from pathlib import Path

if __name__=="__main__":
    doc          = open_exam(2024)
    df = get_doc_line_df(doc)
    page_df = df[df.page==2].copy()
    pd.set_option("display.float_format", "{:.2f}".format)

    print(page_df[["text","w","y0","x0","dL","mode_font", "font_size"]].head(50))
    print(page_df[["text","w","y0","x0","dL","mode_font", "font_size"]].tail(20))
    page_df.dropna(inplace=True)
    
    #cols = ['x0', 'y0', 'y1', 'w','x1', 'font_size', 'mode_font']
    cols = ['x0', 'y0', 'font_size', 'mode_font']
    
    X_df   = preproc(cols, page_df, font_scale=0.07)
    print(X_df.head(50))

    X      = np.array(X_df)
    X_cols = X_df.columns.to_list()

    y0_idx = X_df.columns.get_loc("y0")

    # Extract the y0 column
    y0_values = X[:, y0_idx]
    
    dL = np.empty_like(y0_values)
    dL[:-1] = y0_values[1:] - y0_values[:-1]
    dL[-1]  = np.nan  # Final element as NaN

    dbscan = DBSCAN(eps=0.14, min_samples=3)
    dbscan.fit(X)
    page_df["cluster"] = dbscan.labels_
    page_df["dL"]  = dL
    print(np.unique(dbscan.labels_))
    print(page_df[["text"]+cols+["dL","cluster"]].head(50))

    to_print = ["text"]+cols+["dL"]
    for i in np.unique(dbscan.labels_):
        print(f"Cluster {i}")
        print(page_df.loc[page_df.cluster==i,to_print].head(50))
        print("--"*40)
        print("--"*40)


    #import ipdb; ipdb.set_trace()


    
    
    
        

