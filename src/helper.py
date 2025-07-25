from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_pdf_file(data):
    loader = DirectoryLoader(data, glob="**/*.pdf",loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

def text_splitter(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    split_documents = text_splitter.split_documents(documents)
    return split_documents

def download_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings