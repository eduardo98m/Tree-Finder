from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import pandas as pd
import requests
import json
import os

directorio_credentials = 'credentials_module.json'
sheet_id = "1xBSf09SDMTn2gNMAJrk45kFUsM-SxJA1PWS3ZqtTGmE"
sheets = {'Sector 1': '850096063',
          'Sector 2': '1546506205',
          'Sector 3': '1214437073',
          'Sector 4': '2059242964'}

# Method used to login to google drive.

def login():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(directorio_credentials)

    if (gauth.access_token_expired):
        gauth.Refresh()
        gauth.SaveCredentialsFile(directorio_credentials)
    else:
        gauth.Authorize()
    
    return GoogleDrive(gauth)

def write_trees_csvs():
    credentials = login()
    with open(directorio_credentials) as json_file:
        bearer = json.load(json_file)["token_response"]["access_token"]
    
    for sheet in sheets.keys():
        url = 'https://docs.google.com/spreadsheets/d/' + sheet_id + '/gviz/tq?tqx=out:csv&gid=' + sheets[sheet]
        headers = {'Authorization': 'Bearer ' + bearer}
        res = requests.get(url, headers=headers)
        with open(sheet + '.csv', 'wb') as f:
            f.write(res.content)
    
# Method that reads the csv that contain the data and returns its dataframes, having the extra columns
# already appended.

def get_trees_dataframes():
    
    column_names = pd.read_csv('Sector 1.csv').columns
    df = pd.DataFrame(columns = column_names)
    for elem in sheets.keys():
        try:
            df_aux = pd.read_csv(elem + ".csv")
            df_aux.loc[:,'Sector'] = elem.split(" ")[1]
            try:
                df = pd.concat([df, df_aux])
            except Exception as e:
                print(e)
        except:
            print("The sheet for sector %s is empty or is missing." % elem.split(" ")[1])
    
        os.remove(elem + ".csv")

    return df

def get_image_id(name):

    try:
        credentials = login()
        file_list = credentials.ListFile({'q': "'18kj_O5OGdTXRhBrZLLkfj7KXvHnGKgHu' in parents and trashed=false"}).GetList()
        for file in file_list:
            if(file['title']==str(name)+".jpg"):
                result = file['id']
                return result
        file_list = credentials.ListFile({'q': "'1hAA33dTtetXMe7hjt4_SJI26yL2xQtWq' in parents and trashed=false"}).GetList()
        for file in file_list:
            if(file['title']==str(name)+".jpg"):
                result = file['id']
                return result
        file_list = credentials.ListFile({'q': "'1zFeJI4Tzwybo4jNmdOdZ_leACayhAgOD' in parents and trashed=false"}).GetList()
        for file in file_list:
            if(file['title']==str(name)+".jpg"):
                result = file['id']
                return result
        file_list = credentials.ListFile({'q': "'1VvTY9_IpU0VfYQnqh9GiNUVtHq4QhBre' in parents and trashed=false"}).GetList()
        for file in file_list:
            if(file['title']==str(name)+".jpg"):
                result = file['id']
                return result

    except Exception as e:
        print("The exception is: " + str(e))
    return None

# Here we iterate by the column_name column. Reading the file's name we search for its id and
# insert it in a new column called new_column_name

def get_image_ids_aux(column_name, df, new_column_name):
    
    df_aux = df[column_name]
    id_aux = []
    for elem in df_aux:
        if (elem != 'NaN' and elem != None):
            id_aux.append(get_image_id(elem))
        else:
            id_aux.append(None)

    df[new_column_name] = id_aux
    return df

def get_image_ids(df):

    column_names = ['ID Foto Tronco', 'ID Foto Hojas', 'ID Foto inflorescencia', 'ID Foto fruto', 'ID Foto copa']
    new_column_names = ['Tronco ID', 'Hojas ID', 'Flores ID', 'Fruto ID', 'Copa ID']

    for num in range(len(column_names)):
        df = get_image_ids_aux(column_names[num], df, new_column_names[num])
    
    return df

if __name__ == '__main__':
    write_trees_csvs()
    df = get_trees_dataframes()
    df2 = get_image_ids(df)
    df2.to_csv('result.csv')