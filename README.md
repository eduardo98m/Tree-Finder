# Tree-Finder
## Puropose and motivation:
Tree-Finder is an open source web application build with the purpose of showing on a map the geographic location of a set of trees and, at the same time, give detailed features about every single one of them, obtaining the information through a trees database. We aspire that this application will make easier for its users to keep track of the updated information about a trees population of interest in a graphical way.

We used to manage our trees information using google sheets only. Then we thought that it would be so much better for our understanding and for keeping track of the trees we study if we do it in a more visual way, that's the reason we start developing this project.
## How do we store our data?
Currently we obtain our data from google drive. In it we have a spreadsheet that contains all the information related to each tree, including the name for every single picture we took of them and that are stored in a different folder in the same google drive. Each row is a different tree and each column a different feature.

## How to use your own data?
For using your own data you must create a public google drive and upload the data there, mainly a google sheets file similar to the one we used (link to an example below), this google sheets file has a google app script asociated that is deployed as a web application and processes the google sheets data,  generates a .csv file with the data and then returns a JSON response with the id of the .csv file and a list of the trees sectors, then the python app acceses the google drive and downloads the .csv processes the data (parse obsevartions, converts coordiantes, saves list and dictionaries with unique speciess, etc.) and then saves the .csv to the data directory.

[Link to the example google sheet](https://docs.google.com/spreadsheets/d/1EcDP0P7dB9FYa2iXpSnD5WmczRM8CDPOq4xvHR7XZ64/edit?usp=sharing)

It is important to note that the script tha we use extracts the id of specific columns from the google sheet, so if you change the google sheet you must change the script too.

For your app to be able to acces the google app script you must deploy it as a web application (this is done inside the google app script editor itself) and it must set so it is  executed as you (the person with acces to the google drive) and anyone should be able to acces it (this option are set when deploying the script).

Finally you should copy the API URL given after the deployment and paste it in the API_URL field inside the secrets.toml file (this file should be stored inside the .streamlit/ directory). The contents of this file should look like this:
```
USERNAME = "User1234"
PASSWORD = "password1234"
API_URL = "https://script.google.com/macros/s/da6s5d496fsfdjbasbdiasod/exec"
```

## Considerations to have when structuring the data:
The spreadsheet can contain any amount and kind of columns, the only columns to be careful about are the ones that contain image names, in this version the only images that we use are the ones in the following varible:
```
photo_columns = ["ID Foto Tronco",	"ID Foto Hojas", "ID Foto inflorescencia","ID Foto fruto","ID Foto copa"]
```
If you want to use diferent column names for the photos you must change the `photo_columns` variable to the columns you want to use inside the function `set_photo_columns()` in the google appscript file (line 229).

In case you ar ussing diferent sheets for diferent sectors (i.e diferent sheets  inside the google sheet file for  zones with trees) all the columns betweent sheets must be the same in the same position (see the [example sheet](https://docs.google.com/spreadsheets/d/1EcDP0P7dB9FYa2iXpSnD5WmczRM8CDPOq4xvHR7XZ64/edit?usp=sharing)).
  
Make sure that the image name contained in the spreadsheet is extactly the same as the file name of the image in the images folder.

## Deploying the app

For deploying the app we use the streamlit service, but you can also do it in your own private server.  

If you are deploying the app in streamlit you should be aware that the python version we are using is the 3.7 version. The pipenv package is used to install the dependencies of the app.

We deploying the app you must manually set the .secrets.toml file with the API_UR, the USERNAME and PASSWORD parameters inside the streamlit dashboard (or inside the .streamlit folder if you are deploying the app in a private server).


## The app

We currently have an instance of the app running and you can acces to it via the follwowing link:


[https://share.streamlit.io/eduardo98m/tree-finder/main/app/app.py](https://share.streamlit.io/eduardo98m/tree-finder/main/app/app.py)
