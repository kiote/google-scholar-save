var items = Zotero.getActiveZoteroPane().getSelectedItems();
var changedCount = 0;

// Change item types
await Zotero.DB.executeTransaction(async function () {
    for (let item of items) {
        if (item.itemType !== 'journalArticle') {
            item.setType(Zotero.ItemTypes.getID('journalArticle'));
            await item.saveTx();
            changedCount++;
        }
    }
});

await new Promise(r => setTimeout(r, 1000));

// Attempt to merge
var DupPane = Zotero.getZoteroPanes();
DupPane[0].mergeSelectedItems();
Zotero_Duplicates_Pane.merge();

return `Changed ${changedCount} item(s) to journal article. Total items processed: ${items.length}. Please check if items were merged successfully.`;
