import fitz, itertools
import pandas as pd
import numpy  as np
from numpy.linalg  import norm
from line_utils    import *
from utils         import *
from cluster_utils import print_clusters, calc_cust_dists, calc_cust_clusts
from cluster_utils import custom_cluster_optimise, preproc

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose       import make_column_transformer

def iteration_print(dists, clusts, X,labels, X_cols, word_mask, i_w, verbosity=1):
    '''
    default prints clusters
    1. prints labels.
    2. prints df and labels.
    3. prints df, labels, and distance components
    '''

    X_df      = pd.DataFrame(X,columns=X_cols )
    clusts_df = pd.DataFrame(clusts,columns=X_cols,index=["clust0","clust1"])
    dists_df  = pd.DataFrame(dists,columns=["dist0","dist1"])
    dists_df["labels"] = labels
    X_clusts      = pd.concat((X_df,clusts_df),axis=0)
    X_clusts_dist = pd.concat( (X_clusts, dists_df),axis=1 )
    r01 = norm(clusts[0] - clusts[1])
    X_clusts_dist.loc["clust0","dist0"]=X_clusts_dist.loc["clust1","dist1"]=0
    X_clusts_dist.loc["clust0","dist1"]=X_clusts_dist.loc["clust1","dist0"]=r01
    X_clusts_dist.loc["clust0","labels"]= 0
    X_clusts_dist.loc["clust1","labels"]= 1
    
    if verbosity==2:
        print(X_clusts_dist.head(20),"\n")

    var_contribs = get_variable_diffs(X, clusts, X_cols, word_mask, i_w)
    full_verbose = pd.concat([X_clusts_dist, var_contribs], axis=1)
    if verbosity==3:
        print(full_verbose.head(20), "\n")

    if verbosity==1:
        print(labels[:10])
    
    return None

    



def get_variable_diffs(X, clusts, X_cols, word_mask, i_w):
    """
    Computes squared variable-wise differences between each point and clusters.
    Returns a DataFrame with columns like d0_w, d1_w, d0_y0, etc.
    """
    m, n = X.shape
    k = clusts.shape[0]

    full_vect = X[~word_mask]
    full_diffs = (full_vect[:, np.newaxis, :] - clusts[np.newaxis, :, :]) ** 2

    col_mask    = np.arange(n) != i_w
    small_vect  = np.delete(X[word_mask], i_w, axis=1)
    small_clust = np.delete(clusts, i_w, axis=1)
    small_diffs = (small_vect[:, np.newaxis, :] - small_clust[np.newaxis, :, :]) ** 2
    
    all_diffs = np.zeros((m,k,n))
    all_diffs[~word_mask]                              = full_diffs
    all_diffs[np.ix_(word_mask,np.arange(k),col_mask)] = small_diffs


    var_dfs = []
    for cluster_i in range(k):
        cluster_diff = all_diffs[:, cluster_i, :]
        cluster_df = pd.DataFrame(cluster_diff, columns=[f"d{cluster_i}_{col}" for col in X_cols])
        var_dfs.append(cluster_df)

    return pd.concat(var_dfs, axis=1)
    

pdf_file = "test_pdfs/LC002ALP100EV_2024.pdf"
doc              = fitz.open(pdf_file)
page             = doc[3]
page_dict        = page.get_text("dict",sort=True)
blocks           = page_dict["blocks"]
block            = blocks[6]

lines = [line for line in block["lines"] if not line_is_empty(line)]

pd.set_option("display.float_format", "{:.2f}".format)
df        = get_line_df(lines)

#print("Raw lines dataframe:")
#print(df.head(10))

# We need to choose now the rows where the number of words is below 4
word_mask = df["n_words"].to_numpy() < 4

# These cols of the df are not informative for text-block clustering.
bad_nums = ["n_spans","dL","x1","n_words","h","x0","y1"]
bad_cats = ["font_list","text","mode_font"]

X_df   = preproc(bad_nums, bad_cats, df, font_scale=2)
X      = np.array(X_df)
X_cols = X_df.columns.to_list()

k      = 2
i_w    = X_cols.index("w")

print(f"Preprocessed dataframe of shape {X.shape}:")
print(X_df.head(20),"\n")


best_clustering = np.zeros(X.shape[0])
inertia         = norm(norm(X, axis=1))

# Exclude lines with n_words < 4 from initial clusters list.
for clust0, clust1 in itertools.combinations(X[~word_mask], k):
    clusts = np.array([clust0, clust1])
    
    new_inertia, clusts, labels = custom_cluster_optimise(X,clusts,word_mask, i_w, tol=0.001, verbose=True)
    
    if new_inertia < inertia:
        inertia=new_inertia
        best_clustering =labels
        best_cluster = clusts

    
X_df["cluster"] = pd.Series(best_clustering)
print( X_df.head(20) )

