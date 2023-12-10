function clickSaveButtons() {
  const saveButtons = document.querySelectorAll('[role="button"]');
  saveButtons.forEach((button) => button.click());
}

clickSaveButtons();
