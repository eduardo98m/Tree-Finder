
import pandas as pd
#import streamlit as st
import urllib.request, json 
import os

#@st.cache()
def get_tree_data_df(delete_file = False):
    # Opening JSON file
    f = open('data/data_info.json')
    
    # returns JSON object as
    # a dictionary
    data_info = json.load(f)
    
    try:
        if delete_file:
            if os.path.exists("data/tree_data.csv"):
                os.remove("data/tree_data.csv")
        df = pd.read_csv("data/tree_data.csv")

    except FileNotFoundError: 
    
        path ='https://drive.google.com/uc?id=' + data_info["csv id"]

        df = pd.read_csv(path)

        df.to_csv("data/tree_data.csv")

    finally:

        return df


def update_data():
    
    with urllib.request.urlopen("https://script.google.com/macros/s/AKfycbyl56-t51vp68a_X13xn7VXEweRqa2c2z21CEqyJwr8rnFZZYn2g10mdbpMFJSMnzlaqA/exec") as url:
        data_info = json.loads(url.read().decode())
        print(data_info)
    
    with open('data/data_info.json', 'w') as fp:
        json.dump(data_info, fp)

    get_tree_data_df(delete_file = True)


get_tree_data_df(delete_file = True)