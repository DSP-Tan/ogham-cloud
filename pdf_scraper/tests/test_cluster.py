import pandas as pd
import numpy  as np
from pdf_scraper.line_utils               import line_is_empty, get_line_df
from pdf_scraper.doc_utils                import open_exam
from pdf_scraper.clustering.kmeans import preproc, cluster_optimise
    
from sklearn.cluster import KMeans

def test_standard_cluster():
    """
    This test checks to see that the standard cluster_optimise function, which does a 
    normal Kmeans clustering for 2 clusters, agrees with the result obtained by using
    SKlearns KMeans class.
    """
    doc              = open_exam(2024, "English", "al", 1)
    page_dict        = doc[3].get_text("dict",sort=True)
    block            = page_dict["blocks"][6]
    lines            = [line for line in block["lines"] if not line_is_empty(line)]
    
    pd.set_option("display.float_format", "{:.2f}".format)
    df        = get_line_df(lines)

    cols = ['x0', 'y0', 'y1', 'w',  'font_size', 'mode_font']
    
    X_df = preproc(cols, df)
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
    print(labels)

    assert all(cluster_pred==labels)

def test_custom_kmeans_block_split():
    pass

if __name__=="__main__":
    test_standard_cluster()




