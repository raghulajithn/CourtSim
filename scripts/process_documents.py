from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

def process_document(filename, text, persist_directory):
    documents = [Document(page_content=text, metadata={"source": filename})]
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    chunks = splitter.split_documents(documents)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07")

    collection_name = f"{filename}"
    store_documents_in_chroma(chunks, embeddings, collection_name, persist_directory)

    return chunks

def store_documents_in_chroma(doc_objects, embeddings, collection_name, persist_directory):
    chroma_db = Chroma.from_documents(
        doc_objects,
        embeddings,
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
    chroma_db.persist()  
    print(f"Documents stored in ChromaDB under collection {collection_name}.")


def get_retriever_from_chroma(user_msg, collection_name, persist_directory, search_type="similarity", k=3, fetch_k=10):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07")
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )

    retriever = vector_store.as_retriever(
        search_type=search_type, search_kwargs={"k": k, "fetch_k": fetch_k, "filter": {"source": "filename"}}
    )
    retriever.get_relevant_documents(query = user_msg, filter={"source": "filename"})
    return " ".join(doc["document"] for doc in retriever["documents"][0])
