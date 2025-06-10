import tkinter as tk
from tkinter import scrolledtext
from .handlers import send_message, open_file, select_db
from loc_gist.rag.api import list_dbs


class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.sidebar = None
        self.chat_box = None
        self.input_entry = None
        self.chain = None

    def run(self):
        self.build_ui()
        self.refresh_db_list()
        self.root.mainloop()

    def build_ui(self):
        self.root.title("Local RAG System")
        self.root.geometry("800x600")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar = tk.Frame(self.root, width=150, bg="#333")
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        # Main Area
        main = tk.Frame(self.root, bg="#f9f9f9")
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # Chat Box
        self.chat_box = scrolledtext.ScrolledText(
            main, wrap=tk.WORD, font=("Arial", 12)
        )
        self.chat_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Bottom Input
        bottom = tk.Frame(main, bg="#ddd")
        bottom.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        bottom.grid_columnconfigure(0, weight=1)

        self.input_entry = tk.Entry(bottom, font=("Arial", 12))
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        tk.Button(bottom, text="Send", command=self.on_send).grid(
            row=0, column=1, padx=5)
        tk.Button(bottom, text="📁", command=self.on_open_file).grid(
            row=0, column=2)

    def refresh_db_list(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        tk.Label(self.sidebar, text="Home", fg="white",
                 bg="#333", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.sidebar, text="Refresh List", command=self.refresh_db_list)\
            .pack(fill=tk.X, padx=10, pady=5)

        for db in list_dbs():
            tk.Button(self.sidebar, text=db, command=lambda db=db: self.on_select_db(db))\
                .pack(fill=tk.X, padx=10, pady=5)

    def on_send(self):
        if self.chain is None:
            self.chat_box.insert(tk.END, "\nPlease select a database first.\n")
            return

        msg = self.input_entry.get()
        if msg.strip():
            send_message(self.chain, msg, self.chat_box)
            self.input_entry.delete(0, tk.END)

    def on_open_file(self):
        open_file(self.chat_box)

    def on_select_db(self, db):
        self.chain = select_db(db, self.chat_box)


# Optional helper to run it standalone
if __name__ == "__main__":
    window = Window()
    window.run()
