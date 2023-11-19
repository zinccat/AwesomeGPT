# main pipeline

# Path: main.py

import os
import json
from parse_awesome import get_arxiv_papers_from_github
from crawl_pdf import download_list
from parse_pdf import process_pdfs

username = "AmadeusChan"
repo = "Awesome-LLM-System-Papers"

# load paper list
if not os.path.exists(f'data/paperlist/{username}'):
    # List of dictionaries containing paper details
    #[{'title': title, 'abstract': abstract, 'pdf_link': pdf_link}]
    papers = get_arxiv_papers_from_github(username, repo)
    with open(f'data/paperlist/{username}/{repo}.json', 'w') as f:
        json.dump(papers, f)
else:
    print("paper list already exists")
    with open(f'data/paperlist/{username}/{repo}.json', 'r') as f:
        papers = json.load(f)

# download pdf files
if not os.path.exists(f'data/pdf/{username}/{repo}'):
    # crawl pdf files
    download_list(username, repo, papers)
else:
    print("pdf files already exists")

# parse pdf files
# walk through all pdf files
papers_text = {}
if not os.path.exists(f'data/txt/{username}/{repo}'):
    os.makedirs(f'data/txt/{username}/{repo}')
    papers_text = process_pdfs(username, repo)
else:
    print("txt files already exists")
    for root, dirs, files in os.walk(f'data/txt/{username}/{repo}'):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), 'r') as f:
                    papers_text[file] = f.read()

# send to pinecone
