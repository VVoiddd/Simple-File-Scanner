import os
import time
import webbrowser
from datetime import datetime
import ttkbootstrap as ttk
from tkinter import filedialog, StringVar, BooleanVar
from ttkbootstrap.constants import *
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter.messagebox as messagebox
from MoveFiles import move_files
from FileRemover import delete_files

class SimpleFileScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple File Scanner (SFS)")
        self.root.geometry("600x500")
        self.root.style = ttk.Style('darkly')
        self.root.resizable(False, False)  # Disable window resizing

        # Variables
        self.folder_path = StringVar()
        self.days_unused = StringVar()
        self.days_unused.set("30")  # Default value
        self.move_destination = StringVar()

        # Directory skip options
        self.skip_steam = BooleanVar(value=True)
        self.skip_microsoft_store = BooleanVar(value=True)
        self.skip_xbox = BooleanVar(value=True)
        self.skip_discord = BooleanVar(value=True)
        self.skip_ubisoft = BooleanVar(value=True)
        self.skip_other_games = BooleanVar(value=True)

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

        # Move Destination
        move_frame = ttk.Frame(self.root, padding=10)
        move_frame.pack(fill=X)
        ttk.Label(move_frame, text="Move Destination:", style="secondary.TLabel").pack(side=LEFT)
        move_entry = ttk.Entry(move_frame, textvariable=self.move_destination, width=40, state='readonly', style="info.TEntry")
        move_entry.pack(side=LEFT, padx=5)
        ttk.Button(move_frame, text="Browse", command=self.browse_move_folder, style="info.TButton").pack(side=LEFT)

        # Skip options
        skip_frame = ttk.Frame(self.root, padding=10)
        skip_frame.pack(fill=X)
        ttk.Label(skip_frame, text="Skip Directories:", style="secondary.TLabel").pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Steam", variable=self.skip_steam, style="info.TCheckbutton").pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Microsoft Store", variable=self.skip_microsoft_store, style="info.TCheckbutton").pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Xbox", variable=self.skip_xbox, style="info.TCheckbutton").pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Discord", variable=self.skip_discord, style="info.TCheckbutton").pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Ubisoft", variable=self.skip_ubisoft, style="info.TCheckbutton").pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Other Game Stores (Epic Games, Origin, etc.)", variable=self.skip_other_games, style="info.TCheckbutton").pack(anchor='w')

        ttk.Label(self.root, text="* Having these checked means the scanner will skip these directories.", style="warning.TLabel").pack(pady=10)

        # Scan Button
        ttk.Button(self.root, text="Scan", command=self.scan_files, style="success.TButton").pack(pady=10)

        # Move and Delete Buttons
        ttk.Button(self.root, text="Move Files", command=self.move_files_to_destination, style="success.TButton").pack(pady=5)
        ttk.Button(self.root, text="Delete Files", command=self.delete_files, style="danger.TButton").pack(pady=5)

        # Latest Release Button
        ttk.Button(self.root, text="Latest Release", command=self.open_latest_release, style="info.TButton").pack(pady=10)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.root, orient=HORIZONTAL, mode='determinate', length=500)
        self.progress_bar.pack(pady=10)

        # Watermark
        ttk.Label(self.root, text="Made With <3 By tfbt", style="secondary.TLabel", font=("Helvetica", 8)).place(relx=1.0, rely=1.0, anchor='se', x=-5, y=-5)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def browse_move_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.move_destination.set(folder_selected)

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
        skip_dirs = set()
        if self.skip_steam.get():
            skip_dirs.add('steam')
        if self.skip_microsoft_store.get():
            skip_dirs.add('microsoft store')
        if self.skip_xbox.get():
            skip_dirs.add('xbox')
        if self.skip_discord.get():
            skip_dirs.add('discord')
        if self.skip_ubisoft.get():
            skip_dirs.add('ubisoft')
        if self.skip_other_games.get():
            skip_dirs.update(['epic games', 'origin', 'battle.net', 'gog'])

        unused_files = []
        current_time = time.time()
        cutoff_time = current_time - (days_unused * 86400)  # Convert days to seconds

        total_files = sum(len(files) for _, _, files in os.walk(directory))
        processed_files = 0

        for root, dirs, files in os.walk(directory):
            # Skip specified directories
            if any(skip_dir in root.lower() for skip_dir in skip_dirs):
                continue

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

    def move_files_to_destination(self):
        with open("FoundFiles.txt", 'r') as f:
            file_list = [line.strip() for line in f.readlines()]
        move_files(file_list, self.move_destination.get())
        messagebox.showinfo("Move Complete", f"Moved {len(file_list)} files to {self.move_destination.get()}")

    def delete_files(self):
        with open("FoundFiles.txt", 'r') as f:
            file_list = [line.strip() for line in f.readlines()]
        delete_files(file_list)
        messagebox.showinfo("Deletion Complete", f"Deleted {len(file_list)} files")

    def open_latest_release(self):
        webbrowser.open("https://github.com/VVoiddd/Simple-File-Scanner")

def main():
    root = TkinterDnD.Tk()
    app = SimpleFileScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
