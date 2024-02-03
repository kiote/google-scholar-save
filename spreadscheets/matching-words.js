function deleteRows() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var range = sheet.getDataRange();
  var values = range.getValues();
  var deleted = 0;
  
  for(var i = values.length-1; i >= 0; i--) {
    if(values[i].join().match(/language/i)) {
      // sheet.getRange(i + 1, 1, 1, sheet.getLastColumn()).setBackground("yellow");
      sheet.deleteRow(i + 1);
      deleted++;
    }
  }

  Logger.log("deleted: " + deleted);