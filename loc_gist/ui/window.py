import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText

from loc_gist.rag.api import list_dbs
from .handlers import send_message, open_file, select_db

class DbHandler:
    def __init__(self):
        self.chain = None
        self.active_db = None
        self.list = []

    def activate(self, db_name):
        if self.active_db == db_name:
            return False

        self.chain = select_db(db_name)
        self.active_db = db_name
        return True

    def get_chain(self):
        if self.chain is None:
            raise ValueError("No active database selected.")
        return self.chain

    def get_dbs(self):
        if not self.list:
            self.list = list_dbs()
        return self.list

class Window(ttk.Window):
    def __init__(self, theme="cyborg"):
        super().__init__(themename=theme)
        self.title("Local RAG System")
        self.geometry("800x600")
        self.db_handler = DbHandler()
        self.layout = Layout(parent=self)

    def run(self):
        self.layout.pack(expand=True, fill=tk.BOTH)
        self.mainloop()

class Layout(ttk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent, padding=10)
        self.parent = parent
        self.db_handler = parent.db_handler
        self.pack(expand=True, fill=tk.BOTH)
        self.sidebar = Sidebar(parent=self, title="Databases")
        main = ttk.Frame(self)
        main.pack(expand=True, fill=tk.BOTH)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self.chat_box = ChatBox(parent=main, db_handler=self.db_handler)
        self.status_bar = StatusBar(parent=main, db_handler=self.db_handler)
        self.chat_box.pack(expand=True, fill=tk.BOTH)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


class StatusBar(ttk.Frame):
    def __init__(self, db_handler, parent=None):
        super().__init__(parent, padding=5)
        self.parent = parent
        self.db_handler = db_handler
        self.pack(side=tk.BOTTOM, fill=tk.X)
        self.update("IDLE", "NONE")

    def update(self, status, db_name):
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text=f"[STATUS]: {status}", bootstyle="warning").pack(side=tk.LEFT, padx=10)
        ttk.Label(self, text=f"[DB]: {db_name}", bootstyle="info").pack(side=tk.RIGHT, padx=10)

class ChatBox(ttk.Frame):
    def __init__(self, db_handler, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db_handler = db_handler
        self.text_box = ScrolledText(self, wrap=tk.WORD, font=("Courier Mono", 10), state=tk.DISABLED)
        self.text_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        self.input = ttk.Entry(self)
        self.input.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.input.bind("<Return>", self.on_enter)


    def on_enter(self, event):
        if self.db_handler.chain is None:
            self.write("Please select a database first.")
            return
        msg = self.input.get().strip()
        if msg:
            # send_message(self.parent.db_handler.get_chain(), msg, self)
            self.write(msg)
            self.input.delete(0, tk.END)

    def write(self, msg):
        """Append message to chat box."""
        self.text_box.insert(tk.END, f"\n{msg}")
        self.text_box.see(tk.END)


class Sidebar(ttk.Labelframe):
    def __init__(self, title, parent=None):
        super().__init__(parent, text=title, width=250)
        self.parent = parent
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.create_meter()
        self.create_widgets()

    def create_widgets(self):
        self.db_combo = ttk.Combobox(
            self, values=list_dbs(), state="readonly", bootstyle="primary"
        )
        self.db_combo.pack(fill=tk.X, padx=10, pady=5)
        self.db_combo.bind("<<ComboboxSelected>>", lambda e: self.on_db_select(self.db_combo.get()))
        self.db_combo.set("Select a database")

        refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh_db_list, bootstyle="primary-outline")
        refresh_btn.pack(fill=tk.X, padx=10, pady=5)

        open_file_btn = ttk.Button(self, text="Open File", command=lambda: open_file(self.parent.chat_box), bootstyle="info")
        open_file_btn.pack(fill=tk.X, padx=10, pady=5)

    def create_meter(self):
        self.meter = ttk.Meter(self,
                metersize=100,
                padding=5,
                interactive=True,
                amountused=25,
                stripethickness=10
            )
        self.meter.pack(pady=10, padx=10, fill=tk.X)

    def refresh_db_list(self):
        dbs = self.parent.db_handler.get_dbs()
        if not dbs:
            dbs = ["No databases found."]
        self.db_combo['values'] = dbs
        if dbs:
            self.db_combo.set(dbs[0])

    def on_db_select(self, db_name):
        if not self.parent.db_handler.activate(db_name):
            self.parent.chat_box.insert(tk.END, f"\n[SYS]: Database '{db_name}' already selected.\n")
            return

        self.parent.chat_box.write(f"[SYS]: Connected to database '{db_name}'.")
        self.parent.status_bar.update(status="OK", db_name=db_name)








# class UI:
#     def __init__(self):
#         self.root = ttk.Window(themename="cyborg")
#         self.sidebar = None
#         self.tree_view = None
#         self.db_combo = None
#         self.chat_box = None
#         self.input_entry = None
#         self.chain = None
#         self.active_db = None
#         self.status_bar = None
#         self.build_ui()
#
#     def run(self):
#         self.refresh_db_list()
#         self.root.mainloop()
#
#     def build_ui(self):
#         self.root.title("Local RAG System")
#         self.root.geometry("800x600")
#         self.root.grid_rowconfigure(0, weight=1)
#         self.root.grid_columnconfigure(1, weight=1)
#
#         # Sidebar
#         self.sidebar = ttk.Frame(self.root, width=250, bootstyle="dark",)
#         self.sidebar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
#         self.sidebar.grid_propagate(False)
#
#         # Main Area
#         main = ttk.Frame(self.root)
#         main.grid(row=0, column=1, sticky="nsew")
#         main.grid_rowconfigure(1, weight=1)
#         main.grid_columnconfigure(0, weight=1)
#
#         self.status_bar = ttk.Frame(main)
#         self.status_bar.grid(row=0, column=0, sticky="new", padx=10, pady=10)
#
#         ttk.Label(self.status_bar, text="[STATUS]: IDLE", bootstyle="warning").grid(
#             row=0, column=0, sticky="w", padx=10, pady=5)
#
#         # Chat Box
#         self.chat_box = scrolledtext.ScrolledText(main, wrap=tk.WORD, font=("Courier Mono", 10))
#         self.chat_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
#
#         # Bottom Input
#         bottom = ttk.Frame(main)
#         bottom.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
#         bottom.grid_columnconfigure(0, weight=1)
#
#         self.input_entry = ttk.Entry(bottom, bootstyle="info")
#         self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
#
#         ttk.Button(bottom, text="Send", command=self.on_send,
#                    bootstyle="success").grid(
#             row=0, column=1, padx=5)
#
#     def refresh_db_list(self):
#         for widget in self.sidebar.winfo_children():
#             widget.destroy()
#
#         ttk.Label(self.sidebar, text="Databases").pack(pady=10)
#
#         db_list = list_dbs()
#         if not db_list:
#             db_list = ["No databases found."]
#         self.db_combo = ttk.Combobox(
#             self.sidebar, values=db_list, state="readonly",
#             bootstyle="primary")
#         self.db_combo.pack(fill=tk.X, padx=10, pady=5)
#         self.db_combo.bind("<<ComboboxSelected>>", lambda e: self.on_select_db(self.db_combo.get()))
#         self.db_combo.set("Select a database")
#
#         refresh_btn = ttk.Button(self.sidebar, text="Refresh",
#                                  command=self.refresh_db_list,
#                                  bootstyle="primary-outline").pack(fill=tk.X, padx=10, pady=5)
#
#         # Add a button to open a file
#         open_file_btn = ttk.Button(
#             self.sidebar, text="Open File", command=self.on_open_file, bootstyle="info")
#         open_file_btn.pack(fill=tk.X, padx=10, pady=5)
#
#
#     def on_send(self):
#         if self.chain is None:
#             self.chat_box.insert(tk.END, "\n[SYS]: Please select a database first.\n")
#             return
#
#         msg = self.input_entry.get()
#         if msg.strip():
#             send_message(self.chain, msg, self.chat_box)
#             self.input_entry.delete(0, tk.END)
#
#     def on_open_file(self):
#         open_file(self.chat_box)
#
#     def on_select_db(self, db):
#         if self.active_db == db:
#             self.chat_box.insert(tk.END, "\n[SYS]: Database already selected.\n")
#             return
#
#         self.chain = select_db(db, self.chat_box)
#         self.active_db = db
#
#         for widget in self.status_bar.winfo_children():
#             widget.destroy()
#
#         ttk.Label(self.status_bar, text=f"[Status]: OK",
#                      bootstyle="success").grid(row=0, column=0, sticky="w", padx=10, pady=5)
#         ttk.Label(self.status_bar, text=f"[Active DB]: {db}",
#                         bootstyle="info").grid(row=0, column=1, sticky="w", padx=10, pady=5)
#



# Optional helper to run it standalone
if __name__ == "__main__":
    window = Window()
    window.run()
