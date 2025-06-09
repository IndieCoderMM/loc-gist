import os
import eel
import platform
from rag_local import initModel, initNewDB, query_rag

# Global chain
chain = None


def init_chat(db_name):
    """Initialize the RAG chain with the specified database."""
    global chain
    chain = initModel(os.path.join("chroma_db", db_name))
    if chain is None:
        return "Failed to initialize RAG chain."

    return "RAG chain initialized successfully with database: " + db_name


def get_response(question):
    """Get a response from the RAG chain for the given question."""
    global chain
    if chain is None:
        return "RAG chain is not initialized. Please initialize it first."

    response = query_rag(chain, question)
    return response


def list_dbs(folder="chroma_db"):
    """List top-level folders in the specified db folder."""
    if not os.path.isdir(folder):
        return []

    dbs = []
    for root, dirs, _ in os.walk(folder):
        for dir_name in dirs:
            db_path = os.path.join(root, dir_name)
            if os.path.isdir(db_path):
                dbs.append(dir_name)
        # Only list top-level directories
        break
    return dbs


def create_db(file_path, db_name, folder="chroma_db"):
    """Index new pdf"""
    db_path = initNewDB(file_path, db_name, folder)

    return db_path


def start_eel(develop):
    """Start Eel with either production or development configuration."""

    if develop:
        directory = 'web'
        app = 'chrome-app'
        page = 'index.html'
    else:
        directory = 'build'
        app = 'chrome-app'
        page = 'index.html'

    eel.init(directory)

    eel_kwargs = dict(
        host='localhost',
        port=8080,
        size=(1280, 800),
    )
    try:
        eel.start(page, mode=app, **eel_kwargs)
    except EnvironmentError:
        # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
        if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
            eel.start(page, mode='edge', **eel_kwargs)
        else:
            raise


if __name__ == '__main__':
    import sys

    start_eel(develop=len(sys.argv) == 2)
