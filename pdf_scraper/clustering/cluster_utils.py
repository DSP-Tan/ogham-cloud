import numpy as np 
import pandas as pd
from numpy.linalg import norm

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose       import make_column_transformer

def print_clusters(clusts,X_cols, k):
    print( pd.DataFrame(clusts,columns=X_cols,index=["clust0","clust1"]).head(k) )
    
def preproc(cols, df, font_scale=1):
    num_vars = [ col for col in df.select_dtypes(include=np.number).columns if col in cols] 
    cat_vars = [ col for col in df.select_dtypes(include='object').columns  if col in cols] 
    
    ohe = OneHotEncoder(drop="if_binary",sparse_output=False, handle_unknown="error")
    basic_preproc = make_column_transformer(
        (StandardScaler(), num_vars),
        (ohe, cat_vars),
        remainder="drop"
        )
    X      = basic_preproc.fit_transform(df)

    cat_vars = basic_preproc["onehotencoder"].get_feature_names_out().tolist()
    X_df   = pd.DataFrame(X,columns=num_vars + cat_vars)

    font_cols = [col for col in X_df.columns if "font" in col]
    X_df[font_cols] *=font_scale

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



def calc_cust_dists(clusts, X, word_mask, i_w):
    '''
    calculates cutom distance between cluster centres clusts and observations X, with and without
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

# Here we have an issue when we are trying to update the clusters but we have one cluster
# which has only 1 point and that point is one with not enough words to give a meaningful w.

# The code will try to access X[label_word_mask], but label_word_mask will be all Falses, so
# it will be empty and then try to get the mean of that. 
def calc_cust_clusts(X, labels, word_mask, i_w):
    '''
    produce new clusters 0 and 1 where cluster[0,1] are the averages of all points labelled as such.

    For the observations described by word_mask, their line widths do not contribute to the line with averages
    of their associated clusters.

    For each cluster [0,1], the average width is given by ~word_mask and label==[0,1] 
    '''
    m,n = X.shape
    k = np.unique(labels).shape[0]
    col_mask = np.arange(n) != i_w
    clusts=[]
    for i in range(k):
        clust = np.zeros(n)
        label_mask = (labels==i)
        label_word_mask  = label_mask*~word_mask # rows with the right label and enough words to have meaningful widths
        clust[col_mask]  = X[np.ix_(label_mask, col_mask)].mean(axis=0)
        if np.any(label_word_mask):
            clust[~col_mask] = X[np.ix_(label_word_mask, ~col_mask)].mean(axis=0)
        else:
            clust[~col_mask] = 0
        clusts.append(clust)
    return np.vstack(clusts)


def custom_cluster_optimise(X:np.ndarray, clusts:np.ndarray, word_mask:np.array, i_w:int, tol=0.001, verbose=False):
    diff = np.array([1,1])
    k = clusts.shape[0]
    
    if verbose:
        print(f"\n{'iteration':10} {'d_clust0':10} {'d_clust1':10} {'inertia':10}","\n","-"*40); i=0
    while(all(diff>tol)):
        dists       = calc_cust_dists(clusts, X, word_mask,i_w)

        labels      = np.argmin(dists, axis=1)
        inertia     = calc_inertia(dists)
    
        new_clusts  = calc_cust_clusts(X, labels, word_mask, i_w)
        diff        = norm(clusts-new_clusts,axis=1)/norm(clusts,axis = 1)
        clusts      = new_clusts

        if verbose:
            print(f"{i:<10} {diff[0]:<10.4f} {diff[1]:<10.4f} {inertia:<10.2f}"); i+=1

    dists       = calc_cust_dists(clusts, X, word_mask,i_w)
    labels      = np.argmin(dists, axis=1)
    inertia     = calc_inertia(dists)
    return inertia, clusts, labels

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

def iteration_print(dists, clusts, X,labels, X_cols, word_mask, i_w, verbosity=1):
    '''
    This function can be used to print clustering information during the custom clustering algorithm.
    The verbosity will how much is printed. At the highest verbosity it will print the contributions 
    of each variable in X to the distance calculated between X and each cluster. The function 
    get_variable_diffs is used to get these individual contributions. 
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