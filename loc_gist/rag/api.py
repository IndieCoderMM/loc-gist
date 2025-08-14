from loc_gist.rag.core import init_model, init_db
from .db_helper import get_db_path, create_db, is_db_exists, get_all_dbs


def chain_db(db_name, settings: dict | None = None):
    """Initialize the RAG chain with the specified database and optional settings."""
    if not is_db_exists(db_name):
        return None, "Database does not exist."

    db_path = get_db_path(db_name)

    settings = settings or {}
    chain = init_model(
        db_path,
        model=settings.get("model", "qwen3:4b"),
        temperature=settings.get("temperature", 0.0),
        ctx_window=settings.get("ctx_window", 8192),
        top_k=settings.get("top_k", 3),
        max_tokens=settings.get("max_tokens"),
    )
    if chain is None:
        return None, "Failed to initialize RAG chain."

    return chain, "RAG chain initialized"


def query_rag(chain, question):
    """Queries the RAG chain and return response."""
    response = chain.invoke(question)
    return response


def index_db(file_path, db_name):
    """Index new pdf and return the database path."""
    if is_db_exists(db_name):
        return f"Database '{db_name}' already exists."
    db_path = create_db(db_name)
    init_db(file_path, db_path)
    return db_path


def list_dbs():
    """List all available databases."""
    return get_all_dbs()
