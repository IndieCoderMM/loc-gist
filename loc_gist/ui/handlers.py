import tkinter as tk
from tkinter import filedialog
from loc_gist.rag.api import query_rag, index_db, chain_db
from tkinter import END


def open_file(chat_box):
    path = filedialog.askopenfilename()
    if not path:  # User cancelled the file dialog
        return
    db_name = path.split("/")[-1].split(".")[0]
    db_path = index_db(path, db_name)
    append_user_msg(f"📂 Database '{db_name}' created at {db_path}", chat_box)


def send_message(chain, msg, chat_box):
    append_user_msg(msg, chat_box)
    response = query_rag(chain, msg)
    append_ai_msg(response, chat_box)


def select_db(db_name, chat_box):
    chat_box.insert(tk.END, "\nInitializing model...")
    chain, status = chain_db(db_name)
    chat_box.insert(tk.END, status)

    return chain


def append_user_msg(msg, chat_box):
    chat_box.insert(END, f"\n😍 You: {msg}")


def append_ai_msg(msg, chat_box):
    chat_box.insert(END, f"\n🧠 AI: {msg}")
