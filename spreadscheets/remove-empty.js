function deleteEmpty() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const dataRange = sheet.getDataRange();
    const values = dataRange.getValues();
  
    // Iterate through all rows to identify duplicates in column "C" (index 2)
    values.forEach((row, index) => {
      const cellValue = row[2].toLowerCase().trim(); // Column "C" value
      if (cellValue == "") {
        sheet.deleteRow(index + 1);
        index--; // this is needed since after deletion of a row we need to go back
      } 
    });
  
  }
  