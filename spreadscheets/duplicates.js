/**
 * Sets the background color of rows with duplicate values in column "C" to yellow.
 * Assumes the active sheet is the target and column "C" is the column to check for duplicates.
 */
function colorDuplicateRows() {
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

  // Color the identified duplicate rows in yellow
  duplicateRows.forEach(rowIndex => {
    sheet.getRange(rowIndex + 1, 1, 1, sheet.getLastColumn()).setBackground("yellow");
  });
}
