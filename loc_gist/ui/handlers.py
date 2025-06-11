import threading
from tkinter import filedialog, END

from loc_gist.rag.api import query_rag, index_db, chain_db


def open_file(chat_box):
    path = filedialog.askopenfilename()
    if not path:  # User cancelled the file dialog
        return
    db_name = path.split("/")[-1].split(".")[0]
    db_path = index_db(path, db_name)
    log_sys(f"Indexed {db_name} at {db_path}", chat_box)

def send_message(chain, msg, chat_box):
    log_user(msg, chat_box)
    log_sys("Processing your query...", chat_box)
    threading.Thread(target=_run_query_and_append, args=(chain, msg, chat_box)).start()

def _run_query_and_append(chain, msg, chat_box):
    response = query_rag(chain, msg)
    # Extract thoughts which are between <think></think>

    if "<think>" in response and "</think>" in response:
        thoughts = response.split("<think>")[1].split("</think>")[0]
        response = response.replace(f"<think>{thoughts}</think>", "").strip()
        log_sys(f"Thoughts: {thoughts}", chat_box)

    chat_box.after(0, log_ai, response, chat_box)

def select_db(db_name):
    chain, status = chain_db(db_name)

    return chain, status


def log_user(msg, chat_box):
    chat_box.insert(END, f"\nYou: {msg}")


def log_ai(msg, chat_box):
    chat_box.insert(END, f"\nAI: {msg}")

def log_sys(msg, chat_box):
    chat_box.insert(END, f"\n[SYS]: {msg}")
