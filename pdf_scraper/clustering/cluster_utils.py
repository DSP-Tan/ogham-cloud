import numpy as np 
import pandas as pd

from sklearn.metrics       import pairwise_distances
from sklearn.cluster       import DBSCAN
from sklearn.utils._param_validation import InvalidParameterError

from pdf_scraper.line_utils import get_category_boxes
from pdf_scraper.line_utils import get_df_bbox
from pdf_scraper.general_utils import df_bbox_dist


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


def get_vert_neigh_dist(row, df, dir):
    """
    This function returns the distance to the next non-overlapping line, in the direction dirr. 
    
    The next line in y0 can still be overlapping if it has a y0 which is greater than previous line, 
    but y1 of the current line (row) is greater than y0 of the new line.

    If there is no non-overlapping line on the same side below the line specified in row, np.nan is returned.

    If dir is just one dimensional, "y0", the y0 difference with next line will be calculated.
    If dir is the two dimensional ["y0","y1"], the end to end next line distance will be calculated.

    "next line" means the line closest in dir, but on the same side of the document. This means it will
    not look for the next line in a parallel column of text.

    Examples: 
    dLs  = dff.apply(lambda row: get_vert_neigh_dist(row, dff, ['y0','y1']),axis=1)
    dy0s = dff.apply(lambda row: get_vert_neigh_dist(row, dff, ['y0']),axis=1)
    """
    same_page = (df.page == row.page)
    page_x0, page_y0, page_x1, page_y1 = get_df_bbox(df[same_page])
    middle = (page_x0 + page_x1)/2
        
    same_side  = (row.x0 < middle ) == (df.x0 < middle) 
    below      = (df.y0 > row.y0)
    mask       = same_side & below & same_page
    
    other_rows = df.loc[mask , dir ]
    metric     = "euclidean" if len(dir)==1 else df_bbox_dist

    if len(other_rows)==0:
        return np.nan
    
    distances = pairwise_distances(row[dir].values.reshape(1,-1) , Y=other_rows.values,  metric=metric)
    distances = distances[distances !=0 ]
    if len(distances)==0:
        return np.nan

    return distances.min()

def nn_line_distance(df, row):
    """
    This returns the next nearest neighbour to a line, using the end-to-end distance metric.
    
    It only looks at lines below the current line to find nearest neighbours. If the next line in 
    y0 overlaps with the current line, the nn_line_distance will be 0; if there is no line beneath 
    the current line on the same side, np.nan is returned.
    """

    same_page  = (row.page == df.page)
    middle     = (df[same_page].x0.min() + df[same_page].x1.max())/2
    same_side  = (row.x0 < middle ) == (df.x0 < middle) 
    below      = (df.y0 > row.y0)
    not_image  = (df.category != "image")

    mask       = same_side & below & not_image
    other_rows = df.loc[mask ]

    if len(other_rows)==0:
        return np.nan
    
    dir= ["y0","y1"]
    distances = pairwise_distances(row[dir].values.reshape(1,-1) , Y=other_rows[dir].values,  metric=df_bbox_dist)
    return distances.min()

def second_nn_line_distance(df, row):
    """
    This returns the second next nearest neighbour to a line, using the end-to-end distance metric.
    
    It only looks at lines below the current line to find nearest neighbours. If the second next line in 
    y0 overlaps with the current line, the nn_line_distance will be 0; if there is less than two lines 
    beneath the current line on the same side, np.nan is returned.
    """

    same_page  = (row.page == df.page)
    middle     = (df[same_page].x0.min() + df[same_page].x1.max())/2
    same_side  = (row.x0 < middle ) == (df.x0 < middle) 
    below      = (df.y0 > row.y0)
    not_image  = (df.category != "image")

    mask       = same_side & below & not_image & same_page
    other_rows = df.loc[mask]

    if len(other_rows)<=1:
        return np.nan
    
    dir = ["y0","y1"]
    distances = pairwise_distances(row[dir].values.reshape(1,-1) , Y=other_rows[dir].values,  metric=df_bbox_dist)

    nn_2 = np.sort(distances[0])[1]

    return nn_2


def correct_eps_y_scale(df, page,y_scale):
    """
    This function determines an appropriate scale for the eps_y obtained from nearest neighbour 
    distances for use in dbscan.
    
    Some documents have lines such that subsequent lines overlap with each other, and therefore the
    first non-overlapping line is actually the second neighbour. In this case an appropriate scale is
    1/2 as we have gone ahead two distances.
    """
    page_df = df[df.page==page].copy()

    nn_dist  = page_df.apply(lambda row: nn_line_distance(page_df, row), axis=1)

    if nn_dist.median() == 0:
        return y_scale%1 + 0.5
    return y_scale

def get_eps_y(df, page,y_scale):
    page_df = df[df.page==page].copy()
    dL_median = page_df.apply(lambda row: get_vert_neigh_dist(row, page_df, ["y0","y1"]),axis=1 ).median()
    y_scale = correct_eps_y_scale(page_df, page, y_scale)

    eps_y = (dL_median * y_scale) if not np.isnan(dL_median) else page_df.h.median() * y_scale
    return eps_y
    
def get_eps_x(df, page,x_scale):
    page_df = df[df.page==page].copy()
    middle = (page_df.x0.min() + page_df.x1.max())/2
    left  = page_df[page_df.x1 < middle +5 ]
    right = page_df[page_df.x0 > middle -5 ]

    if len(right)==0 or len(left)==0:
        return 10*x_scale
    
    left_right_dist  = pairwise_distances(left[["x0","x1"]], right[["x0","x1"]], metric=df_bbox_dist)
    mask = (left_right_dist!=0)                 # Exclude overlapping lines

    return x_scale * left_right_dist[mask].min()


def split_cluster(df: pd.DataFrame, i_clust: int,  metric, eps, dir, verbose=False):
    """
    This function will split a cluster in dataframe df by performing a dbscan in direction dir with 
    parameter eps if it can.

    If a split occurs the original cluster id will be kept for one cluster, and new cluster ids, taking into
    account all clusters currently present in df, will be assigned to the new clusters.

    The function modifies df in place, assigning the new cluster labels to df.cluster.
    """
    if verbose: print(f"scanning cluster {i_clust}")
    last_id  = df.cluster.max()
    clust_df = df[df.cluster==i_clust].copy()

    X             = pairwise_distances(clust_df[dir],metric=metric)
    scan          = DBSCAN(eps=eps, min_samples=1,metric="precomputed")

    try:
        labels        = scan.fit_predict(X)
    except InvalidParameterError as e:
        print(e)
        print(f"\n\nScanning cluster {i_clust} page {np.unique(df.page)[0]} in {dir} with eps: {eps}")
        raise 
    
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
    if len(df)<=1:
        return rectangies, labia
    
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