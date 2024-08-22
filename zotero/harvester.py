# adds abstracts to DOI>Title TSV file
import csv
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import os

async def get_abstract_crossref(session, doi, semaphore):
    url = f"https://api.crossref.org/works/{doi}"
    async with semaphore:
        await asyncio.sleep(0.5)  # Wait for 0.5 seconds before making the request
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data['message'].get('abstract')
    return None

async def process_entry(session, entry, semaphore):
    if not entry or len(entry) < 2:
        print(f"Skipping invalid entry: {entry}")
        return None, None, None

    doi, title = entry[0], entry[1]
    try:
        abstract = await get_abstract_crossref(session, doi, semaphore)
        return doi, title, abstract
    except Exception as e:
        print(f"Error processing DOI {doi}: {str(e)}")
        return doi, title, None

def write_results(results, output_file, mode='a'):
    with open(output_file, mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        if mode == 'w':
            writer.writerow(['DOI', 'Title', 'Abstract'])
        writer.writerows(results)

async def harvest_abstracts(input_file, output_file, batch_size=100):
    # Initialize output file
    write_results([], output_file, mode='w')

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        entries = list(reader)

    total_entries = len(entries)
    results_buffer = []

    semaphore = asyncio.Semaphore(10)  # Limit concurrent requests to 10

    async with aiohttp.ClientSession() as session:
        tasks = [process_entry(session, entry, semaphore) for entry in entries]

        with tqdm(total=total_entries, desc="Processing entries") as pbar:
            for task in asyncio.as_completed(tasks):
                result = await task
                if result[0] is not None:  # Only add valid results to the buffer
                    results_buffer.append(result)

                # Write results to file when buffer reaches batch_size
                if len(results_buffer) >= batch_size:
                    write_results(results_buffer, output_file)
                    results_buffer = []

                pbar.update(1)
                pbar.set_postfix({"Completed": f"{pbar.n}/{total_entries}"})

    # Write any remaining results
    if results_buffer:
        write_results(results_buffer, output_file)

if __name__ == "__main__":
    input_file = "/home/kiote/collection.csv"
    output_file = "/home/kiote/collection_abstract.csv"
    asyncio.run(harvest_abstracts(input_file, output_file))

