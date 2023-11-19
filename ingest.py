# Processing pdf and insert to Pinecone
from unstructured.partition.pdf import partition_pdf
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from pprint import pprint
import pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.pinecone import Pinecone

from key import PINECONE_API_KEY, PINECONE_API_ENV, OPENAI_API_KEY, PINECONE_INDEX_NAME

def send_docs_to_pinecone(documents):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_API_ENV)

    if PINECONE_INDEX_NAME in pinecone.list_indexes():
        print(
            f"Index {PINECONE_INDEX_NAME} already exists, deleting and recreating to avoid duplicates"
        )
        pinecone.delete_index(name=PINECONE_INDEX_NAME)

    pinecone.create_index(name=PINECONE_INDEX_NAME, dimension=1536)
    Pinecone.from_documents(documents, embeddings, index_name=PINECONE_INDEX_NAME)

pdf_path = "data/motion to change venue.pdf" #input("Please enter the path to the PDF file: ")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # or any desired value
    chunk_overlap=100,  # or any desired value
    length_function=len,
    is_separator_regex=False,
)

# Extract elements from the PDF
elements = partition_pdf(pdf_path, strategy="auto")
text = "".join([str(x) for x in elements])

def split_text_into_documents(text):
    split_documents = text_splitter.create_documents([text])
    return split_documents

# Assuming elements have been extracted from the PDF using partition_pdf
split_documents = split_text_into_documents(text)


pprint(split_documents)
send_docs_to_pinecone(split_documents)