import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from datetime import datetime

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

        self.status_bar = StatusBar(parent=main)
        self.status_bar.pack(expand=True, fill=tk.X, padx=10, pady=4)

        self.tab_window = TabWindow(parent=main, window=window, bootstyle="secondary")
        self.tab_window.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)


class TabWindow(ttk.Notebook):
    def __init__(self, window: "Window", parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.window = window
        self.chat_tab = ChatBox(parent=self, window=window)
        self.log_tab = LogBox(parent=self)
        self.project_tab = ttk.Frame(self)

        self.add(self.chat_tab, text="Smart Search")
        self.add(self.log_tab, text="AI Logs")
        self.add(self.project_tab, text="Project Details")

        self._populate_tabs()

    def _populate_tabs(self):
        ttk.Label(self.project_tab, text="Project view").pack(padx=10, pady=10)

class StatusBar(ttk.Labelframe):
    def __init__(self, parent=None):
        super().__init__(parent, text="Status")
        self.parent = parent
        # Widgets
        self.status_var = tk.StringVar(value="IDLE")
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        self.progress = ttk.Progressbar(self, mode="indeterminate", bootstyle="secondary")

    def update(self, status, db_name=None):
        self.status_var.set(str(status))
        busy = str(status).upper() in {"THINKING", "PROCESSING", "WORKING", "BUSY"}
        if busy:
            if not self.progress.winfo_ismapped():
                self.progress.pack(side=tk.LEFT, padx=6)
            try:
                self.progress.start(10)
            except Exception:
                pass
        else:
            try:
                self.progress.stop()
            except Exception:
                pass
            if self.progress.winfo_ismapped():
                self.progress.pack_forget()

class LogBox(ttk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_box = ScrolledText(self, wrap=tk.WORD, font=("Courier Mono", 10), state=tk.DISABLED)
        self.text_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        # tags for levels
        self.text_box.text.tag_configure("time", foreground="#6c757d")
        self.text_box.text.tag_configure("sys", foreground="#0d6efd")
        self.text_box.text.tag_configure("warn", foreground="#fd7e14")
        self.text_box.text.tag_configure("error", foreground="#dc3545", underline=True)

    def write(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        level_tag = None
        upper = str(msg).upper()
        if upper.startswith("[SYS]"):
            level_tag = "sys"
        elif "WARN" in upper or "WARNING" in upper:
            level_tag = "warn"
        elif "ERR" in upper or "ERROR" in upper:
            level_tag = "error"
        # enable
        self.text_box.text.config(state=tk.NORMAL)
        # time
        self.text_box.text.insert(tk.END, f"[{now}] ", ("time",))
        # body
        if level_tag:
            self.text_box.text.insert(tk.END, f"{msg}\n", (level_tag,))
        else:
            self.text_box.text.insert(tk.END, f"{msg}\n")
        self.text_box.text.see(tk.END)
        self.text_box.text.config(state=tk.DISABLED)

class ChatBox(ttk.Frame):
    def __init__(self, window: "Window", parent=None):
        super().__init__(parent)
        self.window = window

        self.text_box = ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED)
        self.text_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        # tags for chat bubbles
        self.text_box.text.tag_configure("user_header", foreground="#0d6efd", font=("Helvetica", 10, "bold"), lmargin1=40, lmargin2=40, rmargin=10, spacing3=6, justify="right")
        self.text_box.text.tag_configure("bot_header", foreground="#198754", font=("Helvetica", 10, "bold"))
        self.text_box.text.tag_configure("user_msg", lmargin1=40, lmargin2=40, rmargin=10, spacing3=6, justify="right")
        self.text_box.text.tag_configure("bot_msg", lmargin1=10, lmargin2=10, rmargin=40, spacing3=6, justify="left")
        self.text_box.text.tag_configure("time", foreground="#6c757d", font=("Helvetica", 8))


        self.search_bar = ttk.Frame(self)
        self.search_bar.pack(side=tk.TOP, expand=True, fill=tk.X, padx=10)
        self.search_bar.grid_rowconfigure(0, weight=1)
        self.search_bar.grid_columnconfigure(0, weight=1)


        self.input = ttk.Entry(self.search_bar, bootstyle="primary")
        self.input.pack(expand=True, fill=tk.X, side=tk.LEFT)
        self.input.bind("<Return>", self.handle_input)

        self.button = ttk.Button(self.search_bar, text="Send", command=lambda: self.handle_input(None), bootstyle="primary")
        self.button.pack(padx=10, pady=5, side=tk.LEFT)

    def start_thinking(self):
        # Disable user input while processing
        try:
            self.input.config(state=tk.DISABLED)
            self.button.config(state=tk.DISABLED)
        except Exception:
            pass

    def stop_thinking(self):
        # Re-enable user input when done
        try:
            self.input.config(state=tk.NORMAL)
            self.button.config(state=tk.NORMAL)
            self.input.focus_set()
        except Exception:
            pass

    def handle_input(self, event):
        msg = self.input.get().strip()
        if msg:
            self.write_user(msg)
            self.input.delete(0, tk.END)
            self.window.handle_input(msg)

    def write_user(self, msg: str):
        self._append_message("You", msg, is_user=True)

    def write_bot(self, msg: str):
        self._append_message("Assistant", msg, is_user=False)

    def write(self, msg, tag="user"):
        self.write_user(msg) if tag == "user" else self.write_bot(msg)

    def _append_message(self, sender: str, msg: str, is_user: bool):
        now = datetime.now().strftime("%H:%M")
        header_tag = "user_header" if is_user else "bot_header"
        body_tag = "user_msg" if is_user else "bot_msg"
        text = self.text_box.text
        text.config(state=tk.NORMAL)
        if text.index("end-1c") != "1.0":
            text.insert(tk.END, "\n")
        text.insert(tk.END, f"{sender} ", (header_tag,))
        text.insert(tk.END, f"[{now}]\n", ("time",))
        text.insert(tk.END, f"{msg}\n", (body_tag,))
        text.see(tk.END)
        text.config(state=tk.DISABLED)


class SettingsDialog(tk.Toplevel):
    def __init__(self, window: "Window"):
        super().__init__(window)
        self.window = window
        self.title("Settings")
        self.resizable(False, False)
        self.transient(window)
        self.grab_set()

        s = getattr(window, "settings", {}) or {}
        temp = s.get("temperature", 0.2)
        topk = s.get("top_k", 4)
        maxtoks = s.get("max_tokens", 1024)

        self.var_temp = tk.DoubleVar(value=temp)
        self.var_topk = tk.IntVar(value=topk)
        self.var_maxtoks = tk.IntVar(value=maxtoks)

        body = ttk.Frame(self, padding=12)
        body.pack(fill=tk.BOTH, expand=True)

        ttk.Label(body, text="Temperature").grid(row=0, column=0, sticky=tk.W, pady=4)
        ttk.Entry(body, textvariable=self.var_temp, width=10).grid(row=0, column=1, sticky=tk.W, pady=4)
        ttk.Label(body, text="Top K Sources").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(body, textvariable=self.var_topk, width=10).grid(row=1, column=1, sticky=tk.W, pady=4)
        ttk.Label(body, text="Max Tokens").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(body, textvariable=self.var_maxtoks, width=10).grid(row=2, column=1, sticky=tk.W, pady=4)

        # Buttons
        btns = ttk.Frame(self, padding=(12, 0, 12, 12))
        btns.pack(fill=tk.X)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btns, text="Save", bootstyle="primary", command=self.on_save).pack(side=tk.RIGHT)

        self.update_idletasks()
        x = window.winfo_rootx() + (window.winfo_width() // 2) - (self.winfo_width() // 2)
        y = window.winfo_rooty() + (window.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def on_save(self):
        try:
            temp = max(0.0, min(2.0, float(self.var_temp.get())))
        except Exception:
            temp = 0.2
        try:
            topk = max(1, int(self.var_topk.get()))
        except Exception:
            topk = 4
        try:
            maxtoks = max(1, int(self.var_maxtoks.get()))
        except Exception:
            maxtoks = 1024

        payload = {"temperature": temp, "top_k": topk, "max_tokens": maxtoks}
        if hasattr(self.window, "apply_settings"):
            self.window.apply_settings(payload)
        self.destroy()


class Sidebar(ttk.Labelframe):
    def __init__(self, title: str, parent:Layout, window: "Window"):
        super().__init__(parent, width=250, text=title)
        self.window = window
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.create_widgets()
        self.refresh_db_list()

    def create_widgets(self):
        self.active_var = tk.StringVar(value="NONE")
        self.active_frame = ttk.Frame(self, bootstyle="secondary")
        self.active_frame.pack(fill=tk.X, padx=10, pady=(10, 6))
        ttk.Label(self.active_frame, text="Active Database").pack(anchor=tk.W)
        self.active_label = ttk.Label(self.active_frame, textvariable=self.active_var, bootstyle="success")
        self.active_label.pack(anchor=tk.W, padx=2, pady=(4, 0))

        ttk.Separator(self).pack(fill=tk.X, padx=8, pady=8)

        ttk.Label(self, text="Databases").pack(anchor=tk.W, padx=12)

        self.db_group = ttk.Frame(self, bootstyle="secondary")
        self.db_group.pack(fill=tk.X, padx=10, pady=6)

        refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh_db_list)
        refresh_btn.pack(fill=tk.X, padx=10, pady=5)
        open_file_btn = ttk.Button(self, text="Open File", command=self.window.create_db)

        open_file_btn.pack(fill=tk.X, padx=10, pady=5)

        settings_btn = ttk.Button(self, text="Settings", bootstyle="secondary", command=self.open_settings)
        settings_btn.pack(fill=tk.X, padx=10, pady=(0, 10))

    def open_settings(self):
        SettingsDialog(self.window)

    def refresh_db_list(self):
        active = self.window.db_handler.active_db or "NONE"
        self.active_var.set(active)

        dbs = self.window.db_handler.get_dbs()
        for widget in self.db_group.winfo_children():
            widget.destroy()
        for db in dbs:
            is_active = (db == self.window.db_handler.active_db)
            style = "success" if is_active else "primary-link"
            btn_text = f"{db} (Active)" if is_active else db
            btn = ttk.Button(
                self.db_group,
                text=btn_text,
                command=(lambda db=db: self.on_db_select(db)) if not is_active else None,
                bootstyle=style,
                state=(tk.DISABLED if is_active else tk.NORMAL),
            )
            btn.pack(fill=tk.X, padx=10, pady=4)

    def on_db_select(self, db_name):
        if not self.window.db_handler.activate(db_name):
            self.window.write_log(f"\n[SYS]: Database '{db_name}' already selected.\n")
            return

        self.window.write_log(f"[SYS]: Connected to database '{db_name}'.")
        self.window.update_status(status="OK", db_name=db_name)
        self.refresh_db_list()
