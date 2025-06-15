import threading
import tkinter as tk
import ttkbootstrap as ttk

from loc_gist.rag.api import query_rag
from .db_handler import DbHandler
from .layout import Layout

class Window(ttk.Window):
    def __init__(self, theme="journal"):
        super().__init__(themename=theme)
        self.title("Local RAG System")
        self.geometry("800x620")
        self.db_handler = DbHandler()
        self.layout = Layout(self)

    def run(self):
        self.layout.pack(expand=True, fill=tk.BOTH)
        self.mainloop()

    def write_log(self, msg):
        self.layout.tab_window.log_tab.write(msg)

    def write_chat(self, msg):
        self.layout.tab_window.chat_tab.write(msg)

    def update_status(self, status, db_name):
        self.layout.status_bar.update(status, db_name)

    def create_db(self):
        """Create a new database by opening a file dialog."""
        ok, status = self.db_handler.create_db()
        if ok:
            self.write_log(status)
            self.update_status(status="OK", db_name=status)
        else:
            self.write_log(status)

    def handle_input(self, msg):
        """Handle user input from the chat box."""
        if self.db_handler.chain is None:
            self.write_chat("Please select a database first.")
            return
        self.write_log("Processing your query...")

        def safe_write_chat(text):
            self.after(0, lambda: self.write_chat(text))

        def safe_write_log(text):
            self.after(0, lambda: self.write_log(text))

        threading.Thread(
            target=self._run_query_and_append,
            args=(self.db_handler.chain, msg, safe_write_log, safe_write_chat)
        ).start()

    @staticmethod
    def _run_query_and_append(chain, msg, write_log, write_chat):
        """Run the query in a separate thread and append the response."""
        response = query_rag(chain, msg)
        # Extract thoughts which are between <think></think>

        if "<think>" in response and "</think>" in response:
            thoughts = response.split("<think>")[1].split("</think>")[0]
            response = response.replace(f"<think>{thoughts}</think>", "").strip()
            write_log(f"Thoughts: {thoughts}")

        write_chat(response)
