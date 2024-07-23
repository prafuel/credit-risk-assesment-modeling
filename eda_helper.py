# libraries
import pandas as pd 
import numpy as np


from sklearn.model_selection import train_test_split


# split data into train (training), val (model tuning), test (testing)
def split_data(df, target='target', test_size=0.2):

    X = df.drop(columns=[target])
    y = df[target]

    # test
    X_, X_test, y_, y_test = train_test_split(X, y, test_size=test_size)

    # train, val
    X_train, X_val, y_train, y_val = train_test_split(X_, y_, test_size=test_size)

    return (X_train, X_val, X_test), (y_train, y_val, y_test)


# get columns with null values
def get_null_columns(df):
    columns = df.columns
    null_cols = [col for col in columns if df[col].isnull().any()]
    counts = [df[col].isnull().sum() for col in null_cols]

    return (
        pd.DataFrame({
        "columns" : null_cols,
        "null_count" : counts
        })
        .set_index("columns")
    )
    

if __name__ == "__main__":
    pass