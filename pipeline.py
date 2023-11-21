# main pipeline

# Path: main.py

import os
import json
from parse_awesome import get_arxiv_papers_from_github
from crawl_pdf import download_list
from parse_pdf import process_pdfs

def process(username, repo, output_json=True):
    # if file exists, skip
    if output_json and os.path.exists(f'data/parsed/{username}/{repo}.json'):
        print("parsed file already exists")
        with open(f'data/parsed/{username}/{repo}.json', 'r') as f:
            papers_text = json.load(f)
        return papers_text
    elif not output_json and os.path.exists(f'data/parsed/{username}/{repo}.csv'):
        print("parsed file already exists")
        with open(f'data/parsed/{username}/{repo}.csv', 'r') as f:
            papers_text = {}
            for line in f.readlines():
                title, abstract = line.split('\t')
                papers_text[title] = abstract
        return papers_text
    
    # load paper list
    if not os.path.exists(f'data/paperlist/{username}'):
        os.makedirs(f'data/paperlist/{username}')
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
        os.makedirs(f'data/pdf/{username}/{repo}')
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
                        papers_text[file[:-4]] = f.read()

    output_path = f'data/parsed/{username}'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if output_json:
        with open(f'{output_path}/{repo}.json', 'w') as f:
            json.dump(papers_text, f)
    else:
        with open(f'{output_path}/{repo}.txt', 'w') as f:
            for paper in papers_text:
                f.write(f"{paper}\t{papers_text[paper]}\n")
    return papers_text

if __name__ == '__main__':
    username = "AmadeusChan"
    repo = "Awesome-LLM-System-Papers"
    process(username, repo)