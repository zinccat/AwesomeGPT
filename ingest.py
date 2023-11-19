# Processing pdf and insert to Pinecone
from unstructured.partition.pdf import partition_pdf
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from pprint import pprint
import pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.pinecone import Pinecone

from key import PINECONE_API_KEY, PINECONE_API_ENV, OPENAI_API_KEY

def init_pinecone(index_name):
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(name=index_name, dimension=1536, metric='cosine')
    index = pinecone.Index(index_name)
    return index

def send_docs_to_pinecone(index, documents):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    print(embeddings.client)
    print("Sending documents to Pinecone...")
    zipped = zip(documents, embeddings)
    index.upsert(zipped)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # or any desired value
    chunk_overlap=200,  # or any desired value
    length_function=len,
    is_separator_regex=False,
)


def split_text_into_documents(text):
    split_documents = text_splitter.create_documents([text])
    return split_documents

def ingest_text(text):
    index = init_pinecone('awesome')
    split_documents = split_text_into_documents(text)
    send_docs_to_pinecone(index, split_documents)

if __name__ == "__main__":
    with open('data/txt/AmadeusChan/Awesome-LLM-System-Papers/Skeleton-of-Thought: Large Language Models Can Do Parallel Decoding.txt', 'r') as f:
        text = f.read()
    ingest_text(text)