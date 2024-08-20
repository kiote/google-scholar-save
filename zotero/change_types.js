var items = Zotero.getActiveZoteroPane().getSelectedItems();
var changedCount = 0;

Zotero.DB.executeTransaction(async function () {
    for (let item of items) {
        alert(item.itemType);
        if (item.itemType !== 'journalArticle') {
            item.setType(Zotero.ItemTypes.getID('journalArticle'));
            await item.saveTx();
            await new Promise(r => setTimeout(r, 1000));
            changedCount++;
        }
    }
});

return `Changed ${changedCount} item(s) to journal article. Total items processed: ${items.length}`;
