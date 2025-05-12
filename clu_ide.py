

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk as tkttk
import subprocess
import os

KEYWORDS = {
    "control": ["function", "if", "otherwise", "end", "repeat"],
    "logic": ["greater", "less", "equal", "greater_equal", "less_equal"],
    "math": ["add", "subtract", "multiply", "divide"],
    "core": ["var", "is", "output"]
}

COLORS = {
    "control": "#ffcc00",
    "logic": "#ff9933",
    "math": "#00ffff",
    "core": "#80dfff"
}



class CLUIde:
    def __init__(self, root):
        self.root = root
        self.root.title("CLU IDE")

        self.notebook = tkttk.Notebook(root)
        self.notebook.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.tabs = []

        # Output box
        self.output_box = tk.Text(root, height=10, bg="#2e2e2e", fg="white", font=("Fira Code", 11))
        self.output_box.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.output_box.config(state="disabled")

        # Buttons
        self.run_button = ttk.Button(root, text="▶ Run", command=self.run_code, bootstyle="success")
        self.run_button.grid(row=2, column=1, sticky="e", pady=5, padx=5)

        self.clear_button = ttk.Button(root, text="🗑 Clear Output", command=self.clear_output, bootstyle="secondary")
        self.clear_button.grid(row=2, column=2, sticky="e", pady=5, padx=5)

        self.tab_menu = tk.Menu(self.root, tearoff=0)
        self.tab_menu.add_command(label="Close Tab", command=self.close_current_tab)
        self.notebook.bind("<Button-3>", self.show_tab_menu)

        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Tab", command=self.new_tab)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=0)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=0)
        root.grid_columnconfigure(2, weight=0)

        self.new_tab()

    def new_tab(self):
        frame = tk.Frame(self.notebook)
        line_numbers = tk.Canvas(frame, width=40, bg="#2a2a2a", highlightthickness=0)
        line_numbers.pack(side="left", fill="y")

        text_editor = tk.Text(frame, wrap="word", font=("Fira Code", 13),
                              bg="#1e1e1e", fg="white", insertbackground="white", undo=True, autoseparators=True)
        text_editor.pack(side="right", fill="both", expand=True)

        text_editor.bind("<KeyRelease>", lambda e: [self.highlight_syntax(text_editor), self.redraw_line_numbers(text_editor, line_numbers)])
        text_editor.bind("<Return>", lambda e: self.auto_indent(e, text_editor))
        text_editor.bind("<Tab>", lambda e: self.insert_tab(e, text_editor))
        text_editor.bind("<Option-space>", lambda e: self.show_autocomplete(e, text_editor))  # Mac-friendly

        self.tabs.append({
            "frame": frame,
            "editor": text_editor,
            "lines": line_numbers,
            "path": None
        })

        self.notebook.add(frame, text="Untitled")
        self.notebook.select(frame)

    def get_current_tab(self):
        idx = self.notebook.index(self.notebook.select())
        return self.tabs[idx]

    def show_tab_menu(self, event):
        # Show menu only if user clicked on a tab
        try:
            index = self.notebook.index(f"@{event.x},{event.y}")
            self.notebook.select(index)
            self.tab_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tab_menu.grab_release()

    def close_current_tab(self):
        index = self.notebook.index(self.notebook.select())
        self.notebook.forget(index)
        del self.tabs[index]

    def redraw_line_numbers(self, editor, canvas):
        canvas.delete("all")
        i = editor.index("@0,0")
        while True:
            dline = editor.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            canvas.create_text(35, y, anchor="ne", text=linenum, fill="#888888", font=("Fira Code", 11))
            i = editor.index(f"{i}+1line")

    def highlight_syntax(self, editor):
        for tag in editor.tag_names():
            editor.tag_remove(tag, "1.0", "end")

        for category, words in KEYWORDS.items():
            for word in words:
                start = "1.0"
                while True:
                    pos = editor.search(word, start, stopindex="end")
                    if not pos:
                        break
                    end = f"{pos}+{len(word)}c"
                    before = editor.get(f"{pos} -1c", pos)
                    after = editor.get(end, f"{end} +1c")
                    if not before.isalnum() and not after.isalnum():
                        editor.tag_add(category, pos, end)
                    start = end
            editor.tag_config(category, foreground=COLORS[category])

        # Numbers
        start = "1.0"
        while True:
            pos = editor.search(r"\m\d+\M", start, stopindex="end", regexp=True)
            if not pos:
                break
            end = editor.index(f"{pos} wordend")
            editor.tag_add("number", pos, end)
            start = end
        editor.tag_config("number", foreground="#66ff66")  # light green

        # Lists
        start = "1.0"
        while True:
            pos = editor.search(r"\m\d+(,\d+)+\M", start, stopindex="end", regexp=True)
            if not pos:
                break
            end = editor.index(f"{pos} lineend")
            editor.tag_add("list", pos, end)
            start = end
        editor.tag_config("list", foreground="#00bfff")  # sky blue

        # Strings
        start = "1.0"
        while True:
            pos = editor.search(r"'[^']*'", start, stopindex="end", regexp=True)
            if not pos: break
            match_len = editor.get(pos, "end").find("'", 1) + 2
            if match_len < 2: break
            end = f"{pos}+{match_len}c"
            editor.tag_add("string", pos, end)
            start = end
        editor.tag_config("string", foreground="#ff66cc")

        # Comments
        start = "1.0"
        while True:
            pos = editor.search(r"#.*", start, stopindex="end", regexp=True)
            if not pos: break
            editor.tag_add("comment", pos, f"{pos} lineend")
            start = f"{pos} lineend"
        editor.tag_config("comment", foreground="#888888", font=("Fira Code", 11, "italic"))

    def auto_indent(self, event, editor):
        line = editor.get("insert linestart", "insert")
        indent = len(line) - len(line.lstrip(" "))
        editor.insert("insert", "\n" + " " * indent)
        return "break"

    def insert_tab(self, event, editor):
        editor.insert("insert", "    ")
        return "break"

    def run_code(self):
        editor = self.get_current_tab()["editor"]
        code = editor.get("1.0", tk.END)
        temp_filename = "temp.clu"
        with open(temp_filename, "w", encoding="utf-8") as f:
            f.write(code)

        self.output_box.config(state="normal")
        self.output_box.delete("1.0", tk.END)

        try:
            process = subprocess.Popen(
                ["python", "main.py", temp_filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            if stdout:
                self.output_box.insert(tk.END, stdout)
            if stderr:
                self.output_box.insert(tk.END, "Errors:\n" + stderr)
        except Exception as e:
            messagebox.showerror("Run Error", str(e))
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

        self.output_box.config(state="disabled")

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".clu")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.new_tab()
            tab = self.get_current_tab()
            tab["editor"].delete("1.0", tk.END)
            tab["editor"].insert(tk.END, content)
            tab["path"] = file_path
            self.notebook.tab(tab["frame"], text=os.path.basename(file_path))

    def save_file(self):
        tab = self.get_current_tab()
        file_path = tab["path"]
        if not file_path:
            file_path = filedialog.asksaveasfilename(defaultextension=".clu")
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(tab["editor"].get("1.0", tk.END))
            tab["path"] = file_path
            self.notebook.tab(tab["frame"], text=os.path.basename(file_path))

    def clear_output(self):
        self.output_box.config(state="normal")
        self.output_box.delete("1.0", tk.END)
        self.output_box.config(state="disabled")

if __name__ == "__main__":
    root = ttk.Window(themename="cyborg")
    app = CLUIde(root)
    root.geometry("1100x700")
    root.mainloop()
