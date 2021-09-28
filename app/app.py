import streamlit as st
import pydeck as pdk
import numpy as np
import pandas as pd

# internal modules
from data_proc import procees_df
from PyDrive.pydrive_functions import write_trees_csvs




# App layout #
st.title('La Floresta Tree Finder')


# Possible Filters


#Attribute               Filter implementation

#Código	             	Yes
#Código de Especie	 	Yes
#Especie 	         	Yes
#Nombre común	    	Yes
#Altura (m)	         	Yes (Height Range?)
#Circunferencia (m)   	Yes (Circunference range)
#DAP (m)				 	Yes (DAP range)
#D. de copa N-S (m)   	?¿
#D. de copa E-O (m)	 	?¿
#Fecha	          	 	Yes (Date range)
#Latitud	Longitud	 	Unnecesary
#Dirección			 	Unnecesary (Hard to query)
#Observaciones	     	Depending on the consistency
#ID Foto Tronco	     	Maybe
#ID Foto Hojas		 	Maybe
#ID Foto inflorescencia	Maybe
#ID Foto copa			Maybe

# Query the trees data

species_data = pd.read_csv('data\Especies - Hoja 1.csv')

raw_data = pd.read_csv("data/Parque Aruflo Levantamiento - Sector 1.csv")

map_data =   procees_df(raw_data)[0][['lat', 'lon']].dropna()


df_display = raw_data
# Pydeck
#----------------------------------------------------------------------------------------#
# Display the Map Data
#st.map(map_data) <- Simpler function but almost no customization
# Adding code so we can have map default to the center of the data
midpoint = (np.average(map_data['lat']), np.average(map_data['lon']))

#https://drive.google.com/file/d/19Xmp0UlcfBU85EdLLV8eQDsJ_5KpLWRu/view?usp=sharing
id ="19Xmp0UlcfBU85EdLLV8eQDsJ_5KpLWRu"

img_src = "https://drive.google.com/thumbnail?id=" + id

tooltip = {
   "html" : "<b>Latitude: </b> {lat} <br /> "
   		   "<b>Longitude: </b> {lon} <br /> "
		   #"<b>name: </b> {name} <br /> "
		   "<b>Image</b> <img src= " + str(img_src) + ">",
   "style": {
        "backgroundColor": "steelblue",
        "color": "white"
   }
}

st.header('Mapa')
st.pydeck_chart(pdk.Deck(
			initial_view_state={"latitude": 10.4945, # La Floresta coordinates
			"longitude": -66.8456, "zoom": 15},
			layers=[
				pdk.Layer(
				"ScatterplotLayer",
				data = map_data,
				get_position=['lon', 'lat'],
				radiusScale = 1,
				radiusMinPixels = 5, # Modify to match the scale of the park trees
				getFillColor = [248, 24, 148],
				pickable=True,
				)
			],
			tooltip=tooltip
		))


#----------------------------------------------------------------------------------------#
# FORM
query = {}
with st.form(key='tree_query'):
	query_expr = ""
	st.header('Opciones de Búsqueda')
	#

	col1, col2 = st.beta_columns(2)
	codigo = col1.text_input("Código")
	
	if codigo != "":
		query_expr = query_expr + "Código == @codigo"


	col1.subheader('Especie')

	# The next 4 fields should be linked (The user should only be able to select one)
	codigo_de_especie = col1.multiselect("Código de Especie", 
													species_data["Código"])
	especie = col1.multiselect("Especies", species_data["Nombre"])
	nombre_comun = col1.multiselect("Nombre común", 
											species_data["Nombre Común"])

	col2.subheader('Dimensiones')
	#
	altura = col2.slider('Rango de altura', 0.0, 50.0, (25.0, 35.0))
	circunferencia = col2.slider('Rango de circunferencia', 
										0.0, 50.0, (25.0, 35.0))
	
	dap = col2.slider('Rango de DAP', 
										0.0, 50.0, (25.0, 35.0))
	
	st.subheader('Fecha de Registro')

	fecha_inicial = st.date_input("Fecha inicial")

	fecha_final = st.date_input("Fecha final")
	

	st.form_submit_button()

#query_expr = 'Código == str(@query["Código"]) and Especie == @query["Especie"] and `Nombre común`== @query["Nombre común"] and @query["Altura"][0] <= Altura <= @query["Altura"][1] and @query["Circunferencia"][0] <= Circunferencia  <= @query["Circunferencia"][1] and @query["Fecha inicial"] <= Fecha <= @query["Fecha final"]'
df_display = raw_data.query(query_expr)						


my_placeholder = st.empty()

#

st.write(df_display)




