fuction clickDeleteButton() {
  const deleteButton = document.querySelector('.gs_or_del.gs_or_btn'); // Select the delete button

  if (deleteButton) {
    deleteButton.click(); // Click the delete button if it exists
    console.log("DELETED");
  } else {
    console.log("DELETE button not found");
  }
}

clickDeleteButton(); // Call the function to perform the action
