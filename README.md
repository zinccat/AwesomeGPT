# AwesomeGPT
A tool for grasping the long lists of papers in awesome- repos to make your own GPTs!

## Todo

1. Parse given awesome sites and extract arxiv links, turn into paper titles, abstracts and pdf links (crawl_awesome.py)
2. Crawl pdf files (crawl_pdf.py)
3. Parse pdf to text (parse_pdf.py)
4. Encode text to vectors and store in database (ingest.py)
5. Use RAG to retrieve relevant papers and answer questions (response.py)
6. Provide a streamlit interface to interact with the model (copy from exobrain)