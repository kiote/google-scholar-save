async function clickDeleteButton() {
  const deleteButtons = document.querySelectorAll('a.gs_or_del.gs_or_btn');

  for (let button of deleteButtons) {
    button.click();
    console.log("DELETED");
    
    // Wait for 500ms before continuing to the next iteration
    await new Promise(resolve => setTimeout(resolve, 500));
  }
}

clickDeleteButton(); // Call the function