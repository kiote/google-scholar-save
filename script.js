function saveToLibrary() {
  // Create a new observer instance
  let observer = new MutationObserver((mutations, obs) => {
    let element = document.getElementById('gs_md_d');
    if (element) {
      obs.disconnect(); // Stop observing changes

      let labels = element.querySelectorAll('gs_lbl');
      const targetContent = 'Affective LitReview';
      
      labels.forEach((element) => {
        if (element.textContent.trim() === targetContent) {
          element.click();
        }
      });

      let doneButton = element.querySelector('gs_btn_act');
      console.log("DONE BUTTON");
      console.log(doneButton);
      doneButton.click();
    }
  });
  
  // Start observing the document with the configured parameters
  observer.observe(document, { childList: true, subtree: true });
  
  const saveButtons = document.querySelectorAll('[role="button"].gs_or_sav');
  saveButtons.forEach((button) => {
    button.click();
  });

  
}

saveToLibrary();
