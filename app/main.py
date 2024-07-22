import tkinter as tk
from tkinter import scrolledtext
import idlelib.colorizer as ic
import idlelib.percolator as ip
import requests
import random

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.state("zoomed")
        self.title("Mandelbrot Code Editor")

        # Initialize the ScrolledText widget with color settings
        self.text = scrolledtext.ScrolledText(self, bg='#636363', fg='#F0F0F0', insertbackground='#F0F0F0', wrap=tk.WORD, font=("Courier", 12))
        self.text.pack(fill=tk.BOTH, expand=True)

        # Initialize color delegator and customize tag colors
        self.cdg = ic.ColorDelegator()
        self.cdg.tagdefs['COMMENT'] = {'foreground': '#848484', 'background': '#636363'}  # Comment color
        self.cdg.tagdefs['KEYWORD'] = {'foreground': '#C586C0', 'background': '#636363'}  # Keyword color
        self.cdg.tagdefs['BUILTIN'] = {'foreground': '#4EC9B0', 'background': '#636363'}  # Built-in function color
        self.cdg.tagdefs['STRING'] = {'foreground': '#CE9178', 'background': '#636363'}  # String color
        self.cdg.tagdefs['DEFINITION'] = {'foreground': '#4EC9B0', 'background': '#636363'}  # Definition color

        self.text.config(state="normal")
        ip.Percolator(self.text).insertfilter(self.cdg)
        self.text.config(state="disabled")

        # Fetch and set the initial code from GitHub
        self.code = self.fetch_random_code()
        self.after(100)

        # Set initial index for insertion
        self.index = 0
        # Bind key press events to the insert_text method
        self.bind("<KeyPress>", self.insert_text)

    def fetch_random_code(self):
        try:
            # Search for popular repositories with code files
            search_url = "https://api.github.com/search/repositories"
            params = {'q': 'language:python', 'sort': 'stars', 'order': 'desc', 'per_page': 30}
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            repos = response.json()['items']

            # Choose a random repository
            repo = random.choice(repos)
            repo_name = repo['full_name']

            # Get a list of files in the repository's main branch
            contents_url = f"https://api.github.com/repos/{repo_name}/contents"
            response = requests.get(contents_url)
            response.raise_for_status()
            contents = response.json()

            # Filter out non-code files and choose a random code file
            code_extensions = {'.py', '.js', '.java', '.rb', '.cpp', '.h', '.c', '.cs'}
            files = [file for file in contents if file['type'] == 'file' and any(file['name'].endswith(ext) for ext in code_extensions)]

            if not files:
                return self.fetch_random_code()

            file = random.choice(files)
            file_url = file['download_url']

            # Fetch the code from the file
            response = requests.get(file_url)
            response.raise_for_status()
            if len(response.text) < 500:
                return self.fetch_random_code()
            return response.text

        except requests.RequestException as e:
            print(f"Failed to fetch code: {e}")
            return "# Failed to fetch code"

    def insert_text(self, event):
        if self.index == 0:
            self.text.delete("1.0", tk.END)
        if self.index > len(self.code) - 1:
            self.index = 0
        self.text.config(state="normal")

        char = event.char
        if char:
            while self.code[self.index] == " ":
                self.text.insert(tk.END, self.code[self.index])
                self.index += 1
                self.text.see(tk.END)
            self.text.insert(tk.END, self.code[self.index])
            self.index += 1
            self.text.see(tk.END)
        self.text.update_idletasks()
        self.text.config(state="disabled")

app = App()
app.mainloop()
