from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import pandas as pd
import requests
import json
import os
import PyDrive.ids_file as ids_file

directorio_credentials = 'credentials_module.json'

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

# Method that reads every sheet contained in the data worksheet and creates a new .csv file for every single one of them.
# This, with the intention of making the data more handy to use.

def write_trees_csvs():
    credentials = login()
    with open(directorio_credentials) as json_file:
        bearer = json.load(json_file)["token_response"]["access_token"]
    
    for sheet in ids_file.sheets.keys():
        url = 'https://docs.google.com/spreadsheets/d/' + ids_file.sheet_id + '/gviz/tq?tqx=out:csv&gid=' + ids_file.sheets[sheet]
        headers = {'Authorization': 'Bearer ' + bearer}
        res = requests.get(url, headers=headers)
        with open(sheet + '.csv', 'wb') as f:
            f.write(res.content)
    
# Method that reads the csv that contain the data and returns its dataframes, having the extra columns
# already appended.

def get_trees_dataframes():
    
    column_names = pd.read_csv('Sector 1.csv').columns
    df = pd.DataFrame(columns = column_names)
    for elem in ids_file.sheets.keys():
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

# Method that, given an image name and a dictionary containing ids for image folders it returns
# the id of that image if its contained in any of those folders.

def get_image_id(name,images_ids):

    credentials = login()
    try:
        for key in images_ids.keys():
            file_list = credentials.ListFile({'q': "'"+images_ids[key]+"' in parents and trashed=false"}).GetList()
            for file in file_list:
                if(file['title']==str(name)+".jpg"):
                    result = file['id']
                    return result

    except Exception as e:
        print("The exception is: " + str(e))
    return None

# Here we iterate by the column_name column. Reading the file's name we search for its id and
# insert it in a new column called new_column_name

def get_image_ids_aux(column_name, df, new_column_name, images_ids):
    
    df_aux = df[column_name]
    id_aux = []
    for elem in df_aux:
        if (elem != 'NaN' and elem != None):
            id_aux.append(get_image_id(elem, images_ids))
        else:
            id_aux.append(None)

    df[new_column_name] = id_aux
    return df

# Method that, given the dataframe containing the trees data and a dictionary containing the google drive
# id for different image folders it returns a modified dataframe with new columns that contain the file ids
# for every picture of those trees contained in the .csv

def get_image_ids(df, images_ids):

    column_names = ['ID Foto Tronco', 'ID Foto Hojas', 'ID Foto inflorescencia', 'ID Foto fruto', 'ID Foto copa']
    new_column_names = ['Tronco ID', 'Hojas ID', 'Flores ID', 'Fruto ID', 'Copa ID']

    for num in range(len(column_names)):
        df = get_image_ids_aux(column_names[num], df, new_column_names[num], images_ids)
    
    return df

if __name__ == '__main__':
    write_trees_csvs()
    df = get_trees_dataframes()
    df2 = get_image_ids(df, ids_file.images_ids)
    df2.to_csv('result.csv')
