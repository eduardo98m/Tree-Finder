import pandas as pd
import re
from typing import *
import numpy as np
import pickle
import streamlit as st


"""
Script purpose:

Transform the queried data from the database to usable data.
"""


# Convert geo coordinates to metric.
@np.vectorize
def geo_to_decimal_degrees(coordinate: str) -> float:
    """

    Args:
        coordinate: str -> Degrees, minutes, seconds coordinate representation.
                           (Sexagésimal coordinate)
                           Example: "66° 50' 50,4'' E"
    Return:
        float -> Geografical coordinate in decimal format


    References:
        https://gist.github.com/chrisjsimpson/076a82b51e8540a117e8aa5e793d06ec

    """
    if type(coordinate) != str:
        return None
    # First we eliminate the spaces
    dms_str = re.sub(r'\s', '', coordinate)

    # Change the sing if the coordinate is south or west
    sign = -1 if re.search('[swSW]', dms_str) else 1

    # separate the coordinate numbers
    numbers = [*filter(len, re.split('\D+', dms_str, maxsplit=5))]

    # Get each of the sexagesimal values
    degree = numbers[0]
    minute = numbers[1] if len(numbers) >= 2 else '0'
    second = numbers[2] if len(numbers) >= 3 else '0'
    frac_seconds = numbers[3] if len(numbers) >= 4 else '0'
    second += "." + frac_seconds

    # Conversion is performed and returned
    return sign*(int(degree) + float(minute) / 60 + float(second) / 3600)


# Covert the observations
def convert_observations(observations: str) -> List[str]:
    """
    Parses a string with observations separated by comas.

    Args:
        observations: str -> Obesrvations string, each observation must be separated 
                             by a coma. Example "Green, ugly, has errors"

    Retrun:
        List[str] -> List of the parsed observations.

    References:
    """
    if type(observations) != str:
        return None

    observations = observations.lower()

    observations = re.split(',+', observations)

    observations = [obs.strip() for obs in observations]

    return observations


def create_species_dict(raw_data: pd.DataFrame) -> dict:
    """

    Args:
        raw_data  : pd.DataFrame -> Dataframe with all the collected data.

    Retrun:
        species_df: dict -> Dataframe containing the name info of all the 
                                    tree species. (Code, Name, and common name)

    References:
        https://www.geeksforgeeks.org/pandas-find-unique-values-from-multiple-columns/
    """

    species_dict = {
        'Código': list(raw_data['Código de Especie'].unique()),
        'Nombre':  list(raw_data['Especie'].unique()),
        'Nombre Común': list(raw_data['Nombre común'].unique())
    }

    return species_dict


def create_obs(df: pd.DataFrame) -> tuple:
    """
    Creates a boolean column for each observation in the dataframe with a column named 
    "Observaciones", that column must have  observations separated by comas in each 
    of its rows. The function also creates a list of all the unique observations.

    Example: df["Observaciones"] = ["green, tall", "greeen, good", "red, ugly"]

    Args:
        df: pd.DataFrame ->  Dataframe of where the observations are going to be parsed
    Returns:
        df:pd.DataFrame ->  Dataframe with the observations already parsed and inserted.
        list(obs_list): list:-> List with the unique observations of the dataframe.

    """

    df["New_obs"] = df["Observaciones"].map(convert_observations)

    df["New_obs"].fillna(value='', inplace=True)

    obs_list = pd.Series([item for sublist in df['New_obs'].tolist()
                          for item in sublist]).unique()

    for obs in obs_list:
        df[obs] = np.zeros(len(df))

    for index, row in df.iterrows():
        for elem_obs in row['New_obs']:
            df.at[index, elem_obs] = 1

    df.drop("New_obs", axis=1, inplace=True)

    return df, list(obs_list)


def process_df(data: pd.DataFrame) -> None:
    """ 
    Proceses the dataframe and creates aditional elements for the data to be displayed on 
    the app, saves the proccesed elements in the data directory.

    Args:
        data: pd.DataFrame-> The data frame with the trees info.

    Returns:
        None

    """

    data["lat"] = data["Latitud"].map(geo_to_decimal_degrees)
    data["lon"] = data["Longitud"].map(geo_to_decimal_degrees)
    data["Fecha"] = data["Fecha"].map(
        lambda string: str(string).split(" GMT", 1)[0])

    data, obs_list = create_obs(data)

    data.to_csv("app/data/results.csv")

    with open('app/data/species.pkl', 'wb') as handle:
        pickle.dump(create_species_dict(data), handle,
                    protocol=pickle.HIGHEST_PROTOCOL)

    with open('app/data/observations.pkl', 'wb') as handle:
        pickle.dump(obs_list, handle, protocol=pickle.HIGHEST_PROTOCOL)


@st.cache
def load_data() -> None:
    """
    Loads the data from the .csv and the .pkl files.

    Argas:
        None
    Returns:
        df_display: pd.DataFrame -> Dataframe with the data to be displayed on the app.
        species_dict: dict -> Dictionary with the species info.
        obs_list: list -> List with the unique observations.
        sectors: list -> List with the unique sectors.
    """
    # The dataframe is loaded
    raw_data = pd.read_csv("app/data/results.csv")

    # Pickle files are loaded
    with open('app/data/species.pkl', 'rb') as handle:
        species_dict = pickle.load(handle)

    with open('app/data/observations.pkl', 'rb') as handle:
        obs_list = pickle.load(handle)

    with open('app/data/sectors.pkl', 'rb') as handle:
        sectors = pickle.load(handle)

    # Float columns are converted to floats (they are loaded as strings)
    raw_data["Altura (m)"] = raw_data["Altura (m)"].apply(
        lambda x: float(x))

    raw_data["Circunferencia (m)"] = raw_data["Circunferencia (m)"].apply(
        lambda x: float(x))

    raw_data["DAP (m)"] = raw_data["DAP (m)"].apply(
        lambda x: float(x))
    # The date column 'Fecha' is parsed to a datetime object
    raw_data['Fecha'] = pd.to_datetime(
        raw_data['Fecha'], format='%a %b %d %Y %H:%M:%S').dt.date

    df_display = raw_data

    return df_display, species_dict, obs_list, sectors
