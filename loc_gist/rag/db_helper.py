from pathlib import Path

DB_DIR = ".chroma_db"


def get_db_path(db_name: str) -> str:
    base_path = Path(__file__).resolve().parent.parent  # root of project
    store_path = base_path / DB_DIR / db_name

    return str(store_path)


def is_db_exists(db_name: str) -> bool:
    """Check if the database exists."""
    db_path = get_db_path(db_name)
    return Path(db_path).exists()


def create_db(db_name: str) -> str:
    """Create a new database folder."""
    db_path = Path(__file__).resolve().parent.parent / DB_DIR / \
        db_name.strip().lower().replace(" ", "_")
    if not db_path.exists():
        db_path.mkdir(parents=True, exist_ok=True)
        print(f"Database '{db_name}' created successfully.")
    return str(db_path)


def get_all_dbs() -> list:
    """List top-level folders in the specified db folder."""
    base_path = Path(__file__).resolve().parent.parent  # root of project
    db_folder = base_path / DB_DIR

    if not db_folder.is_dir():
        return []

    dbs = [d.name for d in db_folder.iterdir() if d.is_dir()]
    return dbs
