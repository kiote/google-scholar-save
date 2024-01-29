async function saveToLibrary() {
  const saveButtons = document.querySelectorAll('[role="button"].gs_or_sav');

  // Create a new observer instance
  let observer = new MutationObserver((mutations, obs) => {
    let element = document.getElementById('gs_md_albl-d');
    if (element) {
      const links = document.querySelectorAll('a.gs_cb_gen.gs_in_cb.gs_in_cbb');
      let doneButton = element.querySelector('#gs_lbd_apl');
      const LABEL = 'affective lit review';

      for (let link of links) {
        if (link.textContent.trim() === "affective lit review") {
            link.click();
            break;
        }
      }

      doneButton.click();
      console.log("SAVED");
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
