# for site like https://github.com/AmadeusChan/Awesome-LLM-System-Papers, find all arxiv links in readme.md

import requests
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


def get_readme_content(username, repo):
    url = f"https://raw.githubusercontent.com/{username}/{repo}/main/README.md"
    response = requests.get(url)
    return response.text if response.status_code == 200 else None

def extract_arxiv_links(readme_content):
    # This regex will match both abstract and PDF links
    # print(readme_content)
    arxiv_links = re.findall(r'https?://arxiv\.org/(?:abs|pdf)/[\w.-]+(?:v\d+)?', readme_content)
    # Normalize all links to abstract links
    normalized_links = [link.replace('/pdf/', '/abs/') for link in arxiv_links]
    normalized_links = list(set(normalized_links))
    return normalized_links



def fetch_paper_details(arxiv_link):
    paper_id = arxiv_link.split('/')[-1]
    if '.pdf' in paper_id:
        paper_id = paper_id.replace('.pdf', '')

    arxiv_api_url = f'http://export.arxiv.org/api/query?id_list={paper_id}'
    response = requests.get(arxiv_api_url)
    
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'lxml')
    entry = soup.find('entry')

    if entry:
        title = entry.find('title').text.strip()
        abstract = entry.find('summary').text.strip()
        # Extract the PDF link
        pdf_link = entry.find('link', {'title': 'pdf'}).get('href') if entry.find('link', {'title': 'pdf'}) else None

        return {'title': title, 'abstract': abstract, 'pdf_link': pdf_link}


def get_arxiv_papers_from_github(username, repo):
    readme_content = get_readme_content(username, repo)
    if readme_content is None:
        return "Error fetching README"
    
    arxiv_links = extract_arxiv_links(readme_content)
    papers = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Prepare future-to-url mapping
        future_to_url = {executor.submit(fetch_paper_details, url): url for url in arxiv_links}
        # Iterate over completed futures with progress bar
        for future in tqdm(concurrent.futures.as_completed(future_to_url), total=len(arxiv_links)):
            paper_details = future.result()
            if paper_details:
                papers.append(paper_details)
    return papers

if __name__ == "__main__":
    username = "AmadeusChan"
    repo = "Awesome-LLM-System-Papers"
    papers = get_arxiv_papers_from_github(username, repo)
    # List of dictionaries containing paper details
    #[{'title': title, 'abstract': abstract, 'pdf_link': pdf_link}]
    # print(papers)
    # save to json
    import json
    if not os.path.exists(f'data/paperlist/{username}'):
        os.makedirs(f'data/paperlist/{username}')
    with open(f'data/paperlist/{username}/{repo}.json', 'w') as f:
        json.dump(papers, f)