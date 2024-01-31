// removes rows with given word in a cell
// to run it, paste it to "Extensions" > "Apps Script" and click run (save the script before)
function deleteRows() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var range = sheet.getDataRange();
  var values = range.getValues();
  
  for(var i = values.length-1; i >= 0; i--) {
    if(values[i].join().match(/robot/)) {
      sheet.deleteRow(i+1);
    }
  }
}
