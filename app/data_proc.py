import pandas as pd
import re
from typing import *
import numpy as np


"""
Script purpose:

Transform the queried data from the database to usable data.

raw_data:
    Tasks:
        * Covert geo coordinates to metric.
        * Calculate the tree radius. (Average)
        * Get the photos google-ids. (Ian's part)
        * Covert the observations. [Not Done]
            * Covertobservations into a list
            * Create new columns for each observation
            * Asing True//False values 
        * Create species dataframe. [Done]
    
    Testing:
"""


# Convert geo coordinates to metric.
@np.vectorize
def geo_to_decimal_degrees(coordinate:str)->float: 
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
    return  sign*(int(degree) + float(minute) / 60 + float(second) / 3600)


# Covert the observations
def convert_observations(observations:str)->List[str]:
    """

    Args:
        observations: str ->

    Retrun:
        List[str]

    References:
    """
    if type(observations) != str:
        return None

    observations = observations.lower()

    observations = re.split(',+', observations)

    return observations


def create_species_df(raw_data:pd.DataFrame) -> pd.DataFrame:
    """
    
    Args:
        raw_data  : pd.DataFrame -> Dataframe with all the collected data.

    Retrun:
        species_df: pd.DataFrame -> Dataframe containing the name info of all the 
                                    tree species. (Code, Name, and common name)

    References:
        https://www.geeksforgeeks.org/pandas-find-unique-values-from-multiple-columns/
    """

    species_df = pd.concat([raw_data['Código de Especie'],
                            raw_data['Especie'],
                            raw_data['Nombre común']]).unique()
    
    return species_df


def procees_df(data):
    """
    
    """

    data["lat"] = data["Latitud"].map(geo_to_decimal_degrees)
    data["lon"] = data["Longitud"].map(geo_to_decimal_degrees)
    
    #data["New_obs"] = data["Observaciones"].map(convert_observations)



    return data, create_species_df(data)


"""
# Data 

raw_data = pd.read_csv("data\Parque Aruflo Levantamiento - Sector 1.csv")

print(raw_data["Observaciones"])

df, especies = procees_df(raw_data)


print(df[['lat', 'lon']].dropna())
print(especies)
"""