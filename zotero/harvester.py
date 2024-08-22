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
            messages=[{
                "role": "user",
                "content": f"""Extract the abstract from this HTML of a scientific article. Return only the abstract without any introductory text. If no abstract is found, return "No abstract found."

HTML Content:
{html_content[:10000]}"""  # Truncating to first 10000 characters
            }]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

async def get_abstract(session, doi, client):
    url = f"https://doi.org/{doi}"
    async with session.get(url, allow_redirects=True) as response:
        if response.status == 200:
            html_content = await response.text()
            return await extract_abstract_with_anthropic(html_content, client)
    return None

async def process_entries(entries, client):
    async with aiohttp.ClientSession() as session:
        tasks = [get_abstract(session, entry[0], client) for entry in entries if len(entry) >= 2]
        abstracts = await asyncio.gather(*tasks)
        return [(entry[0], entry[1], abstract) for entry, abstract in zip(entries, abstracts) if abstract]

async def harvest_abstracts(input_file, output_file, anthropic_api_key):
    with open(input_file, 'r', encoding='utf-8') as f:
        entries = list(csv.reader(f, delimiter='\t'))

    client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
    results = await process_entries(entries[1:], client)  # Skip header row

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['DOI', 'Title', 'Abstract'])
        writer.writerows(results)

    print(f"Processed {len(results)} entries. Results saved to {output_file}")

if __name__ == "__main__":
    input_file = "/home/kiote/small_collection.csv"
    output_file = "/home/kiote/collection_abstract.csv"
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not anthropic_api_key:
        print("Please set the ANTHROPIC_API_KEY environment variable.")
    else:
        asyncio.run(harvest_abstracts(input_file, output_file, anthropic_api_key))
