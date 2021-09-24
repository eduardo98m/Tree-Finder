# Tree-Finder
## Puropose and motivation:
Tree-Finder is an open source web application build with the purpose of showing on a map the geographic location of a set of trees and, at the same time, give detailed features about every single one of them, obtaining the information through a trees database. We aspire that this application will make easier for its users to keep track of the updated information about a trees population of interest in a graphical way.

We used to manage our trees information using google sheets only. Then we thought that it would be so much better for our understanding and for keeping track of the trees we study if we do it in a more visual way, that's the reason we start developing this project.
## How do we store our data?
Currently we obtain our data from google drive. In it we have a spreadsheet that contains all the information related to each tree, including the name for every single picture we took of them and that are stored in a different folder in the same google drive. Each row is a different tree and each column a different feature.
## How do you do to use your own data?
For you to be able to use your own data in our app you just need to store it in a similar way than us. Having all the trees information in a single spreedsheet, that could count on multiple sheets, and storing all the images in a set of folders using the same file names than you registered in the spreadsheet.

Inside the project, in the PyDrive folder, there is a file called `ids_file.py`. In it there are three variables: 
- `sheet_id`, used to store the google drive id for the spreadsheet;
- `sheets`, that is a dictionary that contains the specific gdrive id for every sheet contained in the spreadsheet and 
- `images_ids`, a dictionary that contains the gdrive id for every image container folder.

**Note:** We asume that the images are stored in .jpg format.
**Note2:** In that same folder you should store the `client_secrets.py` and `credentials_module.py`, used to connect with your Google Drive App and with the Google Drive API.
## Considerations to have when structuring the data:
The worksheet can contain any amount and kind of columns, the only columns to be careful about are the ones that contain image names. For those columns, add the names to the `column_names` variables, and the name of the new columns where you want to store the image ids to the `new_column_names` variable. 

- If, for the image columns, there are rows that have no image associated, use the string "N/A" in that column to indicate it.
- If, for different sheets, there are columns that contain the same kind of information, make sure that the column name is common to.
  For example: if, for different sheets,you have columns referring to the height of the trees, use the same word for those columns in all sheets.
 - Make sure that the image name contained in the spreadsheet is extactly the same as the file name of the image in the images folder.
