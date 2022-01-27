import streamlit as st
from pathlib import Path
import pandas as pd


tree_info_data = pd.read_csv("app/trees descriptions/TreeInfoMDpairs.csv")
species = list(tree_info_data["Especie"])
files = list(tree_info_data["Markdown files"])
files_species_dict = dict(zip(species, files))


def read_markdown_file(markdown_file):
    """
    A function that reads a markdown file and returns the content as a string.
    Note that the filepath is writen as if the file is executed from the root of the project.
    This is because when deployed the app.py is going to be run from the root of the project.
    """
    return Path("app/trees descriptions/" + markdown_file + ".md").read_text(encoding="utf-8")


def show_tree_info():
    """
    This function shows a search bar for the trees species in the trees descriptions,
    and displays the tree description in markdown format.

    """
    col1, col2, col3 = st.columns([1, 3, 1])

    tree = col2.selectbox("Busca un árbol!", species + [])

    st.markdown(read_markdown_file(
        files_species_dict[tree]), unsafe_allow_html=True)
