from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
import os
# For retrieving the parent chunks
from langchain.retrievers import ParentDocumentRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.storage._lc_store import create_kv_docstore
from langchain.storage import LocalFileStore

current_locations = Path(__file__).parent
env_path = current_locations.parent/"config"/"keys.env" # Need to use string
# The models
from config.keys import (
    openai_key,
)

# Openai embedding model
embedding_openai = OpenAIEmbeddings(
    model="text-embedding-3-large",#"text-embedding-3-small", #The new one is costlier (6x), but it is better
    api_key=openai_key
)

def create_vectorstore(chunks, embedding_model=embedding_openai):
    """This funtions returns the vectorstore"""
    current_locations = Path(__file__).parent
    persist_dir = os.path.join(current_locations.parent/"media"/"process_pdfs", "chroma_db")
    print(persist_dir)
    
    vectorstore = Chroma.from_documents(
    documents=chunks, 
    embedding=embedding_model,
    persist_directory=persist_dir)
    return vectorstore
def load_vector(embedding_model=embedding_openai):
    current_locations = Path(__file__).parent
    persist_dir = os.path.join(current_locations.parent/"media"/"process_pdfs", "chroma_db")

    load_vector = Chroma(
    persist_directory=persist_dir, 
    embedding_function=embedding_model)
    return load_vector
   
    # Load the vector database created above
from langchain.storage._lc_store import create_kv_docstore

# Create the vector store and add document
is_create_user_db = False
def create_user_db(thread_id, collection_name="parent_main", embedding_model=embedding_openai, chunk_size=50, chunk_overlap=20):
    """This function returns the persist_directory where the main user database is saved"""
    persist_directory = current_locations.parent / "media" / "process_pdfs" / thread_id / "chroma_db" / "parent_db"
    # persist_directory = "./"+thread_id
    collection_name = collection_name + thread_id
    parent_chunk_size = chunk_size * 8
    
    
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=parent_chunk_size, chunk_overlap=chunk_overlap)
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # We just have Chroma, this function will only load the vector database
    # We will add text later using the add_documents method.
    vectorstore_context = Chroma(
            collection_name=collection_name, 
            embedding_function=embedding_model,
            persist_directory=persist_directory
        )
    localStorage = LocalFileStore(persist_directory)
    #store = InMemoryStore()
    store = create_kv_docstore(localStorage)


    retriever_main = ParentDocumentRetriever(
            vectorstore=vectorstore_context,
            docstore=store,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
            search_type="similarity_score_threshold",
            search_kwargs={"score_threshold": 0.05}
            # search_kwargs={"k": k_vectors}
        
        )
    
    return retriever_main, persist_directory
def add_docs_parents(retriever_main, thread_id, docs=None):
    """retriever_main is the ParentDocumentRetriever object
    docs: Document object from langchain
    if the persist_directory.exists() is True: it means that we already add the docs to the user vector database"""
    assert docs != None, "docs must be provided"

    persist_directory = current_locations.parent / "media" / "process_pdfs" / thread_id / "chroma_db" / "parent_db" / "parent_retriever_flag"
    if persist_directory.exists():
        print(f"Document is already added!")
    else:
        if not persist_directory.exists():
            persist_directory.mkdir()
            retriever_main.add_documents(documents=docs)
            print(f"Add {len(docs)} to user: {thread_id} vector database")

# Save the chat history without using parent splitter because the queries and resopnes are not too long
def create_user_history_db(thread_id: str, chat_history: str="chat_history", embedding_model=embedding_openai):
    """Inputs:
    Args:
    chat_history: str - which is the name of the chat history vector database
    it will comebine with the thread_id (in this case: visitor_id)"""
    chat_history = chat_history + thread_id
    
    persist_directory = current_locations.parent / "media" / "process_pdfs" / thread_id / "chroma_db" / "history_db"
    
    vectorstore_history = Chroma(
            collection_name=chat_history, 
            embedding_function=embedding_model,
            persist_directory=persist_directory
        )
    # # This function takes the vector store object as an argument.
    # retriever_history = vectorstore_history.as_retriever(search_kwargs={"k":3})
    
    retriever_with_threshold = vectorstore_history.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.01}
    )
    return vectorstore_history, retriever_with_threshold, chat_history, persist_directory    
    
    
    
    
    
    