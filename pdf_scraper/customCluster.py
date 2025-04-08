import fitz
import pandas as pd
import numpy  as np
from numpy.linalg import norm
from line_utils   import *
from utils        import *

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose       import make_column_transformer


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

print("Raw lines dataframe:")
print(df.head(10))

# These cols of the df are not informative for text-block clustering.
bad_nums = ["n_spans","dL","x1","n_words"]
num_vars = [ col for col in df.select_dtypes(include=np.number).columns if col not in bad_nums ] 

bad_cats = ["font_list","text"]
cat_vars = [col for col in  df.select_dtypes(include='object').columns if col not in bad_cats] 

basic_preproc = make_column_transformer(
    (StandardScaler(), num_vars),
    (OneHotEncoder(drop="if_binary",sparse_output=False, handle_unknown="error"), cat_vars),
    remainder="drop"
    )
X_cols = num_vars + cat_vars 
X      = basic_preproc.fit_transform(df)
X_df   = pd.DataFrame(X,columns=X_cols )
print(f"Preprocessed dataframe of shape {X.shape}:")
print(X_df.head(20),"\n")


# initialise clusters - first and last data point are top and bottom of page
k=2
m, n = X.shape
clusts  = X[[0, m-1]]
d_clust = norm(clusts,axis=1)

i_w       = X_cols.index("w")

# full distance calc for certain, N-1 dimensional for others.
full_cols  = num_vars + cat_vars
full_vect  = X[~word_mask, :]
full_clust = clusts[:, :]

full_diff   = full_vect[:, np.newaxis, :] - full_clust[np.newaxis, :, :]  #  (m_full, 2, n)
full_dists  = norm(full_diff, axis=2)                                     #  (m_full, 2)

print(f"Full vector of shape {full_vect.shape}")
print(pd.DataFrame(full_vect, columns= full_cols).head(8),"\n\n" )



# If we have a line with a small n_words, the width is no longer a good variable for clustering.
small_cols  = [i for i in range(n) if i != i_w]
small_vect  = X[ word_mask][:, small_cols ]
small_clust = clusts[:, small_cols]

small_diff   = small_vect[:, np.newaxis, :] - small_clust[np.newaxis, :, :]  #  (m_small, 2, n -1)
small_dists  = norm(small_diff, axis=2)                                      #  (m_small, 2)

print(f"Width-excluded vector of shape {small_vect.shape}")
print(pd.DataFrame(small_vect, columns = X_df.columns[small_cols]).head(2),"\n\n")

dists = np.empty((m, k))
dists[word_mask]  = small_dists
dists[~word_mask] = full_dists
labels = np.argmin(dists, axis=1)

X_df["cluster"] = pd.Series(labels)
#print(X_df.head(8))

import ipdb; ipdb.set_trace()


max_iter = 1000
tol = 1
for i in max_iter:
    if d_clust < tol:
        break
    new_clusts = np.vstack([X[labels == i].mean(axis=0) for i in range(k)])



def calc_dists(clusts, X, word_mask, i_w):
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