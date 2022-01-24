import pandas as pd
import streamlit as st
from data_proc import process_df
import urllib.request, json 
import os
import pickle


#@st.cache()
def get_tree_data_df(delete_file = False):
    # Opening JSON file
    f = open('app/data/data_info.json')
    
    # returns JSON object as
    # a dictionary
    data_info = json.load(f)
    
    try:
        if delete_file:
            if os.path.exists("app/data/results.csv"):
                os.remove("app/data/results.csv")
        df = pd.read_csv("app/data/results.csv")

    except FileNotFoundError: 
        print("Descargando ...")
        path ='https://drive.google.com/uc?id=' + data_info["csv id"]

        df = pd.read_csv(path)

        process_df(df)

        with open('app/data/sectors.pkl', 'wb') as handle:
            pickle.dump(data_info["Sectores"], handle, protocol=pickle.HIGHEST_PROTOCOL)

    


def update_data():
    
    with urllib.request.urlopen(st.secrets["API_URL"]) as url:
        data_info = json.loads(url.read().decode())
        
    
    with open('app/data/data_info.json', 'w') as fp:
        json.dump(data_info, fp)

    get_tree_data_df(delete_file = True)



