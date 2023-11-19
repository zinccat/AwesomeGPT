import requests
import pandas as pd
from tqdm import tqdm
import concurrent.futures

def download_file(url, filename):
    """Download file from a given URL and save it locally."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=16384):
                f.write(chunk)
    except Exception as e:
        print(f"Error downloading {url}: {e}")

def download_wrapper(paper_id, link):
    url = link.replace('forum', 'pdf')
    download_file(url, f'data/papers/{paper_id}.pdf')

df = pd.read_csv('data/paperlist_desk-rejected-withdrawn-submissions.tsv', sep='\t', index_col=0)
# skip the first 1000 papers
# df = df.iloc[1600:]
# Adjust the max_workers according to your system's capability
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_wrapper, paper_id, link) for paper_id, link in df.link.items()]
    # Use tqdm to display progress
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
        pass
