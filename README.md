# google-scholar-save

The current method to save articles found on Google Scholar to CSV is to do manual steps:

* click save
* choose a label from your library
* click done

After that, you can go to your library; there is an "Export all" button.

It might be fine for a couple of articles, but if you have 900 articles, it gives you 900x3 clicks—a very dull and daunting task.

## Solution

This repo offers you a JS script to copy-paste to the [browser console](https://balsamiq.com/support/faqs/browserconsole/) and wait until it does all the clicks. After that, you must do only one click - "Export all".

## Warning

Most of this code Chat-GPT generated, so don't expect much from it's quality. Last time I checked it worked :)

## Tools

### LitReview Workflow

#### MassReader

Get PDFs from zotero and convert it to text: `python3 pdf/mass_reader.py`. This is needed for the workflow: Get PDF -> convert to text -> feed to openAI model -> ask questions -> write answers.

Expects file `docs/in.txt` to have paper's DOI on each line.

`mass_reader` script covers `Get PDF -> convert to text` part of the workflow.

#### RAG

One by one takes text from `docs/papers` (only .txt files) and runs series of questions. Saves answers to the `docs/papers` .md files

```
export LANGSMITH_TRACING="true"
export OPEN_AI_KEY="YOUR_OPEN_AI_KEY"
export LANGSMITH_API_KEY="YOUR_KEY_FROM_LANGSMITH"
python3 pdf/rag.py
```
