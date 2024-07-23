import pandas as pd 
import numpy as np 



# if some column has more than 10000 null rows then we remove those full columns
def removing_cols(df):
    cols = []
    for col in df.columns:
        if df[df[col] == -99999].shape[0] > 10000:
            cols.append(col)
    return cols


# merging two dfs
def merging_both_df(case1, case2, on):
	return (
		pd
		.merge(
			case1, case2,
			on=on, how='inner'
		)
	)

