import os
import sys
import time
import threading
import ctypes
import ttkbootstrap as ttk
from tkinter import filedialog, StringVar, BooleanVar, DoubleVar
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter.messagebox as messagebox
from MoveFiles import move_files
from FileRemover import delete_files
from concurrent.futures import ThreadPoolExecutor

class SimpleFileScanner:
    GITHUB_URL = "https://github.com/VVoiddd/Simple-File-Scanner"

    def __init__(self, root):
        self.root = root
        self.root.style = ttk.Style('darkly')
        self.root.configure(background='#1a1a1a')  # Dark background
        self.root.resizable(False, False)
        self.request_admin_access()  # Ensure admin access

        # Initialize Variables
        self.init_variables()

        # Initialize UI
        self.create_ui()

    def init_variables(self):
        """Initialize the variables used in the UI and functionality."""
        self.folder_path = StringVar()
        self.days_unused = StringVar(value="30")
        self.move_destination = StringVar()
        self.progress = DoubleVar()

        # Skip options
        self.skip_steam = BooleanVar(value=True)
        self.skip_microsoft_store = BooleanVar(value=True)
        self.skip_xbox = BooleanVar(value=True)
        self.skip_discord = BooleanVar(value=True)
        self.skip_ubisoft = BooleanVar(value=True)
        self.skip_other_games = BooleanVar(value=True)

    def create_ui(self):
        """Create the user interface components."""
        self.root.title(f"Simple File Scanner (SFS) |-| Version: 1.0.3")

        ttk.Label(self.root, text="Simple File Scanner (SFS)", font=('Helvetica', 18, 'bold'), foreground='purple').pack(pady=20)

        self.create_folder_selection()
        self.create_days_input()
        self.create_move_destination()
        self.create_skip_options()
        self.create_progress_bar()
        self.create_buttons()

    def create_folder_selection(self):
        """Create folder selection UI."""
        folder_frame = ttk.Frame(self.root, padding=10)
        folder_frame.pack(fill='x')

        ttk.Label(folder_frame, text="Select Folder:", foreground='purple').pack(side='left')
        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=40, state='readonly')
        folder_entry.pack(side='left', padx=5)

        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side='left')
        folder_entry.drop_target_register(DND_FILES)
        folder_entry.dnd_bind('<<Drop>>', self.drop_folder)

    def create_days_input(self):
        """Create the input for specifying days unused."""
        days_frame = ttk.Frame(self.root, padding=10)
        days_frame.pack(fill='x')

        ttk.Label(days_frame, text="Days Unused:", foreground='purple').pack(side='left')
        ttk.Entry(days_frame, textvariable=self.days_unused, width=5).pack(side='left', padx=5)

    def create_move_destination(self):
        """Create the UI for move destination selection."""
        move_frame = ttk.Frame(self.root, padding=10)
        move_frame.pack(fill='x')

        ttk.Label(move_frame, text="Move Destination:", foreground='purple').pack(side='left')
        move_entry = ttk.Entry(move_frame, textvariable=self.move_destination, width=40, state='readonly')
        move_entry.pack(side='left', padx=5)

        ttk.Button(move_frame, text="Browse", command=self.browse_move_folder).pack(side='left')

    def create_skip_options(self):
        """Create checkboxes to allow skipping specific directories."""
        skip_frame = ttk.Frame(self.root, padding=10)
        skip_frame.pack(fill='x')

        ttk.Label(skip_frame, text="Skip Directories:", foreground='purple').pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Steam", variable=self.skip_steam).pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Microsoft Store", variable=self.skip_microsoft_store).pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Xbox", variable=self.skip_xbox).pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Discord", variable=self.skip_discord).pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Ubisoft", variable=self.skip_ubisoft).pack(anchor='w')
        ttk.Checkbutton(skip_frame, text="Other Game Stores (Epic Games, Origin, etc.)", variable=self.skip_other_games).pack(anchor='w')

    def create_progress_bar(self):
        """Create the progress bar to show scan progress."""
        self.progress_bar = ttk.Progressbar(self.root, variable=self.progress, maximum=100, length=300)
        self.progress_bar.pack(pady=10)

    def create_buttons(self):
        """Create buttons for scan, move, and delete functionalities."""        
        ttk.Button(self.root, text="Scan", command=self.scan_files_thread).pack(pady=10)
        ttk.Button(self.root, text="Move Files", command=self.move_files_thread).pack(pady=5)
        ttk.Button(self.root, text="Delete Files", command=self.delete_files_thread).pack(pady=5)

    def browse_folder(self):
        """Open folder dialog to select a folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def drop_folder(self, event):
        """Handle folder drag and drop."""
        self.folder_path.set(event.data)

    def browse_move_folder(self):
        """Open folder dialog to select a destination folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.move_destination.set(folder_selected)

    def scan_files(self):
        """Scan files for unused files based on the specified criteria."""
        directory = self.folder_path.get()
        if not directory:
            messagebox.showerror("Error", "Please select a folder to scan.")
            return

        try:
            days_unused = int(self.days_unused.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of days.")
            return

        unused_files = self.get_unused_files(directory, days_unused)
        if unused_files:
            self.write_to_file(unused_files)
            messagebox.showinfo("Scan Complete", f"Found {len(unused_files)} unused files.")
        else:
            messagebox.showinfo("Scan Complete", "No unused files found.")
        self.progress.set(0)

    def get_unused_files(self, directory, days_unused):
        """Get a list of files that haven't been accessed within the specified days."""
        skip_dirs = self.get_skip_directories()
        current_time = time.time()
        cutoff_time = current_time - (days_unused * 86400)

        unused_files = []
        total_files = sum([len(files) for _, _, files in os.walk(directory)])
        scanned_files = 0

        def scan_file(file, root):
            file_path = os.path.join(root, file)
            try:
                if os.path.getatime(file_path) < cutoff_time:
                    unused_files.append(file_path)
            except Exception as e:
                print(f"Error with file {file_path}: {e}")

            nonlocal scanned_files
            scanned_files += 1
            self.progress.set((scanned_files / total_files) * 100)
            self.root.update_idletasks()

        with ThreadPoolExecutor() as executor:
            for root, dirs, files in os.walk(directory):
                dirs[:] = [d for d in dirs if not any(skip.lower() in d.lower() for skip in skip_dirs)]
                for file in files:
                    executor.submit(scan_file, file, root)

        return unused_files

    def write_to_file(self, file_list):
        """Write the list of found files to a file using UTF-8 encoding."""
        with open("FoundFiles.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(file_list))

    def move_files(self):
        """Move files to the specified destination."""        
        try:
            if not self.move_destination.get():
                messagebox.showerror("Error", "Please select a move destination folder.")
                return
            move_files("FoundFiles.txt", self.move_destination.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_files(self):
        """Delete files listed in the FoundFiles.txt."""        
        try:
            with open("FoundFiles.txt", "r", encoding="utf-8") as f:
                files = f.read().splitlines()

            for file in files:
                if os.path.exists(file):
                    os.remove(file)
                else:
                    print(f"File does not exist: {file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete files: {e}")

    def scan_files_thread(self):
        """Start file scan in a separate thread."""
        threading.Thread(target=self.scan_files).start()

    def move_files_thread(self):
        """Start file move in a separate thread."""
        threading.Thread(target=self.move_files).start()

    def delete_files_thread(self):
        """Start file deletion in a separate thread."""
        threading.Thread(target=self.delete_files).start()

    def request_admin_access(self):
        """Request administrative privileges if not already running with them."""
        try:
            is_admin = os.getuid() == 0  # Check if the current user is root (Linux/Mac)
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()  # Check for Windows

        if not is_admin:
            if messagebox.askyesno("Admin Access Required", "This application requires administrative access. Would you like to restart it with admin privileges?"):
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None)
                sys.exit()

    def get_skip_directories(self):
        """Get the directories to skip based on user selections."""
        skip_dirs = []
        if self.skip_steam.get():
            skip_dirs.append("Steam")
        if self.skip_microsoft_store.get():
            skip_dirs.append("Microsoft Store")
        if self.skip_xbox.get():
            skip_dirs.append("Xbox")
        if self.skip_discord.get():
            skip_dirs.append("Discord")
        if self.skip_ubisoft.get():
            skip_dirs.append("Ubisoft")
        if self.skip_other_games.get():
            skip_dirs.append("Other Game Stores")

        return skip_dirs

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = SimpleFileScanner(root)
    root.mainloop()
