from tkinter import filedialog

from loc_gist.rag.api import chain_db, index_db
from loc_gist.rag.db_helper import get_all_dbs

class DbHandler:
    def __init__(self):
        self.chain = None
        self.active_db = None
        self.list = []
        self.settings_provider = None

    def set_settings_provider(self, provider):
        self.settings_provider = provider

    def _get_settings(self):
        try:
            if callable(self.settings_provider):
                return self.settings_provider() or {}
        except Exception:
            pass
        return {}

    def activate(self, db_name: str):
        if self.active_db == db_name:
            return False

        settings = self._get_settings()
        self.chain, status = chain_db(db_name, settings=settings)

        self.active_db = db_name
        return True

    def create_db(self):
        path = filedialog.askopenfilename()
        if not path:  # User cancelled the file dialog
            return False, "No file selected"
        if not path.endswith(".pdf"):
            return False, "Unsupported file type. Please select a PDF file."
        db_name = path.split("/")[-1].split(".")[0]
        db_path = index_db(path, db_name)
        return True, f"Indexed {db_name} at {db_path}"

    def get_chain(self):
        if self.chain is None:
            raise ValueError("No active database selected.")
        return self.chain

    def get_dbs(self):
        if not self.list:
            self.list = get_all_dbs()
        return self.list
