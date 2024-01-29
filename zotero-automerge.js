// found here https://forums.zotero.org/discussion/94721/merge-all 
var DupPane = Zotero.getZoteroPanes();
for(var i = 0; i < 100; i++) { // if you have more than 100 duplicates, increase this number
    await new Promise(r => setTimeout(r, 1000)); // can be smaller than 1000, then it works faster
    DupPane[0].mergeSelectedItems();
    Zotero_Duplicates_Pane.merge();
}