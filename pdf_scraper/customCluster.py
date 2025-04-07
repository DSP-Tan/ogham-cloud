import math
from utils import *
import pandas as pd
import numpy  as np
from numpy.linalg import norm
import fitz
from fitz import Rect
from line_utils import *
import re

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



X = df.drop(columns=["font_list","text","n_spans","dL"])

num_vars = list( X.select_dtypes(include=np.number).columns )
num_vars.remove("n_words")

cat_vars = list( X.select_dtypes(include='object').columns  )
ohe = OneHotEncoder(drop="if_binary", sparse_output=False, handle_unknown="error" )

basic_preproc = make_column_transformer(
    (StandardScaler(), num_vars),
    (OneHotEncoder(drop="if_binary",sparse_output=False, handle_unknown="error"), cat_vars),
    ("passthrough", ["n_words"]),
    remainder="drop"
    )

X = basic_preproc.fit_transform(df)
X_df = pd.DataFrame(X,columns=num_vars+ cat_vars+["n_words"] )
print(f"Preprocessed dataframe of shape {X.shape}:")
print(X_df.head(5))

i_nword = X.shape[1]-1
print(X[0,i_nword])

# initialise clusters
clusts = X[[0, X.shape[0]-1]]
clust0, clust1 = clusts
clusts.shape

# full distance calc for certain, N-1 dimensional for others.
full_vect = X[:, :i_nword]
print(f"Full vector of shape {full_vect.shape}")
print(pd.DataFrame(full_vect, columns= num_vars + cat_vars).head(2) )


x_cols     = [0,2,4]
non_x_cols = [i for i in range(i_nword) if i not in x_cols]
print(f"In preproc'd X, x cols are: {x_cols}")
print(f"non x-based column indices: {non_x_cols}")
small_vect = X[ :, [i for i in range(i_nword) if i not in x_cols] ]
print(f"Small y-and-font only vector of shape {small_vect.shape}")
print(pd.DataFrame(small_vect, columns = X_df.columns[non_x_cols]).head(2))