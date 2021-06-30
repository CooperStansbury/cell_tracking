"""
A collection of classes/functions use to manipulate trackmate outputs
"""

import sys
import os
import pandas as pd
import numpy as np


def load_trackmate_dir(dir_path, verbose=False):
    """A function to load all trackmate outputs
    in a directory (.csv only)
    
    Parameters:
    -----------------------------
        : dir_path (str): path to the directory
        : verbose (bool): should we print?
        
    Returns:
        : data (dict): file base names as keys, 
    -----------------------------
        pd.DataFrames as values
    """
    data = {}
    for f in os.listdir(dir_path):
        if '.csv' in f:
            fpath = f"{dir_path}{f}"
            data_name = f.replace(".csv", "").split(" ")[0]
            df = pd.read_csv(fpath)
            data[data_name] = df
            if verbose:
                print(f"{data_name} shape: {df.shape}")
    return data


def merge_tracks_and_all(data, verbose=False):
    """A function to to merge the tracks and all spots statistics files
    
    NOTE: missing TRACK_ID dropped
    
    Parameters:
    -----------------------------
        : data (dict): file base names as keys, 
        pd.DataFrames as values
        : verbose (bool): should we print?
        
    Returns:
    -----------------------------
        : df (pd.DataFrame): dataframe merged on TRACK_ID
    """
    spots = data['All']
    tracks = data['Track']
    
    # drop missing TRACK_IDs
    spots = spots[spots['TRACK_ID'] != "None"]
    spots = spots.astype({"TRACK_ID": int})
    
    # convert types
    tracks = tracks.astype({"TRACK_ID": int})
    
    # merge 
    df = pd.merge(spots, tracks, how='left', on=['TRACK_ID'])
    if verbose:
        print(f'merged shape: {df.shape}')
    return df 
  
    
def strip_low_intensities(df, column, quantile):
    """A function to replace low intensity values with zero
    
    Parameters:
    -----------------------------
        : df (pd.DataFrame): dataframe merged on TRACK_ID
        : column (str): column to use
        : quantile (float): intensities below this mark with be replaced with 0
        
    Returns:
    -----------------------------
        : df (pd.DataFrame): dataframe with column corrected in place
    """
    q = df[column].quantile(quantile)
    
    df[column] = np.where(df[column] < q, 0, df[column])
    return df
    
    
def min_max_norm(df, column, group_by):
    """A function to perform min/max scaling
    
    Parameters:
    -----------------------------
        : df (pd.DataFrame): dataframe merged on TRACK_ID
        : column (str): column to min/max scale
        : group_by (str): grouping column, likely TRACK_ID
        
    Returns:
    -----------------------------
        : df (pd.DataFrame): dataframe merged on TRACK_ID
    """
    grouper = df.groupby(group_by)[column]                                         
    maxes = grouper.transform('max')                                                    
    mins = grouper.transform('min')
    new_col_name = f"{column}_SCALED"
    df.loc[:, new_col_name] = ((df[column] - mins)/(maxes - mins))
    return df
    
def clean_up_trackSpots(df, quantile, verbose=False):
    """A function to clean up the merged track and all spots 
    stats file.
    
    Parameters:
    -----------------------------
        : df (pd.DataFrame): dataframe merged on TRACK_ID
        : verbose (bool): should we print?
        
    Returns:
    -----------------------------
        : df (pd.DataFrame): minus some columns, ect.
    """
    keepers = [x for x in df.columns if not df[x].unique().all() == 'None']
    
    # strip useless columns
    df = df[keepers]
    
    # sort by ID then FRAME
    df = df.sort_values(by=['TRACK_ID', 'FRAME'])

    # add a grouped step 
    steps = df.groupby(['TRACK_ID']).cumcount()
    df.loc[:, 'STEP'] = steps
    df.loc[:, 'NORMED_STEP'] = df['STEP'] / df['TRACK_DURATION']
    
    for col in df.columns:
        if 'MEAN_INTENSITY' in col:
            
            df = strip_low_intensities(df, col, quantile)
            
            df = min_max_norm(df, col, group_by='TRACK_ID')
            
    df = df.dropna(axis=1, how='all')
    if verbose:
        print(f"cleaned shape {df.shape}")
        
    df = df.sort_values(by=['TRACK_ID', 'STEP', 'FRAME'])
    return df
    
    
    