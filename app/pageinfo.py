from re import A
import streamlit as st


def page_info():
    """
    This function shows the information about the project.
    It is a simple text with hyperlinks
    """
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.markdown("""
    <center>
    <a href="https://fundacionespacio.com" title="Página web de la fundación espacio">Fundación espacio</a>
    <a href="https://github.com/eduardo98m/Tree-Finder" title="Repositorio de github del proyecto">Código de la Página</a>
    </center>
    """, unsafe_allow_html=True)
