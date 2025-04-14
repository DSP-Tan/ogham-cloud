import fitz, itertools
import pandas as pd
import numpy  as np
from numpy.linalg import norm
from line_utils   import line_is_empty, get_line_df
from utils        import *
    
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose       import make_column_transformer
from sklearn.cluster import KMeans

def print_clusters(clusts,X_cols, k):
    print( pd.DataFrame(clusts,columns=X_cols,index=["clust0","clust1"]).head(k) )
    
def preproc(bad_nums,bad_cats, df):
    num_vars = [ col for col in df.select_dtypes(include=np.number).columns if col not in bad_nums ] 
    cat_vars = [ col for col in df.select_dtypes(include='object').columns  if col not in bad_cats ] 
    
    basic_preproc = make_column_transformer(
        (StandardScaler(), num_vars),
        (OneHotEncoder(drop="if_binary",sparse_output=False, handle_unknown="error"), cat_vars),
        remainder="drop"
        )
    X      = basic_preproc.fit_transform(df)
    X_df   = pd.DataFrame(X,columns=num_vars + cat_vars)
    return X_df

def calc_normal_dists(clusts, X ):
    diff   = X[:, np.newaxis, :] - clusts[np.newaxis, :, :]      
    return norm(diff, axis=2)

def calc_inertia(dists):
    min_dists   = np.min(dists, axis=1)
    return min_dists.T@min_dists

def cluster_optimise(X, clusts, tol=0.001, verbose=False):
    diff = np.array([1,1])
    k = clusts.shape[0]
    
    if verbose:
        print(f"{'iteration':10} {'clust0':10} {'clust1':10} {'inertia':10}\n","--"*40,"\n"); i=0
    while(all(diff>tol)):
        dists       = calc_normal_dists(clusts, X)
        labels      = np.argmin(dists, axis=1)
        inertia     = calc_inertia(dists)
    
        new_clusts  = np.vstack([X[labels == i].mean(axis=0) for i in range(k)])
        diff        = norm(clusts-new_clusts,axis=1)/norm(clusts,axis = 1)
        clusts      = new_clusts

        if verbose:
            print(f"{i:<10} {diff[0]:<10.4f} {diff[1]:<10.4f} {inertia:<10.2f}"); i+=1


    # final labels and distance calculations
    dists       = calc_normal_dists(clusts, X)
    labels      = np.argmin(dists, axis=1)
    inertia     = calc_inertia(dists)
    return inertia, clusts, labels


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


