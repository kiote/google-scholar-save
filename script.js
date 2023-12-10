async function saveToLibrary() {
  const saveButtons = document.querySelectorAll('[role="button"].gs_or_sav');
  for (let button of saveButtons) {
    button.click();
    await new Promise((resolve) => {
      // Create a new observer instance
      let observer = new MutationObserver((mutations, obs) => {
        let element = document.getElementById('gs_md_albl-d');
        if (element) {
          let labels = element.querySelectorAll('gs_lbl');
          let doneButton = element.querySelector('#gs_lbd_apl');

          const targetContent = 'Affective LitReview';
          
          labels.forEach((element) => {
            if (element.textContent.trim() === targetContent) {
              element.click();
            }
          });

          doneButton.click();
          console.log("SAVED");
          obs.disconnect(); // Stop observing changes
          resolve(); // Resolve the promise
        }
      });
      // Start observing the document with the configured parameters
      observer.observe(document, { childList: true, subtree: true });
    });
    await new Promise((resolve) => setTimeout(resolve, 1000)); // Add a 1-second delay between button clicks
  }
}

saveToLibrary();