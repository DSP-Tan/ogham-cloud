import pandas as pd
import numpy  as np 

def examine_value_counts(df: pd.DataFrame, columns):
    n_cols =len(columns)
    for i in range(0,n_cols,4):
        cols=columns[i:i+4]
        cats = [100*(df[col].value_counts()/len(df)) for col in cols]
        heading=""
        for col,cat in zip(cols,cats):
            heading +=f"{col[:35]:<35} {len(cat):<5}  | "
        print("--"*80)
        print(f"{heading}")
        print("--"*80)

        for j in range(min([len(cat) for cat in cats]) ) :
            body=""
            for col,cat in zip(cols,cats):
                idx_type = cat.index.dtype
                col = cat.index[j]
                val = cat.values[j]
                if np.issubdtype(idx_type, np.number):
                    body += f"{col:<35} {val:<5.1f}% | "
                elif np.issubdtype(idx_type, np.object_) or np.issubdtype(idx_type, np.str_):
                    body += f"{col[:30]:<35} {val:<5.1f}% | "
            print(body)
        print("--"*80,"\n\n")