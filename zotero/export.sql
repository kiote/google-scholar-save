--- recursiveley exports from top-level collection named "Libraries"
--- replace it with your name if needed
--- use DB Browser for SQLite to access db in ~/Zotero/*.sqlite
WITH RECURSIVE collection_hierarchy AS (
    -- Anchor member: start with the 'Libraries' collection
    SELECT collectionID, collectionName, 0 AS level
    FROM collections 
    WHERE collectionName = 'Libraries'
    
    UNION ALL
    
    -- Recursive member: find all subcollections at any depth
    SELECT c.collectionID, c.collectionName, ch.level + 1
    FROM collections c
    JOIN collection_hierarchy ch ON c.parentCollectionID = ch.collectionID
)
SELECT DISTINCT
    items.key AS ItemKey,
    DOI.value AS DOI,
    CAST(strftime('%Y', Date.value) AS INTEGER) AS Year,
    Title.value AS Title,
    itemNotes.note AS Abstract,
    ch.collectionName AS Subcollection,
    ch.level AS CollectionDepth
FROM
    items
JOIN collectionItems ON items.itemID = collectionItems.itemID
JOIN collection_hierarchy ch ON collectionItems.collectionID = ch.collectionID
LEFT JOIN itemData DOI_Data ON items.itemID = DOI_Data.itemID AND DOI_Data.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'DOI')
LEFT JOIN itemDataValues DOI ON DOI_Data.valueID = DOI.valueID
LEFT JOIN itemData Date_Data ON items.itemID = Date_Data.itemID AND Date_Data.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'date')
LEFT JOIN itemDataValues Date ON Date_Data.valueID = Date.valueID
LEFT JOIN itemData Title_Data ON items.itemID = Title_Data.itemID AND Title_Data.fieldID = (SELECT fieldID FROM fields WHERE fieldName = 'title')
LEFT JOIN itemDataValues Title ON Title_Data.valueID = Title.valueID
LEFT JOIN itemNotes ON items.itemID = itemNotes.itemID AND itemNotes.parentItemID IS NULL
WHERE
    items.itemTypeID = 2  -- Filter for journal articles
    AND items.itemID NOT IN (SELECT itemID FROM deletedItems)
    AND ch.level > 0  -- Exclude the top-level 'Libraries' collection
ORDER BY
    Year DESC, Title;
