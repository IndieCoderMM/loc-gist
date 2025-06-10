from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings


def get_embedding(model_name="nomic-embed-text"):
    """Initializes the Ollama embedding function."""
    # Ensure Ollama server is running (ollama serve)
    embeddings = OllamaEmbeddings(model=model_name)
    print(f"Initialized Ollama embeddings with model: {model_name}")
    return embeddings


def get_vector_store(embedding, dir):
    """Initializes or loads the Chroma vector store."""
    vectorstore = Chroma(
        persist_directory=dir,
        embedding_function=embedding
    )
    print(f"Vector store initialized/loaded from: {dir}")
    return vectorstore


def index_docs(chunks, embedding, dir):
    """Indexes document chunks into the Chroma vector store."""
    print(f"Indexing {len(chunks)} chunks...")
    # Use from_documents for initial creation.
    # This will overwrite existing data if the directory exists
    # but isn't a valid Chroma DB.
    # For incremental updates, initialize Chroma first
    # and use vectorstore.add_documents().
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=dir
    )
    vectorstore.persist()  # Ensure data is saved
    print(f"Indexing complete. Data saved to: {dir}")
    return vectorstore


def add_docs(chunks, embedding, dir):
    """Adds new document chunks to an existing Chroma vector store."""
    print(f"Adding {len(chunks)} new chunks to the vector store...")
    vectorstore = Chroma(
        persist_directory=dir,
        embedding_function=embedding
    )

    vectorstore.add_documents(chunks)
    vectorstore.persist()  # Ensure data is saved
    print("New chunks added persisted.")
    return vectorstore
