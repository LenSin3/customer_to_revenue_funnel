from ctypes import windll
import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import utils

## function to read data
## check for data quality issues

def read_and_qa(df):
    # check if dataframe is valid
    if isinstance(df, pd.DataFrame):
        # copy file
        df = df.copy()
        ##############################
        # check for nulls
        data_types = []
        non_nulls = []
        nulls = []
        null_column_percent = []
        null_df_percent = []
        df_cols = df.columns
        print("There are {} columns and {} records in the dataframe.".format(len(df_cols), len(df)))
        # loop through columns and capture the variables above
        print("Extracting count and percentages of nulls and non nulls")
        for col in df_cols:
            # extract null count
            null_count = df[col].isna().sum()
            nulls.append(null_count)
                
            # extract non null count
            non_null_count = len(df) - null_count
            non_nulls.append(non_null_count)
                
            # extract % of null in column
            col_null_perc = 100 * null_count/len(df)
            null_column_percent.append(col_null_perc)
            
            if null_count == 0:
                null_df_percent.append(0)
            else:
                # extract % of nulls out of total nulls in dataframe
                df_null_perc = 100 * null_count/df.isna().sum().sum()
                null_df_percent.append(df_null_perc)
                
            # capture data types
            data_types.append(df[col].dtypes) 
    
    else:
        raise utils.InvalidDataFrame(df)
            
    # create zipped list with column names, data_types, nulls and non nulls
    lst_data = list(zip(df_cols, data_types, non_nulls, nulls, null_column_percent, null_df_percent))
    # create dataframe of zipped list
    df_zipped = pd.DataFrame(lst_data, columns = ['Feature', 'DataType', 'CountOfNonNulls', 'CountOfNulls',\
                                                'PercentOfNullsInColumn', 'PercentOfNullsInData'])
    return df, df_zipped


def unique_vals_counts(df: DataFrame) -> DataFrame:
    """Count unique values in dataframe.

    The count is perfromed on all columns in the dataframe.

    Parameters
    ----------
    df : DataFrame
        Dataframe to check for unique values per column.
        

    Returns
    -------
    DataFrame
    """
    if isinstance(df, pd.DataFrame):
        df_cats = df.select_dtypes(include ='object')
        df_cats_cols = df_cats.columns.tolist()
        for col in df_cats_cols:
            if 'essay' in col or 'last_online' in col:
                df_cats = df_cats.drop(col, axis=1)
        vals = df_cats.nunique().reset_index()
    else:
        raise utils.InvalidDataFrame(df)
    return vals.rename(columns = {'index': 'column', 0: 'count'})

def unique_vals_column(df: DataFrame, col: str, normalize = False) -> DataFrame:
    """Count unique values in a single column in a dataframe.

    Value counts are calculated for a single column and tabulated.

    Parameters
    ----------
    df : DataFrame
        Dataframe containing column to check 
        for unique values.
    col : str
        Name of column to check for unique values.
    normalized : bool, optional
        If true this function normalizes the counts.
         (Default value = False)
         

    Returns
    -------
    DataFrame
    """
    if isinstance(df, pd.DataFrame):
        if col in df.columns:
            uniques = df[col].value_counts().reset_index().rename(columns = {'index': col, col : 'count'})
            if normalize:
                uniques = df[col].value_counts(normalize = True).reset_index().rename(columns = {'index': col, col : 'percentOfTotal'})
        else:
            raise utils.InvalidColumn(col)
    else:
        raise utils.InvalidDataFrame(df)
    return uniques


def group_melt(df):
    """Group and melt a DataFrame.

    DataFrame is grouped by week and category and melted with week and category as ID variables.

    Parameters
    ----------
    df : DataFrame
        DataFrame to group and melt.        

    Returns
    -------
    DataFrame
    """

    # aggregate data by year and region
    df_grp = df.groupby(['Week', 'Category'], as_index = False)[['wine', 'beer', 'vodka', 'champagne', 'brandy']].mean()
    # melt data frame - wide to long
    df_melt = pd.melt(df_grp, id_vars = ['year', 'region'], value_vars = ['wine', 'beer', 'vodka', 'champagne', 'brandy'],\
                var_name = 'beverages', value_name = 'Sales per Capita')

    return df_melt