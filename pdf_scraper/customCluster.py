import math, ipdb, re, fitz
from fitz import Rect
import pandas as pd
import numpy  as np
from numpy.linalg import norm
from line_utils import *
from utils import *

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import make_column_transformer


import fitz
from fitz import Rect

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


bad_nums = ["n_spans","dL","n_words"]
num_vars = [ col for col in df.select_dtypes(include=np.number).columns if col not in bad_nums ] 

bad_cats = ["font_list","text"]
cat_vars = [col for col in  df.select_dtypes(include='object').columns if col not in bad_cats] 

basic_preproc = make_column_transformer(
    (StandardScaler(), num_vars),
    (OneHotEncoder(drop="if_binary",sparse_output=False, handle_unknown="error"), cat_vars),
    ("passthrough", ["n_words"]),
    remainder="drop"
    )

X = basic_preproc.fit_transform(df)
X_df = pd.DataFrame(X,columns=num_vars+ cat_vars+["n_words"] )
print(f"Preprocessed dataframe of shape {X.shape}:")
print(X_df.head(5),"\n")

i_nword = X.shape[1]-1

# initialise clusters
clusts = X[[0, X.shape[0]-1]]
clust0, clust1 = clusts
clusts.shape

# We need to choose now the rows where the number of words is below 4
word_mask= X[:,i_nword] < 4

# full distance calc for certain, N-1 dimensional for others.
full_vect = X[~word_mask, :i_nword]
full_clust = clusts[:, :i_nword]

print(f"Full vector of shape {full_vect.shape}")
print(pd.DataFrame(full_vect, columns= num_vars + cat_vars).head(2),"\n\n" )




ipdb.set_trace()
x_cols     = [0,2,4]
non_x_cols = [i for i in range(i_nword) if i not in x_cols]
print(f"In preproc'd X, x cols are: {x_cols}")
print(f"non x-based column indices: {non_x_cols}")
# Have to index like that, because numpy interprects X[list1,list2] as asking for a bunch of pairs of coordinates of mathces from each list.
small_vect  = X[ word_mask][:, non_x_cols ]
small_clust = clusts[:, non_x_cols]
print(f"Small y-and-font only vector of shape {small_vect.shape}")
print(pd.DataFrame(small_vect, columns = X_df.columns[non_x_cols]).head(2))

