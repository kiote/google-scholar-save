import csv
import asyncio
import aiohttp
from tqdm import tqdm
import os
import anthropic
from bs4 import BeautifulSoup

def extract_body_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text from body
    body = soup.body
    if body:
        text = body.get_text(separator='\n', strip=True)
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    return ""

async def extract_abstract_with_anthropic(body_text, client):
    try:
        message = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": f"""Extract the abstract from this text of a scientific article. Return only the abstract without any introductory text. If no abstract is found, return "No abstract found."

Article Text:
{body_text[:10000]}"""  # Truncating to first 10000 characters
            }]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

async def get_abstract_from_html(session, doi, client):
    url = f"https://doi.org/{doi}"
    async with session.get(url, allow_redirects=True) as response:
        if response.status == 200:
            html_content = await response.text()
            body_text = extract_body_text(html_content)
            abstract = await extract_abstract_with_anthropic(body_text, client)
            return abstract
    return None

async def process_entry(session, entry, client):
    if not entry or len(entry) < 2:  # skipping title
        return None, None, None
    doi, title = entry[0], entry[1]
    try:
        abstract = await get_abstract_from_html(session, doi, client)
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

async def harvest_abstracts(input_file, output_file, anthropic_api_key, batch_size=100):
    # Initialize output file
    write_results([], output_file, mode='w')

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        entries = list(reader)

    total_entries = len(entries)
    results_buffer = []

    client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)

    async with aiohttp.ClientSession() as session:
        with tqdm(total=total_entries, desc="Processing entries") as pbar:
            for entry in entries:
                result = await process_entry(session, entry, client)
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
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not anthropic_api_key:
        print("Please set the ANTHROPIC_API_KEY environment variable.")
    else:
        asyncio.run(harvest_abstracts(input_file, output_file, anthropic_api_key))
