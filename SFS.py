import os
import time
from datetime import datetime
import ttkbootstrap as ttk
from tkinter import filedialog, StringVar
from ttkbootstrap.constants import *
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter.messagebox as messagebox

class SimpleFileScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple File Scanner (SFS)")
        self.root.geometry("600x400")
        self.root.style = ttk.Style('darkly')

        # Variables
        self.folder_path = StringVar()
        self.days_unused = StringVar()
        self.days_unused.set("30")  # Default value

        # UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Title
        ttk.Label(self.root, text="Simple File Scanner (SFS)", style="primary.TLabel", font=('Helvetica', 18, 'bold')).pack(pady=20)

        # Folder Selection
        folder_frame = ttk.Frame(self.root, padding=10)
        folder_frame.pack(fill=X)
        ttk.Label(folder_frame, text="Select Folder:", style="secondary.TLabel").pack(side=LEFT)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=40, state='readonly', style="info.TEntry")
        folder_entry.pack(side=LEFT, padx=5)
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder, style="info.TButton").pack(side=LEFT)

        # Drag and Drop
        folder_entry.drop_target_register(DND_FILES)
        folder_entry.dnd_bind('<<Drop>>', self.drop_folder)

        # Days Unused
        days_frame = ttk.Frame(self.root, padding=10)
        days_frame.pack(fill=X)
        ttk.Label(days_frame, text="Days Unused:", style="secondary.TLabel").pack(side=LEFT)
        ttk.Entry(days_frame, textvariable=self.days_unused, width=5, style="info.TEntry").pack(side=LEFT, padx=5)

        # Scan Button
        ttk.Button(self.root, text="Scan", command=self.scan_files, style="success.TButton").pack(pady=20)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.root, orient=HORIZONTAL, mode='determinate', length=500)
        self.progress_bar.pack(pady=20)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def drop_folder(self, event):
        self.folder_path.set(event.data)

    def scan_files(self):
        directory = self.folder_path.get()
        days_unused = int(self.days_unused.get())
        if not directory:
            messagebox.showerror("Error", "Please select a directory to scan.")
            return

        unused_files = self.scan_for_unused_files(directory, days_unused)
        self.write_to_file(unused_files)

        messagebox.showinfo("Scan Complete", f"Found {len(unused_files)} unused files. The list has been written to FoundFiles.txt")

    def scan_for_unused_files(self, directory, days_unused):
        unused_files = []
        current_time = time.time()
        cutoff_time = current_time - (days_unused * 86400)  # Convert days to seconds

        total_files = sum(len(files) for _, _, files in os.walk(directory))
        processed_files = 0

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    last_access_time = os.path.getatime(file_path)
                    if last_access_time < cutoff_time:
                        unused_files.append(file_path)

                processed_files += 1
                self.progress_bar['value'] = (processed_files / total_files) * 100
                self.root.update_idletasks()

        return unused_files

    def write_to_file(self, file_list):
        with open("FoundFiles.txt", 'w') as f:
            for file in file_list:
                f.write(f"{file}\n")

def main():
    root = TkinterDnD.Tk()
    app = SimpleFileScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
