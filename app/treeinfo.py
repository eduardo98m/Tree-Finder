from turtle import forward
import streamlit as st
from pathlib import Path
import pandas as pd

tree_info_data = pd.read_csv("app/trees descriptions/TreeInfoMDpairs.csv")
species =list(tree_info_data["Especie"])
files =list(tree_info_data["Markdown files"])
files_species_dict = dict(zip(species, files))
i = 0

def read_markdown_file(markdown_file):
    return Path("app/trees descriptions/" + markdown_file + ".md").read_text(encoding = "utf-8")


def show_tree_info():
    col1, col2, col3 = st.columns([1, 3, 1])
     
    tree = col2.selectbox("Busca un árbol!", species + [])


    
    st.markdown(read_markdown_file(files_species_dict[tree]), unsafe_allow_html=True)