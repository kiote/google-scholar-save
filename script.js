function saveToLibrary() {
  // Create a new observer instance
  let observer = new MutationObserver((mutations, obs) => {
    let element = document.getElementById('gs_md_albl-d-bdy');
    if (element) {
      console.log("Element exists!");
      obs.disconnect(); // Stop observing changes

      let elements = element.querySelectorAll('*');
      const targetContent = 'Affective LitReview';
      
      elements.forEach((element) => {
        if (element.textContent.trim() === targetContent) {
          element.click();
        }
      });
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
