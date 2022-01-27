import pandas as pd
import streamlit as st
from data_proc import process_df
import urllib.request
import json
import os
import pickle


def get_tree_data_df(delete_file=False) -> None:
    """
    The fucntion gets the .csv file from Google drive

    kwargs:

        delete_file: bool -> If True, the previous (results.csv) file is deleted.

    returns:
        None

    """
    # Opening JSON file
    f = open('app/data/data_info.json')

    # returns JSON object as
    # a dictionary
    data_info = json.load(f)

    # If the data exists, it is deleted.
    try:
        if delete_file:
            if os.path.exists("app/data/results.csv"):
                os.remove("app/data/results.csv")
        df = pd.read_csv("app/data/results.csv")

    except FileNotFoundError:
        print("Descargando ...")
        # It is important to note that Pandas can only download the file
        # from google drive if the file space is less than around 100MB
        path = 'https://drive.google.com/uc?id=' + data_info["csv id"]
        df = pd.read_csv(path)

        # Dataframe is processed (and saved)
        process_df(df)

        # We also save the sectors list in a pickle file
        with open('app/data/sectors.pkl', 'wb') as handle:
            pickle.dump(data_info["Sectores"], handle,
                        protocol=pickle.HIGHEST_PROTOCOL)


def update_data() -> None:
    """

    This function updates the dataframe with the new data from Google Drive.

    Args:
        None

    Returns:
        None
    """

    # A request to the API is made to get the JSON file with the sector list and the URL to the csv file.
    with urllib.request.urlopen(st.secrets["API_URL"]) as url:
        data_info = json.loads(url.read().decode())

    with open('app/data/data_info.json', 'w') as fp:
        json.dump(data_info, fp)

    # Dataframe is loaded and processed
    get_tree_data_df(delete_file=True)
