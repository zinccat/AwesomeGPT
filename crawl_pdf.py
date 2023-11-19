import requests
from tqdm import tqdm
import concurrent.futures
import os

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

def download_wrapper(user, reponame, title, url):
    # print(url)
    download_file(url, f'data/pdf/{user}/{reponame}/{title}.pdf')

def download_list(user, reponame, paper_list):
    if not os.path.exists(f'data/pdf/{user}'):
        os.makedirs(f'data/pdf/{user}/{reponame}')
    # Adjust the max_workers according to your system's capability
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download_wrapper, user, reponame, paper["title"], paper["pdf_link"]) for paper in paper_list]
        # Use tqdm to display progress
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            pass
