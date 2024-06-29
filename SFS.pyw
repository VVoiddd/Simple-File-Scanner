import os
import time
import sys
import threading
import webbrowser
import ctypes
import requests
import zipfile
import shutil
import tempfile
import ttkbootstrap as ttk
from tkinter import filedialog, StringVar, BooleanVar
from ttkbootstrap.constants import *
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter.messagebox as messagebox
from MoveFiles import move_files
from FileRemover import delete_files
from shared_utils import get_core_windows_dirs

class SimpleFileScanner:
    # Define the URL to your version file and latest release ZIP
    VERSION_URL = "https://raw.githubusercontent.com/VVoiddd/Simple-File-Scanner/main/version.txt"
    LATEST_RELEASE_URL = "https://github.com/VVoiddd/Simple-File-Scanner/archive/refs/heads/main.zip"

    def __init__(self, root):
        self.root = root
        self.root.title("Simple File Scanner (SFS)")
        self.root.geometry("600x650")
        self.root.style = ttk.Style('darkly')
        self.root.resizable(False, False)  # Disable window resizing

        # Request administrative privileges
        self.request_admin_access()

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
        self.check_for_updates()  # Check for updates when the app starts

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
        ttk.Button(self.root, text="Scan", command=self.scan_files_thread, style="success.TButton").pack(pady=10)

        # Move and Delete Buttons
        ttk.Button(self.root, text="Move Files", command=self.move_files_to_destination_thread, style="success.TButton").pack(pady=5)
        ttk.Button(self.root, text="Delete Files", command=self.delete_files_thread, style="danger.TButton").pack(pady=5)

        # Latest Release Button
        ttk.Button(self.root, text="Check Latest Release", command=self.open_latest_release, style="info.TButton").pack(pady=20)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def drop_folder(self, event):
        self.folder_path.set(event.data)

    def browse_move_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.move_destination.set(folder_selected)

    def scan_files(self):
        directory = self.folder_path.get()
        if not directory:
            messagebox.showerror("Error", "Please select a folder to scan.")
            return

        try:
            days_unused = int(self.days_unused.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of days.")
            return

        # Start scanning
        unused_files = self.get_unused_files(directory, days_unused)
        if unused_files:
            self.write_to_file(unused_files)
            messagebox.showinfo("Scan Complete", f"Scan complete. Found {len(unused_files)} unused files.")
        else:
            messagebox.showinfo("Scan Complete", "No unused files found.")

    def get_unused_files(self, directory, days_unused):
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
            skip_dirs.update(['epic games', 'origin', 'gog galaxy', 'battle.net'])

        current_time = time.time()
        cutoff_time = current_time - (days_unused * 86400)

        unused_files = []
        for root, dirs, files in os.walk(directory):
            for skip_dir in skip_dirs:
                dirs[:] = [d for d in dirs if skip_dir.lower() not in d.lower()]

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    last_access_time = os.path.getatime(file_path)
                    if last_access_time < cutoff_time:
                        unused_files.append(file_path)
                except Exception as e:
                    print(f"Error accessing file: {file_path}, {e}")

        return unused_files

    def write_to_file(self, file_list):
        with open("FoundFiles.txt", "w") as f:
            for file in file_list:
                f.write(f"{file}\n")

    def move_files_to_destination(self):
        try:
            if not self.move_destination.get():
                messagebox.showerror("Error", "Please select a move destination folder.")
                return
            move_files("FoundFiles.txt", self.move_destination.get())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_files(self):
        try:
            delete_files("FoundFiles.txt")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def scan_files_thread(self):
        thread = threading.Thread(target=self.scan_files)
        thread.start()

    def move_files_to_destination_thread(self):
        thread = threading.Thread(target=self.move_files_to_destination)
        thread.start()

    def delete_files_thread(self):
        thread = threading.Thread(target=self.delete_files)
        thread.start()

    def request_admin_access(self):
        try:
            is_admin = os.getuid() == 0
        except AttributeError:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if not is_admin:
            messagebox.showwarning("Warning", "This application requires administrative privileges. Please run as administrator.")
            self.root.quit()

    def open_latest_release(self):
        webbrowser.open("https://github.com/VVoiddd/Simple-File-Scanner/releases/latest")

    def get_current_version(self):
        # Read the local version from a file
        with open("version.txt", "r") as f:
            return f.read().strip()

    def check_for_updates(self):
        try:
            response = requests.get(self.VERSION_URL)
            if response.status_code == 200:
                latest_version = response.text.strip()
                current_version = self.get_current_version()
                if latest_version > current_version:
                    self.notify_update_available(latest_version)
            else:
                print("Failed to check for updates")
        except Exception as e:
            print(f"Error checking for updates: {e}")

    def notify_update_available(self, latest_version):
        result = messagebox.askyesno("Update Available", f"A new version ({latest_version}) is available. Do you want to download and install it?")
        if result:
            self.download_update(latest_version)

    def download_update(self, latest_version):
        try:
            # Create a temporary directory to store the downloaded ZIP file
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "latest_release.zip")

            # Download the latest release ZIP file
            response = requests.get(self.LATEST_RELEASE_URL)
            with open(zip_path, "wb") as f:
                f.write(response.content)

            # Extract the ZIP file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            # Find the extracted folder (assuming it matches the repository name)
            extracted_folder = os.path.join(temp_dir, "Simple-File-Scanner-main")

            # Replace old files with the new ones
            self.apply_update(extracted_folder)

            # Clean up the temporary directory
            shutil.rmtree(temp_dir)

            # Update the local version file
            with open("version.txt", "w") as f:
                f.write(latest_version)

            messagebox.showinfo("Update Complete", "The application has been updated to the latest version.")
        except Exception as e:
            messagebox.showerror("Update Failed", f"An error occurred while updating: {e}")

    def apply_update(self, extracted_folder):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        for item in os.listdir(extracted_folder):
            source = os.path.join(extracted_folder, item)
            destination = os.path.join(current_dir, item)
            if os.path.isdir(source):
                # Remove old directory and replace with the new one
                if os.path.exists(destination):
                    shutil.rmtree(destination)
                shutil.move(source, destination)
            else:
                # Replace old files with the new ones
                if os.path.exists(destination):
                    os.remove(destination)
                shutil.move(source, destination)

def main():
    root = TkinterDnD.Tk()
    app = SimpleFileScanner(root)
    app.check_for_updates()  # Check for updates when the app starts
    root.mainloop()

if __name__ == "__main__":
    main()