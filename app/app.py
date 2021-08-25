import streamlit as st
import pydeck as pdk
import numpy as np
import pandas as pd



# App layout #
st.title('La Floresta Tree Finder')


# Filters


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

# Map

# Query the Map Data
map_data = pd.DataFrame({
    #'awesome cities' : ['Chicago', 'Minneapolis', 'Louisville', 'Topeka'],
    'lat' : [41.868171, 44.979840,  38.257972, 39.030575],
    'lon' : [-87.667458, -93.272474, -85.765187,  -95.702548]
})

# Display the Map Data
#st.map(map_data) <- Simpler function but almost no customization
# Adding code so we can have map default to the center of the data
midpoint = (np.average(map_data['lat']), np.average(map_data['lon']))

st.header('Mapa')
st.pydeck_chart(pdk.Deck(
			initial_view_state={"latitude": midpoint[0], 
			"longitude": midpoint[1], "zoom": 4},
			layers=[
				pdk.Layer(
				"ScatterplotLayer",
				data = map_data,
				get_position=['lon', 'lat'],
				radiusScale = 250,
				radiusMinPixels = 5,
				getFillColor = [248, 24, 148],)
			]
		))



with st.form(key='tree_query'):
	query = {}
	st.header('Opciones de Búsqueda')
	#

	col1, col2 = st.beta_columns(2)
	query["Código"] = col1.text_input("Código")

	col1.subheader('Especie')

	# The next 4 fields should be linked (The user shoul only be able to select one)
	query["Código de Especie"] = col1.text_input('Código de la Especie')
	query["Especie"] = col1.multiselect("Especies", ["Especie 1", "Especie 2"])
	query["Nombre común"] = col1.multiselect("Nombre común", 
											["Especie nc 1", "Especie nc 2"])

	col2.subheader('Dimensiones')
	#
	query["Altura"] = col2.slider('Rango de altura', 0.0, 50.0, (25.0, 35.0))
	query["Circunferencia"] = col2.slider('Rango de circunferencia', 
										0.0, 50.0, (25.0, 35.0))
	
	query["DAP"] = col2.slider('Rango de DAP', 
										0.0, 50.0, (25.0, 35.0))
	
	st.subheader('Fecha de Registro')

	query["Fecha inicial"] = st.date_input("Fecha inicial")

	query["Fecha final"] = st.date_input("Fecha final")
	

	st.form_submit_button()

	
my_placeholder = st.empty()



# Display the items in the map (With selector)


# Display selected item pictures





