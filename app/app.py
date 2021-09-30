import streamlit as st
import pydeck as pdk
import numpy as np
import pandas as pd
import plotly.express as px
# internal modules
from data_proc import procees_df
import PyDrive.pydrive_functions as pf

import datetime 



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

# Getting the data from Google Drive and processing it to add new needed columns.
pf.produce_results_csv()
raw_data = pd.read_csv("results.csv")

raw_data["Altura (m)"] = raw_data["Altura (m)"].apply(
													lambda x: float(x))

raw_data["Circunferencia (m)"] = raw_data["Circunferencia (m)"].apply(
												lambda x: float(x))											

raw_data["DAP (m)"] = raw_data["DAP (m)"].apply(
												lambda x: float(x))

raw_data['Fecha'] = pd.to_datetime(raw_data['Fecha'],format='%d/%m/%Y').dt.date

df_display = raw_data


# Pydeck
#----------------------------------------------------------------------------------------#
# Display the Map Data
#st.map(map_data) <- Simpler function but almost no customization
# Adding code so we can have map default to the center of the data

#https://drive.google.com/file/d/19Xmp0UlcfBU85EdLLV8eQDsJ_5KpLWRu/view?usp=sharing



#----------------------------------------------------------------------------------------#
# FORM

query = {}
with st.form(key='tree_query'):
	query_expr = []
	st.header('Opciones de Búsqueda')
	#

	col1, col2 = st.beta_columns(2)
	
	codigo = col1.text_input("Código")
	if codigo != "":
		query_expr.append("Código == @codigo")


	col1.subheader('Especie')

	# The next 4 fields should be linked (The user should only be able to select one)

	
	codigo_de_especie = col1.multiselect("Código de Especie", 
											list(species_data["Código"]) + [],
											default = [] )
	
	especie = col1.multiselect("Especies", list(species_data["Nombre"]) + [],
										 default = [])

	

	nombre_comun = col1.multiselect("Nombre común", 
									list(species_data["Nombre Común"]) + [],
									default = [])
	
	
	
	if 	nombre_comun != [] or especie !=[] or nombre_comun != []:
		
		query_expr.append("`Código de Especie` == @codigo_de_especie or "
						" Especie == @especie or "
						"`Nombre común` == @nombre_comun")
		

	col2.subheader('Dimensiones')
	#
	altura = col2.slider('Rango de altura', 0.0, 50.0, (0., 50.0))
	circunferencia = col2.slider('Rango de circunferencia', 
										0.0, 5.0, (0., 5.0))
	
	dap = col2.slider('Rango de DAP', 
										0.0, 1.0, (0., 1.0))
	
	query_expr.append(" @altura[0] <= `Altura (m)` <= @altura[1] and "
					  " @circunferencia[0] <= `Circunferencia (m)` <= @circunferencia[1] "
					  "and @dap[0] <= `DAP (m)` <= @dap[1]")

	
	st.subheader('Fecha de Registro')

	fecha_inicial = st.date_input("Fecha inicial",
								datetime.date(2021, 7, 6))

	fecha_final = st.date_input("Fecha final")

	query_expr.append("@fecha_inicial < Fecha < @fecha_final")


	st.form_submit_button()

df_display = raw_data
if query_expr!=[]:
	for expr in query_expr:
		df_display.query(expr, inplace=True)						


my_placeholder = st.empty()

#

st.write(df_display)

#df_display["Especie"] = df_display.Especie.astype('category')

st.write(df_display.groupby('Nombre común')["Código"].count())#.plot.pie(subplots=True, autopct='%1.1f%%')

df_display.groupby("Especie")["Código"].count().plot.pie(subplots=True, autopct='%1.1f%%')

st.write(px.pie(df_display, names='Nombre común', title='Distribución de Especies'))

st.line_chart(df_display["Altura (m)"])

st.write(df_display.describe()[["Altura (m)",  "Circunferencia (m)", "DAP (m)"]])

# Map display

id ="19Xmp0UlcfBU85EdLLV8eQDsJ_5KpLWRu"

img_src = "https://drive.google.com/thumbnail?id=" + id


Atributes = ["lat", 
			"lon",
			"Especie",
			"Código", 
			"Altura (m)", 
			"Circunferencia (m)",
			"Altura (m)",
			"DAP (m)" 
			]


tooltip = {
   "html" : "<b>Especie: </b> {Especie} <br /> "
			"<b>Altura (m): </b> {Altura (m)} <br /> "
			"<b>Circunferencia (m): </b> {Circunferencia (m)} <br /> "
			"<b>DAP (m): </b> {DAP (m)} <br /> "
		   "<b>Image</b> <img src= " + str(img_src) + "> <br />"
		   "<b>Código: </b> {Código} <br /> ",
   "style": {
        "backgroundColor": "steelblue",
        "color": "white"
   }
}
print("meme1")
map_data = procees_df(df_display)[0][Atributes].dropna()
print("meme2")
st.header('Mapa')
print("meme3")
query_layer = pdk.Layer(
				"ScatterplotLayer",
				data = map_data,
				get_position=['lon', 'lat'],
				radiusScale = 1,
				radius_min_pixels = 4, # Modify to match the scale of the park trees
				radius_max_pixels = 10,
				getFillColor = [0, 158, 96],
				pickable=True,
				)
print("memoso")
st.pydeck_chart(pdk.Deck(
			initial_view_state={"latitude": 10.4945, # La Floresta coordinates
			"longitude": -66.8456, "zoom": 15, "pitch":30},
			layers=[query_layer],
			tooltip=tooltip,
		))
print("meme4")
