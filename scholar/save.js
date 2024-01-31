// Copy-paste this to browser console
// it's recommended that you make sure what this code does before running it
// for example, that it doesn't steal your bank account details
async function saveToLibrary(label) {
  const saveButtons = document.querySelectorAll('[role="button"].gs_or_sav');

  // Create a new observer instance
  let observer = new MutationObserver((mutations, obs) => {
    let element = document.getElementById('gs_md_albl-d');
    if (element) {
      const links = document.querySelectorAll('a.gs_cb_gen.gs_in_cb.gs_in_cbb');
      let doneButton = element.querySelector('#gs_lbd_apl');

      for (let link of links) {
        if (link.textContent.trim() === label) {
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
      }, 500);
    });
  }
}

saveToLibrary('affective lit review');
