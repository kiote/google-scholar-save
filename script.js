async function saveToLibrary() {
  const saveButtons = document.querySelectorAll('[role="button"].gs_or_sav');

  // Create a new observer instance
  let observer = new MutationObserver((mutations, obs) => {
    let element = document.getElementById('gs_md_albl-d');
    if (element) {
      let labels = element.querySelectorAll('gs_ldb_lbc');
      let doneButton = element.querySelector('#gs_lbd_apl');
      const LABEL = 'Affective LitReview';

      console.log(labels);
      labels.forEach((element) => {
        if (element.textContent.trim() === LABEL) {
          element.click();
        }
      });

      doneButton.click();
      console.log("SAVED");
      obs.disconnect(); // Stop observing changes
    }
  });

  for (let button of saveButtons) {
    button.click();
    await new Promise((resolve) => {
      // Start observing the document with the configured parameters
      observer.observe(document, { childList: true, subtree: true });

      // Add a 1-second delay between button clicks
      setTimeout(() => {
        observer.disconnect(); // Stop observing changes
        resolve(); // Resolve the promise
      }, 1000);
    });
  }
}

saveToLibrary();
