import fitz, itertools
import pandas as pd
import numpy  as np
from numpy.linalg import norm
from line_utils   import *
from utils        import *

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

    print_clusters(new_clusts, X_cols, k)
    if verbosity==1:
        print(labels[:10])
    
    return None





def print_clusters(clusts,X_cols, k):
    print("Clusters:\n", pd.DataFrame(clusts,columns=X_cols,index=["clust0","clust1"]).head(k) )
    

def calc_dists(clusts, X, word_mask, i_w):
    '''
    calculates distance between cluster centres clusts and observations X, with and without
    variable specified as i_w th column of X, with rows distributed according to word_mask
    '''
    k = clusts.shape[0]
    m, n = X.shape
    
    full_vect  = X[~word_mask, :]
    
    full_diff   = full_vect[:, np.newaxis, :] - clusts[np.newaxis, :, :]      #  (m_full, 2, n)
    full_dists  = norm(full_diff, axis=2)                                     #  (m_full, 2)
    
    small_vect  = np.delete(X[word_mask], i_w, axis=1)
    small_clust = np.delete(clusts,       i_w, axis=1)
    
    small_diff   = small_vect[:, np.newaxis, :] - small_clust[np.newaxis, :, :]  #  (m_small, 2, n -1)
    small_dists  = norm(small_diff, axis=2)                                      #  (m_small, 2)
    
    dists = np.empty((m, k))
    dists[word_mask]  = small_dists
    dists[~word_mask] = full_dists

    return dists

def get_variable_diffs(X, clusts, X_cols, word_mask, i_w):
    """
    Computes squared variable-wise differences between each point and clusters.
    Returns a DataFrame with columns like d0_w, d1_w, d0_y0, etc.
    """
    m, n = X.shape
    k = clusts.shape[0]

    full_vect = X[~word_mask]
    full_diffs = (full_vect[:, np.newaxis, :] - clusts[np.newaxis, :, :]) ** 2

    small_vect  = np.delete(X[word_mask], i_w, axis=1)
    small_clust = np.delete(clusts, i_w, axis=1)
    small_diffs = (small_vect[:, np.newaxis, :] - small_clust[np.newaxis, :, :]) ** 2

    all_diffs = np.empty((m, k, n))
    all_diffs[~word_mask] = full_diffs
    # Fill small_diffs into all_diffs for word_mask rows (with width excluded)
    # We must check below tomorrow pretty sure they are the same.
    all_diffs[word_mask, :, :i_w]   = small_diffs[:, :, :i_w]
    all_diffs[word_mask, :, i_w+1:] = small_diffs[:, :, i_w:]
    all_diffs[word_mask, :, i_w]    = 0  


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

# We need to choose now the rows where the number of words is below 4
word_mask = df["n_words"].to_numpy() < 4

#print("Raw lines dataframe:")
#print(df.head(10))

# These cols of the df are not informative for text-block clustering.
#bad_nums = ["n_spans","dL","x1","n_words"]
#bad_cats = ["font_list","text"]
bad_nums = ["n_spans","dL","x1","n_words","h","x0","y1"]
bad_cats = ["font_list","text","mode_font"]

num_vars = [ col for col in df.select_dtypes(include=np.number).columns if col not in bad_nums ] 
cat_vars = [ col for col in df.select_dtypes(include='object').columns  if col not in bad_cats ] 

basic_preproc = make_column_transformer(
    (StandardScaler(), num_vars),
    (OneHotEncoder(drop="if_binary",sparse_output=False, handle_unknown="error"), cat_vars),
    remainder="drop"
    )
X_cols = num_vars + cat_vars 
X      = basic_preproc.fit_transform(df)

k      = 2
m, n   = X.shape
i_w    = X_cols.index("w")
i_font = X_cols.index("common_font")

# Scale font importance
X[:,i_font] *=3

X_df   = pd.DataFrame(X,columns=X_cols )
print(f"Preprocessed dataframe of shape {X.shape}:")
print(X_df.head(20),"\n")


# initialise clusters - first and last data point are top and bottom of page
clusts    = X[[0, m-1]]
clusts    = X[np.random.choice(m, size=2, replace=False)]
epsilon = 2.5  
noise   = np.random.uniform(-epsilon, epsilon, size=clusts.shape)
clusts += noise

for clust0, clust1 in itertools.combinations(X, k):
    clusts = np.array([clust0, clust1])

    print_clusters(clusts, X_cols, k)
    
    diff            = np.array([1,1])
    inertia         = norm(norm(X, axis=1))
    best_clustering = np.zeros(X.shape[0])
    tol  = 0.001
    i=0
    verbose = False
    
    while(all(diff>tol)):
    
        dists       = calc_dists(clusts, X, word_mask,i_w)
        labels      = np.argmin(dists, axis=1)
    
        new_clusts = np.vstack([X[labels == i].mean(axis=0) for i in range(k)])
        
        norm_change =  norm(clusts-new_clusts,axis=1)
        norm_clust  =  norm(clusts,axis = 1)
        diff        = norm_change/norm_clust
        
    
        if verbose: iteration_print(dists, clusts, X, labels, X_cols, word_mask, i_w, 3)
        print(f"{i} {diff}\n","--"*40,"\n\n"); i+=1
        clusts = new_clusts

    
    # final labels and distance calculations
    dists  = calc_dists(clusts, X, word_mask,i_w)
    labels = np.argmin(dists, axis=1)
    min_dists   = np.min(dists, axis=1)
    new_inertia = norm(min_dists)
    if new_inertia < inertia:
        inertia=new_inertia
        best_clustering =labels
        best_cluster = clusts

    
iteration_print(dists, best_cluster, X, best_clustering, X_cols, word_mask, i_w, 3)   
#X_df["cluster"] = pd.Series(best_clustering)
#print( X_df.head(20) )

