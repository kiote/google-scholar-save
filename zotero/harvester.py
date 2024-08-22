# adds abstracts to DOI>Title TSV file
import csv
import requests
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def get_abstract_crossref(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['message'].get('abstract')
    return None

def get_abstract_unpaywall(doi):
    email = "your_email@example.com"  # Replace with your email
    url = f"https://api.unpaywall.org/v2/{doi}?email={email}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('abstract')
    return None

def get_abstract_sciencedirect(doi):
    url = f"https://www.sciencedirect.com/science/article/pii/{doi}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        abstract = soup.find('div', class_='abstract')
        if abstract:
            return abstract.text.strip()
    return None

def get_abstract(doi):
    abstract = get_abstract_crossref(doi) or get_abstract_unpaywall(doi) or get_abstract_sciencedirect(doi)
    return abstract

def process_entry(entry):
    doi, title = entry
    try:
        abstract = get_abstract(doi)
        return doi, title, abstract
    except Exception as e:
        print(f"Error processing DOI {doi}: {str(e)}")
        return doi, title, None

def harvest_abstracts(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        entries = list(reader)  # Read all entries into memory

    total_entries = len(entries)
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_entry, entry): entry for entry in entries}

        with tqdm(total=total_entries, desc="Processing entries") as pbar:
            for future in as_completed(futures):
                entry = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error processing entry {entry}: {str(e)}")
                finally:
                    pbar.update(1)
                    pbar.set_postfix({"Completed": f"{pbar.n}/{total_entries}"})

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['DOI', 'Title', 'Abstract'])
        writer.writerows(results)

if __name__ == "__main__":
    input_file = "/home/kiote/collection.csv"
    output_file = "/home/kiote/collection_abstract.csv"
    harvest_abstracts(input_file, output_file)
