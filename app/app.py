import streamlit as st
import streamlit.components.v1 as components
from treeinfo import show_tree_info

import pydeck as pdk
import numpy as np
import pandas as pd
import plotly.express as px
import pickle
# internal modules
from data_proc import load_data

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


pages = ["🗺️🌲 Mapa Interactivo",
        "🌳🌲🌴🎋 Árboles de la Floresta", 
        "📚 References"
]

st.session_state.current_page = st.sidebar.radio(
                                    "",
                                    pages)


if 'current_page' not in st.session_state:
    st.session_state.current_page = "🗺️🌲 Mapa Interactivo",

# Esto hace que al cambiar de  página se resetee la vista
components.html(
    f"""
        <p>{st.session_state.current_page }</p>
        <script>
            window.parent.document.querySelector('section.main').scrollTo(0, 0);
        </script>
    """,
    height=0
)


# App layout #
st.title('La Floresta Tree Finder')


# Query the trees data


#---------------------------------------------------------------------------------------#


full_data, species_data, obs_list = load_data()


Atributes = ["lat", 
			"lon",
			"Código", 
			"ID Foto Tronco google_id",
			"ID Foto Hojas google_id",
			"ID Foto inflorescencia google_id",
			"ID Foto fruto google_id",
			"ID Foto copa google_id"
			]

map_data = full_data[Atributes].dropna()


# FORM
if st.session_state.current_page == "🗺️🌲 Mapa Interactivo":

	query = {}
	with st.form(key='tree_query'):
		query_expr = []
		st.header('Opciones de Búsqueda')
		#

		col1, col2 = st.columns(2)
		

		col1.subheader('Especie')

		# The next 4 fields should be linked (The user should only be able to select one)

		
		nombre_comun = col1.multiselect("Especie", 
										species_data["Nombre Común"] + [],
										default = [])
		

		sector = col1.multiselect("Sector", 
								["Sector 1", "Sector 2", "Sector 3", "Sector 4"] + [],
								default = [])
		
		
		
		if 	nombre_comun != []:
			
			query_expr.append("`Nombre común` == @nombre_comun")
			

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
			"<img src= " + img_src + "{ID Foto Tronco google_id}>"
			"<img src= " + img_src + "{ID Foto Hojas google_id}> "
			"<img src= " + img_src + "{ID Foto copa google_id}> "
			"<img src= " + img_src + "{ID Foto inflorescencia google_id}>"
			"<img src= " + img_src + "{ID Foto fruto google_id}>"
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

if  st.session_state.current_page == "🌳🌲🌴🎋 Árboles de la Floresta":
	show_tree_info()

with st.sidebar.expander("Update Form"):

	username = st.text_input('Username') 
	password = st.text_input('Password', type = "password" )

	if username == st.secrets["USERNAME"] and password == st.secrets["PASSWORD"]:
		actualizar = st.button("Actualizar")
		if actualizar:
			print("Datos Actualziados")
