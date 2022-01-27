/*
 * Script to export data of the from the sheet where the tree info is stored to the a 
 * Sources: 
 * Michael Derazon (https://gist.github.com/mderazon/9655893)
*/
  



function doGet(){
 /*
 Main function that is going to be exceuted when the API is called, 
 the name doGet is important as it signals to that is going to be 
 a response to a url request.

 The function returns a JSON response of the form:
  output = {
    "csv id" :csv_file_id,
    "Sectores":sectores 
  }
  
  Being the inside varibles
  csv_file_id: string
  sectores: Array (list)
 */

  // First we read the values of the API_control sheet to set what sheet are going to be proccesed
  // adn other parameters of the excecution
  spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  var api_control_sheet = spreadsheet.getSheetByName("API_Control");
  api_control_sheet.activate();
  var csv_folder = api_control_sheet.getRange('E3').getValue();
  var image_not_found_id = api_control_sheet.getRange('E2').getValue();
  var sectores = api_control_sheet.getRange("A2:A100000").getValues().join().split(',').filter(Boolean);
  var sectores_folder_id = api_control_sheet.getRange("B2:B100000").getValues().join().split(',').filter(Boolean); 
  
  Logger.log("Execution started")
  // We made a copy of the current spreadsheet to work in it separetly
  Logger.log("Creating copy of the spreadsheet")
  sheet_id = saveAsSpreadsheet(csv_folder)
  var spreadsheet = SpreadsheetApp.openById(sheet_id); 
  Logger.log("Done")

  // The we asing each photo column the corresponding ID of the image the containd 
  // And also create a new column called sector for each element.
  Logger.log("Searching Photo ids and setting sectors")
  for (var sec_index in sectores){
    
    try {
      var sector = sectores[sec_index];
      var sector_folder_id = sectores_folder_id[sec_index];
      set_photo_columns(spreadsheet, sector, sector_folder_id, image_not_found_id);
      set_sector(spreadsheet, sector);
    } catch (e) {
      // Logs an ERROR message.
      console.error('File not found ' + e);
      console.error('Unable to process ' + sector);
    }

  }
  Logger.log("Done")

  // We combine the sheets in the Final Data Sheet
  Logger.log("Combining Sheets")
  combineSheets(spreadsheet, sectores, "Final Data")

  Logger.log("Done")
  Logger.log("Writing files and returning json")
  // The previous test.csv file that was on that directory is deleted
  delteFile("test.csv", image_not_found_id)
  // The new test.csv file is created (and we get the google drive id of that file)
  var csv_file_id = saveLoadcsv_testAsCSV("test.csv", spreadsheet.getSheetByName("Final Data"), csv_folder)  
  
  // Now we do the API thing
  var output = {
    "csv id":csv_file_id,
    "Sectores":sectores 
  }
  
  Logger.log("Done")
  // We then retrun the JSON REsponse
  return ContentService.createTextOutput(JSON.stringify(output) ).setMimeType(ContentService.MimeType.JSON); 

}




function combineSheets(spreadsheet, sheetsNames, finalSheetName) {

  // Combines the sheets contents in one new sheet.
  // Args:
  //  sheetsNames: Array (list) -> With the names of the sheets to be combined
  //  finalSheetName: str -> Name of the sheet where the other sheets are going to be combined
  // Returns:
  //  None
  
  var finalValues = [];
  for (var index in sheetsNames){
    var s = spreadsheet.getSheetByName(sheetsNames[index]);

    // This if is to only get the headers from the first sheet
    if (index == 0){
      finalValues = finalValues.concat(s.getRange(1,1,s.getLastRow(),s.getLastColumn()).getValues());
    } 
    else {
      finalValues = finalValues.concat(s.getRange(2,1,s.getLastRow(),s.getLastColumn()).getValues());
    }
    
  }

  var finalDataSheet = spreadsheet.insertSheet();
  finalDataSheet.setName(finalSheetName);
  finalDataSheet.getRange(1,1,finalValues.length,s.getLastColumn()).setValues(finalValues);

}


function saveAsSpreadsheet(folder_id){ 
  // Creates a copy of the current google sheet
  // It saves the copy with the name "Copy Sheet" and deletes a previous copy
  // In case there was a previous copy
  // Args:
  //  folder_id: str-> Id of the folder where the google sheet is going to be saved
  // Returns:
  //  sheet_id: str -> Id of the google sheet 
  var sheet = SpreadsheetApp.getActiveSpreadsheet();
 
  var destFolder = DriveApp.getFolderById(folder_id); 
  
  // If there was a previous sheet it is deleted
  delteFile("Copy Sheet", folder_id)
  
  DriveApp.getFileById(sheet.getId()).makeCopy("Copy Sheet", destFolder); 
  sheet_id = destFolder.getFilesByName("Copy Sheet").next().getId();
  return sheet_id
}

function delteFile(myFileName, folder_id) {
  // Deletes a file
  // Args:
  //  myFileName: str-> Name of the file inside the folder.
  //  folder_id : str-> Id of the folder where the file is located.
  // Returns:
  //  None
  var allFiles, myFolder, thisFile;

  myFolder = DriveApp.getFolderById(folder_id);

  allFiles = myFolder.getFilesByName(myFileName);

  while (allFiles.hasNext()) {//If there is another element in the iterator
    thisFile = allFiles.next();
    thisFile.setTrashed(true);
  };
};

function Get_photo_id(folder_id, photo_name, image_not_found_id){
  // Returns the id of a file inside a folder given the folder id and the file name
  // Args:
  //  folder_id: str -> folder id of the ubication of the image
  //  photo_name: str -> name of the photo (withouth the extension)
  //  image_not_found_id: str -> google drive id of the image that will be returned if no image is found
  // Returns:
  //  str -> google Id of an image
  var folder = DriveApp.getFolderById(folder_id); // We get to the folder containing the file (using its ID)
  var searchFor = 'title contains "' +photo_name+'"'; //Search for a file that contains the phot title 
  // (We dont use the = operator beacuse of the file extenstion is not included in the name on the sheet)
  var Files = folder.searchFiles(searchFor); // Returns a file iterator
 
  try {
    var File = Files.next(); // We asume the iterator only has one file (ther should not be duplicate photos on the folder)
    return File.getId();     // Function to time.
  } catch (e) {
    // Logs an ERROR message.
    console.error('File not found ' + e);
    // Instead of returning error we pass the script the id of a not found
    return image_not_found_id; 
  }
  
}

function set_photo_column_id(spreadsheet, sector, column_name, sector_folder_id, image_not_found_id){
  // Sets the colums of the spreadsheet with the ids of the column
  // Args:
  //  spreadsheet: Spreadsheet -> spreadhseet where the operations are being made
  //  sector: str -> Name of the sector (this is also the name of the sheet)
  //  column_name: str -> Name of the column that contains the images (photo) names
  //  sector_folder_id: str -> Id of the folder where the images are stored
  //  image_not_found_id: str -> Id of the placeholder image to return if no image is found
  // Returns:
  //  None
   
  var sheet = spreadsheet.getSheetByName(sector);
  sheet.activate()
  array = getByName(column_name, sector);
  var photo_id_array = new Array(array.length);
  for (var index in array){
    var photo_name = array[index][0];
    photo_id_array[index] = [Get_photo_id(sector_folder_id, photo_name, image_not_found_id)];
  
  }
  //Logger.log(photo_id_array);
  var new_col_pos = sheet.getLastColumn()+1;
  sheet.insertColumns(new_col_pos) ;
  var range = sheet.getRange(2, new_col_pos, array.length, 1);
  try {
    range.setValues(photo_id_array);}
  catch(e){
    console.error('Unable to set column: ' + e);
    console.error('Probably the sheet is empty');
  }
  var title_range  = sheet.getRange(1, new_col_pos);
  title_range.setValues([[column_name + " google_id"]]);
}

function set_photo_columns(spreadsheet, sector, sector_folder_id, image_not_found_id){
  
  // Wrapper function that applies the 'set_photo_column_id' function to the columns specified in the
  // photo_columns variable 
  // Args:
  //  spreadsheet: Spreadsheet -> spreadhseet where the operations are being made
  //  sector: str -> Name of the sector (this is also the name of the sheet)
  //  sector_folder_id: str -> Id of the folder where the images are stored
  //  image_not_found_id: str -> Id of the placeholder image to return if no image is found
  // Returns:
  //  None
  
  photo_columns = ["ID Foto Tronco",	"ID Foto Hojas", "ID Foto inflorescencia","ID Foto fruto","ID Foto copa"]
  for (var index in photo_columns){
    var column_name = photo_columns[index]
    set_photo_column_id(spreadsheet, sector, column_name, sector_folder_id, image_not_found_id)
  
  }
  
}

function getByName(colName, sheetName) {
  // Gets the column values of a sheet using the name of the column
  // Args:
  //  colName: str-> Name of the column (must be unique)
  //  sheetName: str > Name of the sheet
  // Returns:
  //  ragnge type cointaining the values of the specified column
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  var data = sheet.getRange("A1:1").getValues();
  var col = data[0].indexOf(colName);
  if (col != -1) {
    return sheet.getRange(2,col+1,sheet.getLastRow()-1).getValues();
  }
}

function set_sector(spreadsheet, sector){
  // For an specified sector (sheet), a new column called 'Sector' is created and its values are set to the sector str. 
  // Args:
  //  spreadsheet: Spreadsheet where the sheets are located
  //  sector: str -> Name of the sector (this is also the name of the sheet) where the values are going to be set
  // Returns: 
  //  None
  var sheet = spreadsheet.getSheetByName(sector);
  sheet.activate();
  var array = [];
  
  for (var n=0 ; n<sheet.getLastRow()-1;n++){
    array.push([sector]);
  }
  var new_col_pos = sheet.getLastColumn()+1;
  sheet.insertColumns(new_col_pos) ;
   try {
    var range = sheet.getRange(2, new_col_pos, array.length, 1);
    range.setValues(array);}
  catch(e){
    console.error('Unable to set column: ' + e);
    console.error('Probably the sheet is empty');
  }
  var title_range  = sheet.getRange(1, new_col_pos);
  title_range.setValues([["Sector"]]);
}





function saveLoadcsv_testAsCSV(exportFileName, sheet, csv_folder) {
  // Saves a sheet as a .csv file.
  // Args:
  //  exportFileName: str-> Name of the csv file that will saved
  //  sheet: sheet type. Sheet that is going to be exported as a .csv file
  //  csv_folder: str-> Google drive od of the folder where the csv is going to be saved  

  //Note: Function Copied from Michael Derazon (https://gist.github.com/mderazon/9655893)
  var folder = DriveApp.getFolderById(csv_folder);//this is the folder where the exporte csv will be saved
  fileName = sheet.getName() + ".csv";
  // convert all available sheet data to csv format
  var csvFile = convertcsv_testRangeToCsvFile_(sheet);
  // create a file in the Docs List with the given name and the csv data
  var file = folder.createFile(exportFileName, csvFile);
  // set the file so anyone can access it
  file.setSharing(DriveApp.Access.ANYONE, DriveApp.Permission.VIEW);
  return file.getId()
}





function convertcsv_testRangeToCsvFile_(sheet) {
  // Function that creates a csv file using the contents of a (single) sheet of a google spreadshet
  // Args:
  //  sheet:(sheet type) The sheet that will be converted to a .csv format 
  // Note: Function Copied from Michael Derazon (https://gist.github.com/mderazon/9655893)
  // get available data range in the spreadsheet
  var activeRange = sheet.getDataRange();
  try {
    var data = activeRange.getValues();
    var csvFile = undefined;

    // loop through the data in the range and build a string with the csv data
    if (data.length > 1) {
      var csv = "";
      for (var row = 0; row < data.length; row++) {
        for (var col = 0; col < data[row].length; col++) {
          if (data[row][col].toString().indexOf(",") != -1) {
            data[row][col] = "\"" + data[row][col] + "\"";
          }
        }
        if (row < data.length-1) {
          csv += data[row].join(",") + "\r\n";
        }
        else {
          csv += data[row];
        }
      }
      csvFile = csv;
    }
    return csvFile;
  }
  catch(err) {
    Logger.log(err);
  }
}