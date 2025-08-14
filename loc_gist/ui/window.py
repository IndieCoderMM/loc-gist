import threading
import tkinter as tk
import ttkbootstrap as ttk

from loc_gist.rag.api import query_rag
from .db_handler import DbHandler
from .layout import Layout

class Window(ttk.Window):
    def __init__(self, theme="cyborg"):
        super().__init__(themename=theme)
        self.title("LocGist - RAG System")
        self.geometry("800x620")
        self.db_handler = DbHandler()
        self.layout = Layout(self)
        # settings dict for app variables
        self.settings = {"model": "qwen3:4b", "temperature": 0.2, "top_k": 4, "max_tokens": 1024, "ctx_window": 8192}
        # allow DbHandler to fetch settings on activation
        self.db_handler.set_settings_provider(lambda: self.settings)

    def apply_settings(self, payload: dict):
        # Save and apply to downstream components if needed
        self.settings.update(payload or {})
        self.write_log(f"[SYS]: Settings updated: {self.settings}")
        # Reinitialize chain with new settings if a DB is active
        if self.db_handler.active_db:
            self.write_log("[SYS]: Reinitializing model with new settings…")
            # Trigger re-activation to rebuild chain
            self.db_handler.activate(self.db_handler.active_db)

    def run(self):
        self.layout.pack(expand=True, fill=tk.BOTH)
        self.mainloop()

    def write_log(self, msg):
        self.layout.tab_window.log_tab.write(msg)

    def write_chat(self, msg):
        # Route to bot-styled renderer by default (user messages are written by ChatBox itself)
        self.layout.tab_window.chat_tab.write_bot(msg)

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
        # show UI processing signals
        self.layout.tab_window.chat_tab.start_thinking()
        self.update_status(status="THINKING", db_name=self.db_handler.active_db or "NONE")

        def safe_write_chat(text):
            self.after(0, lambda: self.write_chat(text))

        def safe_write_log(text):
            self.after(0, lambda: self.write_log(text))

        def safe_stop_thinking():
            self.after(0, self.layout.tab_window.chat_tab.stop_thinking)

        def safe_set_ok():
            self.after(0, lambda: self.update_status("OK", self.db_handler.active_db or "NONE"))

        def safe_set_error():
            self.after(0, lambda: self.update_status("ERROR", self.db_handler.active_db or "NONE"))

        threading.Thread(
            target=self._run_query_and_append,
            args=(self.db_handler.chain, msg, safe_write_log, safe_write_chat, safe_stop_thinking, safe_set_ok, safe_set_error),
            daemon=True,
        ).start()

    @staticmethod
    def _run_query_and_append(chain, msg, write_log, write_chat, stop_thinking, set_ok, set_error):
        """Run the query in a separate thread and append the response."""
        try:
            response = query_rag(chain, msg)
            # Extract thoughts which are between <think></think>
            if "<think>" in response and "</think>" in response:
                thoughts = response.split("<think>")[1].split("</think>")[0]
                response = response.replace(f"<think>{thoughts}</think>", "").strip()
                write_log(f"Thoughts: {thoughts}")

            write_chat(response)
            set_ok()
        except Exception as e:
            write_log(f"[ERROR]: {e}")
            set_error()
        finally:
            stop_thinking()
