import streamlit as st
import streamlit.components.v1 as components


# Plot modules
import pydeck as pdk
import plotly.express as px

# Data processing
import datetime


# Internal modules
# For data processing and updating
from data_proc import load_data
from get_data import update_data

# For building the app
from treeinfo import show_tree_info
from pageinfo import page_info


# We set configuration of the streamlit webpage

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
# Removal of the default Streamlit Main Menu and footer
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# We list the pages that our apliccation is going to contatin
pages = ["🗺️🌲 Mapa Interactivo",
         "🌳🌲 Árboles de la Floresta 🌴🎋",
         "🗘 Actualizar Datos"
         ]

# The pages are set in the aplication sidebar, so the user can
# jump betweent them using a radio button in the sidebar
st.session_state.current_page = st.sidebar.radio(
    "",
    pages)

# We set the initial page to "🗺️🌲 Mapa Interactivo"
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🗺️🌲 Mapa Interactivo",

# This component is used to make that every time the users changes pages the scrollbar goes to the top
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


full_data, species_data, obs_list, sectors = load_data()


# We only teake into consideration the atributes relevant for the trees in the map
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

# We must always drop the elemts that contain N/A values
# This is beacuse pudeck will throw an error if we try
# to plot a dataframe with N/A values into a pydeck map
map_data = full_data[Atributes].dropna()
map_data_query = full_data[Atributes].dropna()

# FORM
if st.session_state.current_page == "🗺️🌲 Mapa Interactivo":
    # Note: It maybe more efficient and clean to wrap all this section in a function
    with st.form(key='tree_query'):
        st.header('Opciones de Búsqueda')
        query_expr = []  # We create a list to store the user's query

        col1, col2 = st.columns(2)

        # We create a dropdown menu to select the species
        col1.subheader('Especie')
        nombre_comun = col1.multiselect("Especie",
                                        species_data["Nombre Común"] + [],
                                        default=[])

        # If the user selects a species we addd it to the query
        if nombre_comun != []:

            query_expr.append("`Nombre común` == @nombre_comun")

        # We repeat the procces for the sector
        # We create a dropdown menu to select the sector
        sector = col1.multiselect("Sector",
                                  sectors + [],
                                  default=[])

        # If the user selects a sector we addd it to the query
        if sector != []:

            query_expr.append("`Sector` == @sector")

        # Now, for the observations we create a dropdown menu
        # the same as berore.

        col2.subheader('Observaciones')

        observaciones = col2.multiselect("Observaciones", obs_list + [],
                                         default=[])

        # But in this case to add the observation to the query we must set it to one,
        # This is because each observation is a column in the dataframe (a boolean one)
        for obs in observaciones:
            query_expr.append("`"+str(obs) + "`" + "== 1")

        # For the date we use the date inut widgets
        # The initial date is set to July 6 2021 because that is the
        #  date of the first tree in the data
        st.subheader('Fecha de Registro')

        fecha_inicial = st.date_input("Fecha inicial",
                                      datetime.date(2021, 7, 6))

        fecha_final = st.date_input("Fecha final")

        query_expr.append("@fecha_inicial < Fecha < @fecha_final")

        st.form_submit_button()
    # We make a copy of the full dataframe to be able to filter it without affecting the original dataframe
    # We do the same for the map
    df_display = full_data.copy()
    if query_expr:
        for expr in query_expr:
            df_display.query(expr, inplace=True)
            map_data_query.query(expr, inplace=True)

    # If the user has submitted the form, show the results on if the results are not empty
    st.subheader('Resultados de la Búsqueda')
    if len(map_data_query) != 0:
        col1, col2 = st.columns(2)
        col1.write(px.pie(df_display, names='Nombre común',
                   title='Distribución de Especies'))
        col2.write(px.bar(df_display, x='Nombre común',
                   y=obs_list, title="Obervaciones por especie"))

    else:
        st.markdown("No hay árboles que coincidan con tu búsqueda 🌳")

    # Map Section

    st.header('Mapa')

    # We drop the 'Fecha' column because it is not needed in the map (causes an error with Pydeck)
    map_data_query.drop('Fecha', inplace=True, axis=1)
    map_data.drop('Fecha', inplace=True, axis=1)

    # The tooltip is the code that makes it possible for the user to see the information of the tree
    # when the mouse is passed over a point on the map. (Is only active for the trees that belong to the query)
    tooltip = {
        "html": "<b>Código: </b> {Código} <br /> "
        "<b>Especie: </b> {Nombre común} <br /> "
        "<b>Observaciones:<br /> "
        "</b> {Observaciones} <br /> "
        "<img src= " + "https://drive.google.com/thumbnail?id=" +
        "{ID Foto copa google_id}> ",
        "style": {
            "backgroundColor": "LightGreen",
            "color": "DarkSlateGray",
            'font-family': 'Courier New',
        }
    }

    # We cretate two pydeck layers, the trees of the query and other for all the trees
    # The user
    query_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data_query,
        get_position=['lon', 'lat'],
        radiusScale=1,
        radius_min_pixels=4,
        radius_max_pixels=10,
        getFillColor=[0, 158, 96],  # light green in RGB
        pickable=True,  # It is set to true so the user can interact with those trees
    )

    gray_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_data,
        get_position=['lon', 'lat'],
        radiusScale=1,
        radius_min_pixels=4,
        radius_max_pixels=10,
        getFillColor=[128, 128, 128],  # Gray in RGB
        # It is set to false because we don't want the user
        # to be able to interact with the gray trees
        pickable=False,
    )

    pydeck_map = pdk.Deck(
        initial_view_state={"latitude": 10.4945,  # La Floresta coordinates
                            "longitude": -66.8456, "zoom": 15, "pitch": 30},
        # The order is important the query layer must go after the gray layer so the green trees are on top.
        layers=[gray_layer, query_layer],
        tooltip=tooltip,
    )

    # The map is shown
    st.pydeck_chart(pydeck_map)

    # Meet a tree / Specific Tree info section
    st.subheader("Conoce un árbol🌳")
    col1, col2, col3 = st.columns([1, 3, 1])

    # If there are elements in the search (i.e The user query produced results)
    if len(map_data_query) != 0:
        selected_tree = col2.selectbox(
            "Busca un arbol por su ID 🌳", map_data_query["Código"])

        selected_tree_data = full_data.loc[full_data["Código"]
                                           == selected_tree]

        st.markdown("**Especie: **" +
                    str(selected_tree_data.iloc[0]["Nombre común"]))
        st.markdown("**Nombre cientifico** : *" +
                    str(selected_tree_data.iloc[0]["Especie"]) + "*")
        st.markdown("**Observaciones: **" +
                    str(selected_tree_data.iloc[0]["Observaciones"]))
        st.markdown("**Ubicación: **" +
                    str(selected_tree_data.iloc[0]["Dirección"]))

        # We create 5 columns for the posible 5 types of photos that can be show below
        # (Tornco, hoja, copa, fruto, inflorescencia [flor])
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        if type(selected_tree_data.iloc[0]["ID Foto Tronco"]) == str:
            col1.subheader("Tronco")
            col1.image("https://drive.google.com/uc?export=view&id=" +
                       str(selected_tree_data.iloc[0]["ID Foto Tronco google_id"]), width=300)

        if type(selected_tree_data.iloc[0]["ID Foto Hojas"]) == str:
            col2.subheader("Hojas")
            col2.image("https://drive.google.com/uc?export=view&id=" +
                       str(selected_tree_data.iloc[0]["ID Foto Hojas google_id"]), width=300)

        if type(selected_tree_data.iloc[0]["ID Foto copa"]) == str:
            col3.subheader("Copa")
            col3.image("https://drive.google.com/uc?export=view&id=" +
                       str(selected_tree_data.iloc[0]["ID Foto copa google_id"]), width=300)

        if type(selected_tree_data.iloc[0]["ID Foto inflorescencia"]) == str:
            col4.subheader("Flor")
            col4.image("https://drive.google.com/uc?export=view&id=" + str(
                selected_tree_data.iloc[0]["ID Foto inflorescencia google_id"]), width=300)

        if type(selected_tree_data.iloc[0]["ID Foto fruto"]) == str:
            col5.subheader("Fruto")
            col5.image("https://drive.google.com/uc?export=view&id=" +
                       str(selected_tree_data.iloc[0]["ID Foto fruto google_id"]), width=300)

        # We also show the metrics of the tree below
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        col1.metric("Altura", str(
            float(selected_tree_data["Altura (m)"])) + " m")
        col2.metric("Circunferencia", str(
            float(selected_tree_data["Circunferencia (m)"])) + " m")
        col3.metric("Diámetro de la copa Norte-Sur",
                    str(float(selected_tree_data["D. de copa N-S (m)"])) + " m")
        col4.metric("Diámetro de la copa Este-Oeste",
                    str(float(selected_tree_data["D. de copa E-O (m)"])) + " m")

    # If no trees are found we show a message saying that there are no trees matching the search
    else:
        st.markdown("No hay árboles que coincidan con tu búsqueda 🌳")


# If the session_state changes, we change the page

if st.session_state.current_page == "🌳🌲 Árboles de la Floresta 🌴🎋":
    show_tree_info()


# If the session_state changes, we change the page
if st.session_state.current_page == "🗘 Actualizar Datos":
    # This is a actualization form, it should only beaccesed by admins of the page, that why is hidded behind an exapander
    with st.expander("Formulario de Actualización"):
        # The admin shoul write the username an password to access the form to update the data in the aplication
        username = st.text_input('Usuario')
        password = st.text_input('Contraseña', type="password")

        if username == st.secrets["USERNAME"] and password == st.secrets["PASSWORD"]:
            st.success(
                "Bienvenido, presione el botón para actualizar los datos de la aplicación")
            actualizar = st.button("Actualizar", on_click=update_data)
            if actualizar:
                print("Datos Actualizados")

# The page info is a fotter that shows links to the github repo and the website of "Fundacion Espacio"
page_info()
