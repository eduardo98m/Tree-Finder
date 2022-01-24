from pyparsing import col
import streamlit as st
import streamlit.components.v1 as components
from treeinfo import show_tree_info
from pageinfo import page_info

import pydeck as pdk
import numpy as np
import pandas as pd
import plotly.express as px
import pickle
# internal modules
from data_proc import load_data
from get_data import update_data
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
        "🌳🌲 Árboles de la Floresta 🌴🎋", 
        "📚 Referencias"
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
st.title(st.session_state.current_page)

# Query the trees data


#---------------------------------------------------------------------------------------#


full_data, species_data, obs_list, sectors = load_data()


Atributes = ["lat", 
			"lon",
			"Código",
			"Nombre común",
			"Sector",
			"Observaciones",
			"Fecha",
			"ID Foto Tronco google_id",
			"ID Foto Hojas google_id",
			"ID Foto inflorescencia google_id",
			"ID Foto fruto google_id",
			"ID Foto copa google_id"
			] + obs_list

map_data = full_data[Atributes].dropna()
map_data_query = full_data[Atributes].dropna()

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
								sectors + [],
								default = [])
		
		
		
		if 	nombre_comun != []:
			
			query_expr.append("`Nombre común` == @nombre_comun")
		
		if 	sector != []:
			
			query_expr.append("`Sector` == @sector")
			
			

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
			map_data_query.query(expr, inplace=True)
									
	map_data_query.drop('Fecha', inplace=True, axis=1)
	map_data.drop('Fecha', inplace=True, axis=1)
	
	my_placeholder = st.empty()

	df_display.groupby("Especie")["Código"].count().plot.pie(subplots=True, autopct='%1.1f%%')


	chart_col1, chart_col2 = st.columns(2)

	chart_col1.write(px.pie(df_display, names='Nombre común', title='Distribución de Especies'))
	chart_col2.write(px.bar(df_display, x='Nombre común', y=obs_list, title="Obervaciones por especie"))




	tooltip = {
	"html" :"<b>Código: </b> {Código} <br /> "
			"<b>Especie: </b> {Nombre común} <br /> "
			"<b>Observaciones:<br /> "
			"</b> {Observaciones} <br /> "
			"<img src= " + "https://drive.google.com/thumbnail?id="  + "{ID Foto copa google_id}> ",
	"style": {
			"backgroundColor": "LightGreen",
			"color": "DarkSlateGray",
  			'font-family': 'Courier New',
	}
	}


	st.header('Mapa')

	query_layer = pdk.Layer(
					"ScatterplotLayer",
					data = map_data_query,
					get_position=['lon', 'lat'],
					radiusScale = 1,
					radius_min_pixels = 4, # Modify to match the scale of the park trees
					radius_max_pixels = 10,
					getFillColor = [0, 158, 96],
					pickable=True,
					)
	gray_layer = pdk.Layer(
					"ScatterplotLayer",
					data = map_data,
					get_position=['lon', 'lat'],
					radiusScale = 1,
					radius_min_pixels = 4, # Modify to match the scale of the park trees
					radius_max_pixels = 10,
					getFillColor = [128, 128, 128],
					pickable=False,
					)
	
	pydeck_map = pdk.Deck(
					initial_view_state={"latitude": 10.4945, # La Floresta coordinates
					"longitude": -66.8456, "zoom": 15, "pitch":30},
					layers=[gray_layer, query_layer],
					tooltip=tooltip,
					)


	st.pydeck_chart(pydeck_map)
	
	
	
	st.subheader("Conoce un árbol🌳")
	col1, col2, col3 = st.columns([1, 3, 1])
	selected_tree = col2.selectbox("Busca un arbol por su ID 🌳", map_data_query["Código"])
	
	selected_tree_data = full_data.loc[full_data["Código"] == selected_tree]

	st.markdown("**Especie: **" + str(selected_tree_data.iloc[0]["Nombre común"]))
	st.markdown("**Nombre cientifico** : *" + str(selected_tree_data.iloc[0]["Especie"]) + "*")
	st.markdown("**Observaciones: **" + str(selected_tree_data.iloc[0]["Observaciones"]))
	st.markdown("**Ubicación: **" + str(selected_tree_data.iloc[0]["Dirección"]))

	col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
	if type(selected_tree_data.iloc[0]["ID Foto Tronco"]) == str:
		col1.subheader("Tronco")
		col1.image("https://drive.google.com/uc?export=view&id=" + str(selected_tree_data.iloc[0]["ID Foto Tronco google_id"]), width=300)
	
	if type(selected_tree_data.iloc[0]["ID Foto Hojas"]) == str:
		col2.subheader("Hojas")
		col2.image("https://drive.google.com/uc?export=view&id=" + str(selected_tree_data.iloc[0]["ID Foto Hojas google_id"]), width=300)
	
	if type(selected_tree_data.iloc[0]["ID Foto copa"]) == str:
		col3.subheader("Copa")
		col3.image("https://drive.google.com/uc?export=view&id=" + str(selected_tree_data.iloc[0]["ID Foto copa google_id"]), width=300)
	
	if type(selected_tree_data.iloc[0]["ID Foto inflorescencia"]) == str:
		col4.subheader("Flor")
		col4.image("https://drive.google.com/uc?export=view&id=" + str(selected_tree_data.iloc[0]["ID Foto inflorescencia google_id"]), width=300)
	
	if type(selected_tree_data.iloc[0]["ID Foto fruto"]) == str:
		col5.subheader("Fruto")
		col5.image("https://drive.google.com/uc?export=view&id=" + str(selected_tree_data.iloc[0]["ID Foto fruto google_id"]), width=300)


	
	
	
	col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
	col1.metric("Altura",str(float(selected_tree_data["Altura (m)"])) + " m")
	col2.metric("Circunferencia",str(float(selected_tree_data["Circunferencia (m)"])) + " m")
	col3.metric("Diámetro de la copa Norte-Sur",str(float(selected_tree_data["D. de copa N-S (m)"])) + " m")
	col4.metric("Diámetro de la copa Este-Oeste",str(float(selected_tree_data["D. de copa E-O (m)"])) + " m")


	
	

	

if  st.session_state.current_page == "🌳🌲 Árboles de la Floresta 🌴🎋":
	show_tree_info()

with st.sidebar.expander("Update Form"):

	username = st.text_input('Username') 
	password = st.text_input('Password', type = "password" )

	if username == st.secrets["USERNAME"] and password == st.secrets["PASSWORD"]:
		actualizar = st.button("Actualizar", on_click = update_data)
		if actualizar:
			print("Datos Actualizados")

page_info()