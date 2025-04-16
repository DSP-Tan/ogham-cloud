import fitz, itertools
import pandas as pd
import numpy  as np
from line_utils   import line_is_empty, get_line_df
from cluster_utils import preproc, cluster_optimise
from utils        import *
    
from sklearn.cluster import KMeans

if __name__=="__main__":
    pdf_file         = "test_pdfs/LC002ALP100EV_2024.pdf"
    page_dict        = fitz.open(pdf_file)[3].get_text("dict",sort=True)
    block            = page_dict["blocks"][6]
    lines            = [line for line in block["lines"] if not line_is_empty(line)]
    
    pd.set_option("display.float_format", "{:.2f}".format)
    df        = get_line_df(lines)
    
    # These cols of the df are not informative for text-block clustering.
    bad_nums = ["n_spans","dL","x1","n_words","h","x0","y1"]
    bad_cats = ["font_list","text","mode_font"]
    
    X_df = preproc(bad_nums,bad_cats, df)
    X    = np.array(X_df)
    X_cols = X_df.columns.to_list()
    
    print(f"Preprocessed dataframe of shape {X.shape}:")
    print(X_df.head(6),"\n")

    # initialise clusters - first and last data point are top and bottom of page
    clusts         = X[[0, -1]]
    epsilon = 2.5  
    noise   = np.random.uniform(-epsilon, epsilon, size=clusts.shape)
    clusts  += noise
    init_centroids = clusts
    
    inertia, final_clusts, labels = cluster_optimise(X,clusts, tol=0.001, verbose=True)
    print(f"final inertia: {inertia}\n","--"*40,"\n\n"); 
    
    # Kmeans sklearn
    kmeans = KMeans(n_clusters=2, random_state=42,init=init_centroids, n_init="auto",verbose=True)
    cluster_pred = kmeans.fit_predict(X)
    assert all(cluster_pred==labels)
    print(labels)


