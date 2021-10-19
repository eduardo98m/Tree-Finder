import streamlit as st
import pydeck as pdk
import numpy as np
import pandas as pd
import plotly.express as px
import pickle
# internal modules
from data_proc import process_df

import datetime 


st.set_page_config(
     page_title="Floresta Tree Finder",
     page_icon="🌳",
     layout="wide",
     initial_sidebar_state="collapsed",
     menu_items={
         'Report a bug': "https://fundacionespacio.com",
         'About': "https://fundacionespacio.com"
     }
 )


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




# Getting the data from Google Drive and processing it to add new needed columns.

# The following lines may change 
#---------------------------------------------------------------------------------------#
raw_data = pd.read_csv("app/results.csv")

"""
with open('species_dict.pkl', 'rb') as handle:
    species_data = pickle.load(handle)

with open('obs_list.pkl', 'rb') as handle:
    obs_list = pickle.load(handle)
"""

raw_data["Altura (m)"] = raw_data["Altura (m)"].apply(
													lambda x: float(x))

raw_data["Circunferencia (m)"] = raw_data["Circunferencia (m)"].apply(
												lambda x: float(x))											

raw_data["DAP (m)"] = raw_data["DAP (m)"].apply(
												lambda x: float(x))

raw_data['Fecha'] = pd.to_datetime(raw_data['Fecha'],format='%d/%m/%Y').dt.date

df_display = raw_data

full_data, species_data, obs_list = process_df(df_display)


#---------------------------------------------------------------------------------------#

#print(map_data)
Atributes = ["lat", 
			"lon",
			"Código", 
			'Tronco ID', 
			'Hojas ID',  
			'Copa ID'
			]

map_data = full_data[Atributes].dropna()

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

	col1, col2 = st.columns(2)
	
	codigo = col1.text_input("Código")
	if codigo != "":
		query_expr.append("Código == @codigo")


	col1.subheader('Especie')

	# The next 4 fields should be linked (The user should only be able to select one)

	
	codigo_de_especie = col1.multiselect("Código de Especie", 
											species_data["Código"] + [],
											default = [] )
	
	especie = col1.multiselect("Especies", species_data["Nombre"] + [],
										 default = [])

	

	nombre_comun = col1.multiselect("Nombre común", 
									species_data["Nombre Común"] + [],
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
										0.0, 50.0, (0., 50.0))
	
	query_expr.append(" @altura[0] <= `Altura (m)` <= @altura[1] and "
					  " @circunferencia[0] <= `Circunferencia (m)` <= @circunferencia[1] "
					  "and @dap[0] <= `DAP (m)` <= @dap[1]")
	
	col2.subheader('Observaciones')

	observaciones = col2.multiselect("Observaciones", obs_list + [],
										 default = [])

	for obs in observaciones:
		query_expr.append("`"+str(obs) + "`" + "== 1")
	
	st.subheader('Fecha de Registro')

	fecha_inicial = st.date_input("Fecha inicial",
								datetime.date(2021, 7, 6))

	fecha_final = st.date_input("Fecha final")

	query_expr.append("@fecha_inicial < Fecha < @fecha_final")


	st.form_submit_button()

df_display = full_data.copy()
if query_expr:
	for expr in query_expr:
		df_display.query(expr, inplace=True)						


my_placeholder = st.empty()

#

st.write(map_data)
st.write(df_display)
st.write(full_data)

st.write(df_display.groupby('Nombre común')["Código"].count())

df_display.groupby("Especie")["Código"].count().plot.pie(subplots=True, autopct='%1.1f%%')


chart_col1, chart_col2 = st.columns(2)

chart_col1.write(px.pie(df_display, names='Nombre común', title='Distribución de Especies'))
chart_col2.write(px.bar(df_display, x='Nombre común', y=obs_list, title="Obervaciones por especie"))



st.write(df_display.describe()[["Altura (m)",  "Circunferencia (m)", "DAP (m)"]])

# Map display

id ="19Xmp0UlcfBU85EdLLV8eQDsJ_5KpLWRu"

img_src = "https://drive.google.com/thumbnail?id=" 





tooltip = {
   "html" : "<b>Especie: </b> {Especie} <br /> "
			"<b>Altura (m): </b> {Altura (m)} <br /> "
			"<b>Circunferencia (m): </b> {Circunferencia (m)} <br /> "
			"<b>DAP (m): </b> {DAP (m)} <br /> "
		   "<img src= " + img_src + "{Tronco ID}>"
		   "<img src= " + img_src + "{Hojas ID}> "
		   "<img src= " + img_src + "{Copa ID}> "
		   "<b>Código: </b> {Código} <br /> ",
   "style": {
        "backgroundColor": "steelblue",
        "color": "white"
   }
}

st.header('Mapa')

query_layer = pdk.Layer(
				"ScatterplotLayer",
				data = map_data.dropna(),
				get_position=['lon', 'lat'],
				radiusScale = 1,
				radius_min_pixels = 4, # Modify to match the scale of the park trees
				radius_max_pixels = 10,
				getFillColor = [0, 158, 96],
				pickable=True,
				)

st.pydeck_chart(pdk.Deck(
			initial_view_state={"latitude": 10.4945, # La Floresta coordinates
			"longitude": -66.8456, "zoom": 15, "pitch":30},
			layers=[query_layer],
			tooltip=tooltip,
		))



with st.sidebar.expander("Update Form"):

	username = st.text_input('Username') 
	password = st.text_input('Password', type = "password" )

	if username == st.secrets["USERNAME"] and password == st.secrets["PASSWORD"]:
		actualizar = st.button("Actualizar")
		if actualizar:
			print("Datos Actualziados")
