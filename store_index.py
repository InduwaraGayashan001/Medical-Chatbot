from src.helper import load_pdf_file, text_splitter, download_embeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

extracted_data = load_pdf_file(data='Data/')
print("Extracted data from PDF files.")

text_chunks = text_splitter(extracted_data)
print("Text chunks created from the extracted data.")

embeddings = download_embeddings()
print("Embeddings downloaded.")

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "medibot"

pc.create_index(
    name=index_name,
    dimension=384,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)
print(f"Index '{index_name}' created in Pinecone.")

docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings
)
print("Documents indexed in Pinecone.")