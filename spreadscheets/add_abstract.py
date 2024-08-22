import csv
import asyncio
import aiohttp
from tqdm import tqdm
from bs4 import BeautifulSoup

def extract_abstract_text(html_content):
    print(f"Extracting abstract from HTML content...")
    print(html_content[:100])
    soup = BeautifulSoup(html_content, 'html.parser')

    # Look for the div with id="abstract"
    abstract_div = soup.find('div', id='abstracts')

    if abstract_div:
        # Extract text from the abstract div
        abstract_text = abstract_div.get_text(separator=' ', strip=True)
        print(f"Abstract extracted: {abstract_text}")
        return abstract_text
    else:
        print("No abstract div found in the HTML content")

    # If no abstract div is found, return an empty string
    return ""

async def get_abstract_from_html(session, doi):
    url = f"https://doi.org/{doi}"
    async with session.get(url, allow_redirects=True) as response:
        if response.status == 200:
            html_content = await response.text()
            abstract_text = extract_abstract_text(html_content)
            return abstract_text
    return None

async def process_entry(session, entry):
    if not entry or len(entry) < 2:  # skipping title
        return None, None, None
    doi, title = entry[0], entry[1]
    try:
        abstract = await get_abstract_from_html(session, doi)
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

    async with aiohttp.ClientSession() as session:
        with tqdm(total=total_entries, desc="Processing entries") as pbar:
            for entry in entries:
                result = await process_entry(session, entry)
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
    input_file = "/home/kiote/small_collection.csv"
    output_file = "/home/kiote/collection_abstract.csv"

    asyncio.run(harvest_abstracts(input_file, output_file))
