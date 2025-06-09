import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()  # Optional: Loads environment variables from.env file

CHROMA_PATH = "chroma_db"  # Directory to store ChromaDB data
DATA_PATH = "data/"
PDF_FILENAME = "ielts-essays.pdf"  # Replace with your PDF filename


def load_documents(pdf_path):
    """Loads documents from the specified data path."""
    loader = PyPDFLoader(pdf_path)
    # loader = UnstructuredPDFLoader(pdf_path) # Alternative
    documents = loader.load()
    print(f"Loaded {len(documents)} page(s) from {pdf_path}")
    return documents


def split_documents(documents):
    """Splits documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    all_splits = text_splitter.split_documents(documents)
    print(f"Split into {len(all_splits)} chunks")
    return all_splits


def get_embedding_function(model_name="nomic-embed-text"):
    """Initializes the Ollama embedding function."""
    # Ensure Ollama server is running (ollama serve)
    embeddings = OllamaEmbeddings(model=model_name)
    print(f"Initialized Ollama embeddings with model: {model_name}")
    return embeddings


def get_vector_store(embedding_function, persist_directory=CHROMA_PATH):
    """Initializes or loads the Chroma vector store."""
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding_function
    )
    print(f"Vector store initialized/loaded from: {persist_directory}")
    return vectorstore


def index_documents(chunks, embedding_function, persist_directory=CHROMA_PATH):
    """Indexes document chunks into the Chroma vector store."""
    print(f"Indexing {len(chunks)} chunks...")
    # Use from_documents for initial creation.
    # This will overwrite existing data if the directory exists
    # but isn't a valid Chroma DB.
    # For incremental updates, initialize Chroma first
    # and use vectorstore.add_documents().
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=persist_directory
    )
    vectorstore.persist()  # Ensure data is saved
    print(f"Indexing complete. Data saved to: {persist_directory}")
    return vectorstore


def create_rag_chain(vector_store, model="qwen3:4b", ctx_window=4096):
    """Creates the RAG chain."""
    # Initialize the LLM
    llm = ChatOllama(
        model=model,
        temperature=0,  # Lower temperature for more factual RAG answers
        num_ctx=ctx_window  # IMPORTANT: Set context window size
    )
    print(
        f"Initialized ChatOllama with model: {model}, context window: {ctx_window}")

    # Create the retriever
    retriever = vector_store.as_retriever(
        search_type="similarity",  # Or "mmr"
        search_kwargs={'k': 3}  # Retrieve top 3 relevant chunks
    )
    print("Retriever initialized.")

    # Define the prompt template
    template = """Answer the question based ONLY on the following context:
{context}

Question: {question}
Note: Do not make up any information. Small talk is allowed.'
"""
    prompt = ChatPromptTemplate.from_template(template)
    print("Prompt template created.")

    # Define the RAG chain using LCEL
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    print("RAG chain created.")
    return rag_chain


def query_rag(chain, question):
    """Queries the RAG chain and prints the response."""
    print("\nQuerying RAG chain...")
    print(f"Question: {question}")
    response = chain.invoke(question)
    print("\nResponse:")
    print(response)
    return response


def initNewDB(file_path, db_name, folder="chroma_db"):
    """Create a new database folder."""
    db_path = os.path.join(folder, db_name.strip().lower().replace(" ", "_"))
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        print(f"Database '{db_name}' created successfully.")
        docs = load_documents(file_path)

        # 2. Split Documents
        chunks = split_documents(docs)

        print("Attempting to index documents...")
        embedding_function = get_embedding_function()
        index_documents(chunks, embedding_function, db_path)
    else:
        print(f"Database '{db_name}' already exists.")

    return db_path


def initModel(db_path=CHROMA_PATH, model="qwen3:4b"):
    # 3. Get Embedding Function
    embedding_function = get_embedding_function()

    # 4. Index Documents (Only needs to be done once per document set)
    # TODO: Check if DB exists before reindexing
    if not os.path.exists(db_path):
        return None
        # 1. Load Documents
    else:
        print("Loading existing DB...")
        vector_store = get_vector_store(embedding_function, db_path)

    # 5. Create RAG Chain
    rag_chain = create_rag_chain(vector_store, model)

    # 6. Query
    # query_question = "What is the main topic of the document?"
    # query_rag(rag_chain, query_question)

    return rag_chain
