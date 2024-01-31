function colorAndDeleteDuplicateRows() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const dataRange = sheet.getDataRange();
  const values = dataRange.getValues();
  let seenValues = new Set();
  let duplicateRows = [];

  // Iterate through all rows to identify duplicates in column "C" (index 2)
  values.forEach((row, index) => {
    const cellValue = row[2].toLowerCase().trim(); // Column "C" value
    if (seenValues.has(cellValue)) {
      // If value is already seen, mark row index as duplicate
      duplicateRows.push(index);
    } else {
      seenValues.add(cellValue);
    }
  });

  // Reverse iterate through the duplicate rows to delete them without affecting indices
  for (let i = duplicateRows.length - 1; i >= 0; i--) {
    let rowIndex = duplicateRows[i];
    sheet.getRange(rowIndex + 1, 1, 1, sheet.getLastColumn()).setBackground("yellow");
    // Delete row
    sheet.deleteRow(rowIndex + 1);
  }
}