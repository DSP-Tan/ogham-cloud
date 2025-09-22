import numpy as np 
import pandas as pd
from numpy.linalg import norm

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose       import make_column_transformer
from sklearn.metrics       import pairwise_distances
from sklearn.cluster       import DBSCAN

from pdf_scraper.line_utils import get_category_boxes

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


def find_y0_dL(df: pd.DataFrame, cat: str = "" ) -> float:
    """
    This will find the median spacing between y0 values for all the pages of the 
    document that contain an instance a line of category "cat".

    Note: This method is deprecated for finding the median dL between lines. It does not
    give good values when dual columns are involved, particularly two columns slightly offset
    in y. See "get_vert_neigh_dist" instead. 
    """
    dLs = []
    pages = np.unique(df[df[cat]==1].page) if cat else np.unique(df.page)
    for page in pages:
        page_df = df[(df.page==page)].copy()
        page_df.sort_values(by=["x0","y0"],inplace=True)
        diffs = page_df.y0.diff().dropna()
        diffs = diffs[diffs !=0]
        dLs.append(diffs)
    dL = np.median( np.concat(dLs, axis=0) )
    return dL


def get_vert_neigh_dist(row, dff, dir):
    """
    This function returns the distance to the next line , in the direction dirr.

    If dir is just one dimensional, "y0", the y0 difference with next line will be calculated.
    If dir is the two dimensional ["y0","y1"], the end to end next line distance will be calculated.

    "next line" means the line closest in dir, but on the same side of the document. This means it will
    not look for the next line in a parallel column of text.

    Examples: 
    dLs = dff.apply(lambda row: get_vert_neigh_dist(row, dff, ['y0','y1']),axis=1)
    dy0s = dff.apply(lambda row: get_vert_neigh_dist(row, dff, ['y0']),axis=1)
    """
    same_side  = (row.x0 < middle )*(dff.x0 < middle) == True
    below      = (dff.y0 > row.y0)
    mask       = same_side & below
    other_rows = dff.loc[mask , dir ]
    metric     = "euclidean" if len(dir)==1 else df_bbox_dist

    if len(other_rows)==0:
        return np.nan

    
    return pairwise_distances(row[dir].values.reshape(1,-1) , Y=other_rows.values,  metric=metric).min()

def split_cluster(df: pd.DataFrame, i_clust: int,  metric, eps, dir, verbose=False):
    if verbose: print(f"scanning cluster {i_clust}")
    last_id  = df.cluster.max()
    clust_df = df[df.cluster==i_clust].copy()

    X             = pairwise_distances(clust_df[dir],metric=metric)
    scan          = DBSCAN(eps=eps, min_samples=1,metric="precomputed")
    labels        = scan.fit_predict(X)
    
    unique_labels = np.unique(labels)
    n_labels = len( unique_labels )
    if n_labels ==1:
        if verbose: print("No split")
        return  unique_labels
    
    labels[labels!=0] += last_id
    labels[labels==0] += i_clust

    df.loc[clust_df.index, "cluster"] = labels
    unique_labels = np.unique(labels)
    
    if verbose: print(f"Cluster {i_clust} split {dir} with eps = {round(eps)} into {n_labels} clusters: {unique_labels}")

    return unique_labels

def hdbscan(df: pd.DataFrame, max_iter: int, eps_x: float, eps_y: float, metric, verbose=False):
    dir1 = ["y0"] if metric=="euclidean" else ["y0","y1"]
    dir2 = ["x0"] if metric=="euclidean" else ["x0","x1"]
    dirs = ((dir1, eps_y), (dir2,eps_x))
    i_dir, n_fail, df["cluster"] = (0, 0, 0)
    N_clusters=1
    rectangies, labia = ([], [])
    
    for n_loop in range(max_iter):
        # assign the direction and cluster numbers for this round of scanning
        dir, eps  = dirs[i_dir]
    
        if verbose: print(f"Full Scan {n_loop} in {dir} with eps={eps:<6.2f}")
        if n_fail >=4:
            break
        # Loop over all current clusters and break up in dir
        for i_clust in np.unique(df.cluster):
            split_cluster(df, i_clust, metric, eps, dir, verbose=verbose)
                
        labelos = np.unique(df.cluster)
        n_clusters = len(labelos)
        i_dir = 1 if i_dir==0 else 0
    
        if n_clusters == N_clusters:
            n_fail +=1
            continue
        else:
            n_fail = 0
            N_clusters = n_clusters
    
        rectangies.append(get_category_boxes(df, 'cluster') )
        labia.append( np.unique(df.cluster) )
        if verbose: print(f"Total {n_clusters} clusters: {labelos}")

    return ( rectangies, labia )