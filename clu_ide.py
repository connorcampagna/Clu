import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

class CLUIde:
    def __init__(self, root):
        self.root = root
        self.root.title("CLU IDE")

        # Menu Bar
        self.menu = tk.Menu(root)
        root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        self.text_editor = tk.Text(root, wrap="word", font=("Consolas", 12))
        self.text_editor.grid(row=0, column=0, sticky="nsew")

        self.output_box = tk.Text(root, wrap="word", height=10, bg="#ffffff", fg="#000000", font=("Consolas", 10))
        self.output_box.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.output_box.config(state="disabled")

        self.run_button = tk.Button(root, text="Run", command=self.run_code)
        self.run_button.grid(row=0, column=1, sticky="n")

        self.clear_button = tk.Button(root, text="Clear Output", command=self.clear_output)
        self.clear_button.grid(row=0, column=1, sticky="s")

        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=0)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=0)

        self.current_file = None

    def run_code(self):
        code = self.text_editor.get("1.0", tk.END)
        temp_filename = "temp.clu"
        with open(temp_filename, "w") as f:
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
        filename = filedialog.askopenfilename(
            defaultextension=".clu",
            filetypes=[("CLU Files", "*.clu"), ("All Files", "*.*")]
        )
        if filename:
            with open(filename, "r") as f:
                content = f.read()
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert(tk.END, content)
            self.current_file = filename
            self.root.title(f"CLU IDE - {os.path.basename(filename)}")

    def save_file(self):
        if self.current_file:
            filename = self.current_file
        else:
            filename = filedialog.asksaveasfilename(
                defaultextension=".clu",
                filetypes=[("CLU Files", "*.clu"), ("All Files", "*.*")]
            )
        if filename:
            with open(filename, "w") as f:
                f.write(self.text_editor.get("1.0", tk.END))
            self.current_file = filename
            self.root.title(f"CLU IDE - {os.path.basename(filename)}")

    def clear_output(self):
        self.output_box.config(state="normal")
        self.output_box.delete("1.0", tk.END)
        self.output_box.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = CLUIde(root)
    root.geometry("900x600")
    root.mainloop()
