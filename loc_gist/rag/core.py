import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from .pdf_reader import load_documents, split_documents
from .embedding import get_embedding, get_vector_store, index_docs


def init_model(db_path, model="qwen3:4b"):
    embedding_function = get_embedding()

    if not os.path.exists(db_path):
        return None
    else:
        print("Loading existing DB...")
        vector_store = get_vector_store(embedding_function, db_path)

    rag_chain = init_chain(vector_store, model)

    return rag_chain


def init_chain(vector_store, model="qwen3:4b", ctx_window=4096):
    """Creates the RAG chain."""
    # Initialize the LLM
    llm = ChatOllama(
        model=model,
        temperature=0,  # Lower temperature for more factual RAG answers
        num_ctx=ctx_window  # IMPORTANT: Set context window size
    )
    print(
        f"Initialized ChatOllama: {model}, context window: {ctx_window}")

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


def init_db(file_path, db_path):
    """Create a new vector store and index documents."""
    docs = load_documents(file_path)
    chunks = split_documents(docs)

    print("Attempting to index documents...")
    embedding = get_embedding()
    index_docs(chunks, embedding, db_path)
