import tkinter as tk
from tkinter import filedialog, scrolledtext
from rag import create_db, list_dbs, init_chat, get_response


def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        db_name = file_path.split("/")[-1].split(".")[0]
        db_path = create_db(file_path, db_name)
        chat_box.insert(
            tk.END, f"\n📂 Database '{db_name}' created at {db_path}")


def send_message():
    msg = input_entry.get()
    if msg.strip():
        chat_box.insert(tk.END, f"\n😍 You: {msg}")
        input_entry.delete(0, tk.END)
        response = get_response(msg)
        chat_box.insert(tk.END, f"\n🧠 AI: {response}")


app = tk.Tk()
app.title("Local RAG System")
app.geometry("800x600")

# --- Layout config ---
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)

# --- Sidebar ---
sidebar = tk.Frame(app, width=150, bg="#333")
sidebar.grid(row=0, column=0, sticky="ns", ipadx=20, ipady=10)
sidebar.grid_propagate(False)

tk.Label(sidebar, text="Home", fg="white",
         bg="#333", font=("Arial", 16)).pack(pady=10)


def select_db(db_name):
    chat_box.insert(tk.END, "\nInitializing model...")
    status = init_chat(db_name)
    chat_box.insert(tk.END, status)


def refresh_db_list():
    global db_list
    db_list = list_dbs()
    for widget in sidebar.winfo_children():
        widget.destroy()

    refresh_db_btn = tk.Button(
        sidebar, text="Refresh List", command=refresh_db_list)
    refresh_db_btn.pack(fill=tk.X, padx=10, pady=5)

    for db in db_list:
        db_btn = tk.Button(
            sidebar, text=db, command=lambda db=db: select_db(db))
        db_btn.pack(fill=tk.X, padx=10, pady=5)


# --- Database List ---
refresh_db_list()

# --- Settings Button ---
settings_btn = tk.Button(sidebar, text="Settings",
                         command=lambda: print("Settings clicked"))
settings_btn.pack(fill=tk.X, padx=10, pady=5)

# --- Main Content Area ---
main = tk.Frame(app, bg="#f9f9f9")
main.grid(row=0, column=1, sticky="nsew")
main.grid_rowconfigure(0, weight=1)
main.grid_rowconfigure(1, weight=0)
main.grid_columnconfigure(0, weight=1)

# Chat Box (Text Area)
chat_box = scrolledtext.ScrolledText(
    main, wrap=tk.WORD, state="normal", font=("Arial", 12))
chat_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

# --- Bottom Input ---
bottom_frame = tk.Frame(main, bg="#ddd")
bottom_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
bottom_frame.grid_columnconfigure(0, weight=1)

input_entry = tk.Entry(bottom_frame, font=("Arial", 12))
input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

send_btn = tk.Button(bottom_frame, text="Send", command=send_message)
send_btn.grid(row=0, column=1, padx=(0, 5))

file_btn = tk.Button(bottom_frame, text="📁", command=open_file)
file_btn.grid(row=0, column=2)

app.mainloop()
