import tkinter as tk
import ttkbootstrap as ttk
from tkinter import scrolledtext

from loc_gist.rag.api import list_dbs
from .handlers import send_message, open_file, select_db


class Window:
    def __init__(self):
        self.root = ttk.Window(themename="cyborg")
        self.sidebar = None
        self.tree_view = None
        self.chat_box = None
        self.input_entry = None
        self.chain = None
        self.active_db = None
        self.status_bar = None
        self.build_ui()

    def run(self):
        self.refresh_db_list()
        self.root.mainloop()

    def build_ui(self):
        self.root.title("Local RAG System")
        self.root.geometry("800x600")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = ttk.Frame(self.root, width=250, bootstyle="dark",)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        self.sidebar.grid_propagate(False)

        # Main Area
        main = ttk.Frame(self.root)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self.status_bar = ttk.Frame(main, bootstyle="dark")
        self.status_bar.grid(row=0, column=0, sticky="new", padx=10, pady=10)

        ttk.Label(self.status_bar, text="[STATUS]: IDLE").grid(
            row=0, column=0, sticky="w", padx=10, pady=5)

        # Chat Box
        self.chat_box = scrolledtext.ScrolledText(main, wrap=tk.WORD, font=("Courier Mono", 10))
        self.chat_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Bottom Input
        bottom = ttk.Frame(main)
        bottom.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        bottom.grid_columnconfigure(0, weight=1)

        self.input_entry = ttk.Entry(bottom, bootstyle="info")
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ttk.Button(bottom, text="Send", command=self.on_send,
                   bootstyle="success").grid(
            row=0, column=1, padx=5)

    def refresh_db_list(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        refresh_btn = ttk.Button(self.sidebar, text="Refresh",
                                 command=self.refresh_db_list,
                                 bootstyle="primary-outline").pack(fill=tk.X, padx=10, pady=5)

        # Populate the sidebar with database buttons
        self.sidebar.pack_propagate(False)

        self.tree_view = ttk.Treeview(
            self.sidebar, show="tree", bootstyle="dark")
        self.tree_view.pack(fill=tk.BOTH, expand=True)
        self.tree_view.bind("<Double-1>", self.on_tree_select)

        root_node = self.tree_view.insert(
            "", "end", text="Databases", open=True)

        # Add databases to the tree view
        for db in list_dbs():
            self.tree_view.insert(root_node, "end", text=db)

        self.tree_view.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Add a button to open a file
        open_file_btn = ttk.Button(
            self.sidebar, text="Open File", command=self.on_open_file, bootstyle="info")
        open_file_btn.pack(fill=tk.X, padx=10, pady=5)


    def on_tree_select(self, event):
        selected_item = self.tree_view.selection()
        if not selected_item:
            return

        db_name = self.tree_view.item(selected_item[0], "text")
        if db_name == "Databases":
            return

        self.on_select_db(db_name)

        # Clear chat box when a new database is selected
        self.chat_box.delete(1.0, tk.END)
        self.chat_box.insert(tk.END, f"[SYS]: Selected database: {db_name}\n")

    def on_send(self):
        if self.chain is None:
            self.chat_box.insert(tk.END, "\n[SYS]: Please select a database first.\n")
            return

        msg = self.input_entry.get()
        if msg.strip():
            send_message(self.chain, msg, self.chat_box)
            self.input_entry.delete(0, tk.END)

    def on_open_file(self):
        open_file(self.chat_box)

    def on_select_db(self, db):
        if self.active_db == db:
            self.chat_box.insert(tk.END, "\n[SYS]: Database already selected.\n")
            return

        self.chain = select_db(db, self.chat_box)
        self.active_db = db
        ttk.Label(self.status_bar, text=f"[Status]: OK | [Active]: {db}",
                     bootstyle="success").grid(row=0, column=0, sticky="w", padx=10, pady=5)




# Optional helper to run it standalone
if __name__ == "__main__":
    window = Window()
    window.run()
