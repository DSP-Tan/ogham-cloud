import fitz, itertools
import pandas as pd
import numpy  as np
from pdf_scraper.line_utils    import line_is_empty, get_line_df
from pdf_scraper.clustering.cluster_utils import calc_cust_dists, calc_inertia, custom_cluster_optimise, preproc
from pathlib import Path

if __name__=="__main__":
    exam_dir     = Path(__file__).parent.parent.parent / "Exams" / "english" / "AL"
    pdf_file     = exam_dir / "LC002ALP100EV_2024.pdf"
    doc          = fitz.open(pdf_file)
    page         = doc[3]
    page_dict    = page.get_text("dict",sort=True)
    blocks       = page_dict["blocks"]
    block        = blocks[6]
    
    lines = [line for line in block["lines"] if not line_is_empty(line)]
    
    pd.set_option("display.float_format", "{:.2f}".format)
    df        = get_line_df(lines)
    
    
    # We need to choose now the rows where the number of words is below 4
    word_mask = df["n_words"].to_numpy() < 4
    
    cols = ['x0', 'y0', 'y1', 'w',  'font_size', 'mode_font']
    
    X_df   = preproc(cols, df, font_scale=2)
    X      = np.array(X_df)
    X_cols = X_df.columns.to_list()
    
    k      = 2
    i_w    = X_cols.index("w")
    
    
    best_clusts     = np.array([X[0], X[-1]])
    dists           = calc_cust_dists(best_clusts, X, word_mask,i_w)
    best_clustering = np.argmin(dists,axis=1)
    inertia         = calc_inertia(dists)
    
    # Loop over initial cluster positions excluding lines with n_words < 4.
    for clust0, clust1 in itertools.combinations(X[~word_mask], k):
        clusts = np.array([clust0, clust1])
        
        new_inertia, clusts, labels = custom_cluster_optimise(X,clusts,word_mask, i_w, tol=0.001, verbose=True)
        
        if new_inertia < inertia:
            inertia=new_inertia
            best_clustering =labels
            best_clusts = clusts
    
        
    X_df["cluster"] = pd.Series(best_clustering)
    print(f"Preprocessed clustered line-dataframe of shape {X.shape} with:")
    print( X_df.head(20) )


def reblock_lines(lines, verbose=False):
    '''
    This function splits one line block into two line blocks by clustering together lines based on 
    y-position, x-position, width and font. A custom clustering is used which takes into account the
    fact that for lines with fewer than 4 words, the width is no longer an informative variable for
    clustering.  
    
    The function returns a np.array of labels telling which block each line belongs to. 
    '''
    lines = [line for line in lines if not line_is_empty(line)]
    line_df = get_line_df(lines)
    # We need to choose now the rows where the number of words is below 4
    word_mask = line_df["n_words"].to_numpy() < 4
    
    cols = ['x0', 'y0', 'y1', 'w', 'mode_font']
    
    X_df   = preproc(cols, line_df, font_scale=2)
    X      = np.array(X_df)
    X_cols = X_df.columns.to_list()
    
    k      = 2
    i_w    = X_cols.index("w")
    
    
    best_clusts     = np.array([X[0], X[-1]])
    dists           = calc_cust_dists(best_clusts, X, word_mask,i_w)
    best_clustering = np.argmin(dists,axis=1)
    inertia         = calc_inertia(dists)
    
    # Check every combination of lines with >4 words for initial clusters
    for clust0, clust1 in itertools.combinations(X[~word_mask], k):
        clusts = np.array([clust0, clust1])
        
        new_inertia, clusts, labels = custom_cluster_optimise(X,clusts,word_mask, i_w, tol=0.001, verbose=verbose)
        
        if new_inertia < inertia:
            inertia=new_inertia
            best_clustering =labels
            best_clusts = clusts
    
    if verbose:    
        X_df["cluster"] = pd.Series(best_clustering)
        print(f"Preprocessed clustered line-dataframe of shape {X.shape} with:")
        print( X_df.head(20) )

    return best_clustering