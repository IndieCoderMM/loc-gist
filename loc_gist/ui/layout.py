import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .window import Window

class Layout(ttk.Frame):
    def __init__(self, window: "Window"):
        super().__init__(window, padding=10)
        self.parent = window
        self.pack(expand=True, fill=tk.BOTH)
        self.sidebar = Sidebar(parent=self, title="Knowledge Bases", window=window)
        main = ttk.Frame(self)
        main.pack(expand=True, fill=tk.BOTH)
        main.grid_rowconfigure(0, weight=2)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self.tab_window = TabWindow(parent=main, window=window, bootstyle="secondary")
        self.tab_window.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.status_bar = StatusBar(parent=main)
        self.status_bar.pack(expand=True, fill=tk.X, padx=10, pady=4)

class TabWindow(ttk.Notebook):
    def __init__(self, window: "Window", parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.window = window
        # Create the frames for each tab
        self.chat_tab = ChatBox(parent=self, window=window)
        self.log_tab = LogBox(parent=self)
        self.project_tab = ttk.Frame(self)

        # Add tabs to the notebook
        self.add(self.chat_tab, text="Smart Search")
        self.add(self.log_tab, text="System Logs")
        self.add(self.project_tab, text="Project Details")

        # Optional: populate with placeholders
        self._populate_tabs()

    def _populate_tabs(self):
        ttk.Label(self.project_tab, text="Project view").pack(padx=10, pady=10)

class StatusBar(ttk.Labelframe):
    def __init__(self, parent=None):
        super().__init__(parent, text="Status")
        self.parent = parent
        self.update("IDLE", "NONE")

    def update(self, status, db_name):
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text=f"{status}").pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Label(self, text=f"[DB]: {db_name}").pack(side=tk.RIGHT, padx=10, pady=5)

class LogBox(ttk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_box = ScrolledText(self, wrap=tk.WORD, font=("Courier Mono", 10), state=tk.DISABLED)
        self.text_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def write(self, msg):
        """Append message to log box."""
        self.text_box.text.config(state=tk.NORMAL)
        self.text_box.text.insert(tk.END, f"\n{msg}")
        self.text_box.text.see(tk.END)
        self.text_box.text.config(state=tk.DISABLED)

class ChatBox(ttk.Frame):
    def __init__(self, window: "Window", parent=None):
        super().__init__(parent)
        self.window = window

        self.search_bar = ttk.Frame(self)
        self.search_bar.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10)
        self.search_bar.grid_rowconfigure(0, weight=1)
        self.search_bar.grid_columnconfigure(0, weight=1)

        self.text_box = ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED)
        self.text_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.text_box.text.tag_configure("user", foreground="blue")
        self.text_box.text.tag_configure("bot", foreground="green")

        self.input = ttk.Entry(self.search_bar, bootstyle="primary")
        self.input.pack(expand=True, fill=tk.X, side=tk.LEFT)
        self.input.bind("<Return>", self.handle_input)

        self.button = ttk.Button(self.search_bar, text="Send", command=lambda: self.handle_input(None), bootstyle="primary")
        self.button.pack(padx=10, pady=5, side=tk.LEFT)


    def handle_input(self, event):
        msg = self.input.get().strip()
        if msg:
            self.write(msg)
            self.input.delete(0, tk.END)
            self.window.handle_input(msg)

    def write(self, msg, tag="user"):
        """Append message to chat box."""
        self.text_box.text.config(state=tk.NORMAL)
        self.text_box.text.insert(tk.END, f"\n{msg}", (tag,))
        self.text_box.text.see(tk.END)
        self.text_box.text.config(state=tk.DISABLED)


class Sidebar(ttk.Labelframe):
    def __init__(self, title: str, parent:Layout, window: "Window"):
        super().__init__(parent, width=250, text=title)
        self.window = window
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.create_widgets()
        self.refresh_db_list()

    def create_widgets(self):
        self.db_group = ttk.Frame(self, bootstyle="light")
        self.db_group.pack(fill=tk.X, padx=10, pady=10)
        refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh_db_list)
        refresh_btn.pack(fill=tk.X, padx=10, pady=5)

        open_file_btn = ttk.Button(self, text="Open File", command=self.window.create_db)
        open_file_btn.pack(fill=tk.X, padx=10, pady=5)

    def refresh_db_list(self):
        dbs = self.window.db_handler.get_dbs()
        for widget in self.db_group.winfo_children():
            widget.destroy()
        for db in dbs:
            btn = ttk.Button(self.db_group, text=db, 
                             command=lambda db=db:self.on_db_select(db), 
                             bootstyle="primary" if db == self.window.db_handler.active_db else "primary-link")
            btn.pack(fill=tk.X, padx=10, pady=4)

    def on_db_select(self, db_name):
        if not self.window.db_handler.activate(db_name):
            self.window.write_log(f"\n[SYS]: Database '{db_name}' already selected.\n")
            return

        self.window.write_log(f"[SYS]: Connected to database '{db_name}'.")
        self.window.update_status(status="OK", db_name=db_name)
        self.refresh_db_list()
