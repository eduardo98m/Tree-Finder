import streamlit as st
import numpy as np

# App layout #
st.title('La Floresta Tree Finder')


# Filters
#Sliders
hour_to_filter = st.slider('hour', 0, 23, 17)
with st.form(key='tree_query'):
	text_input = st.text_input(label='Enter your name')
	submit_button = st.form_submit_button(label='Submit') 


# Map

# Query the Map Data
map_data = pd.DataFrame(
np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
columns=['lat', 'lon'])

# Display the Map Data
st.map(map_data)

# Display the items in the map (With selector)


# Display selected item pictures





