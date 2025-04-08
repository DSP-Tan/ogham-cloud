import fitz
from fitz import Rect
import pandas as pd
import numpy  as np
from numpy.linalg import norm
from line_utils   import *
from utils        import *

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import make_column_transformer


pdf_file = "test_pdfs/LC002ALP100EV_2024.pdf"
doc              = fitz.open(pdf_file)
page             = doc[3]
page_dict        = page.get_text("dict",sort=True)
blocks           = page_dict["blocks"]
block            = blocks[6]

lines = [line for line in block["lines"] if not line_is_empty(line)]

pd.set_option("display.float_format", "{:.2f}".format)
df = get_line_df(lines)
print("Raw lines dataframe:")
print(df.head(10))

# These cols of the df are not informative for text-block clustering.
bad_nums = ["n_spans","dL","n_words","x1"]
num_vars = [ col for col in df.select_dtypes(include=np.number).columns if col not in bad_nums ] 

bad_cats = ["font_list","text"]
cat_vars = [col for col in  df.select_dtypes(include='object').columns if col not in bad_cats] 

basic_preproc = make_column_transformer(
    (StandardScaler(), num_vars),
    (OneHotEncoder(drop="if_binary",sparse_output=False, handle_unknown="error"), cat_vars),
    ("passthrough", ["n_words"]),
    remainder="drop"
    )
X_cols = num_vars + cat_vars + ["n_words"]
X      = basic_preproc.fit_transform(df)
X_df   = pd.DataFrame(X,columns=X_cols )
print(f"Preprocessed dataframe of shape {X.shape}:")
print(X_df.head(20),"\n")


# initialise clusters
k=2
clusts = X[[0, X.shape[0]-1]]

# We need to choose now the rows where the number of words is below 4
i_nword   = X_cols.index("n_words")
word_mask = X[:,i_nword] < 4
full_cols = num_vars + cat_vars

# full distance calc for certain, N-1 dimensional for others.
full_vect  = X[~word_mask, :i_nword]
full_clust = clusts[:, :i_nword]

full_diff   = full_vect[:, np.newaxis, :] - full_clust[np.newaxis, :, :]  #  (m_full, 2, n)
full_dists  = norm(full_diff, axis=2)                                     #  (m_full, 2)

print(f"Full vector of shape {full_vect.shape}")
print(pd.DataFrame(full_vect, columns= full_cols).head(8),"\n\n" )



# If we have a line with a small n_words, the width is no longer a good variable for clustering.
i_w     = X_cols.index("w")
small_cols = [i for i in range(i_nword) if i != i_w]
# Have to index like that, because numpy interprects X[list1,list2] as asking for a bunch of pairs of coordinates of mathces from each list.
small_vect  = X[ word_mask][:, small_cols ]
small_clust = clusts[:, small_cols]

print(f"Width-excluded vector of shape {small_vect.shape}")
print(pd.DataFrame(small_vect, columns = X_df.columns[small_cols]).head(2),"\n\n")

small_diff   = small_vect[:, np.newaxis, :] - small_clust[np.newaxis, :, :]  #  (m_small, 2, n -1)
small_dists  = norm(small_diff, axis=2)                                      #  (m_small, 2)

dists = np.empty((word_mask.shape[0], k))
dists[word_mask]  = small_dists
dists[~word_mask] = full_dists
labels = np.argmin(dists, axis=1)

X_df["cluster"] = pd.Series(labels)
#print(X_df.head(8))

import ipdb; ipdb.set_trace()


d_clust = norm(clusts,axis=1)
max_iter = 1000

#new_clusts = np.vstack([X[labels == i].mean(axis=0) for i in range(k)])



