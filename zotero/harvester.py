import csv
import asyncio
import aiohttp
from tqdm import tqdm
import os
import anthropic

async def extract_abstract_with_anthropic(html_content, client):
    try:
        message = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""You are an AI assistant tasked with extracting the abstract from an HTML page of a scientific article.
    The HTML content of the page is provided below. Please analyze the content and return only the abstract of the article. Don't include into "Here is the abstract:" or similar text.
    If you can't find an abstract, return "No abstract found."

    HTML Content:
    {html_content[:10000]}"""  # Truncating to first 10000 characters to avoid token limits
                        }
                    ]
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

async def get_abstract_from_html(session, doi, semaphore, client):
    url = f"https://doi.org/{doi}"
    async with semaphore:
        await asyncio.sleep(0.5)  # Wait for 0.5 seconds before making the request
        async with session.get(url, allow_redirects=True) as response:
            if response.status == 200:
                html_content = await response.text()
                abstract = await extract_abstract_with_anthropic(html_content, client)
                return abstract
    return None

async def process_entry(session, entry, semaphore, client):
    if not entry or len(entry) < 2:  # skipping title
        return None, None, None
    doi, title = entry[0], entry[1]
    try:
        abstract = await get_abstract_from_html(session, doi, semaphore, client)
        if abstract:
            print(f"\nAbstract for DOI {doi}:")
            print(f"{abstract[:500]}...") if len(abstract) > 500 else print(abstract)
            print("-" * 80)  # Separator line
        else:
            print(f"\nNo abstract found for DOI {doi}")
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
    semaphore = asyncio.Semaphore(10)  # Limit concurrent requests to 10

    client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)

    async with aiohttp.ClientSession() as session:
        tasks = [process_entry(session, entry, semaphore, client) for entry in entries]
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
    input_file = "/home/kiote/small_collection.csv"
    output_file = "/home/kiote/collection_abstract.csv"
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not anthropic_api_key:
        print("Please set the ANTHROPIC_API_KEY environment variable.")
    else:
        asyncio.run(harvest_abstracts(input_file, output_file, anthropic_api_key))
