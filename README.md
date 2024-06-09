# Simple File Scanner (SFS)

Simple File Scanner (SFS) is a Python application designed to scan a directory for unused files that have not been accessed within a specified number of days. The application features a modern, dark-themed graphical user interface (GUI) built with `ttkbootstrap`.

## Features

- Scan a selected directory for unused files.
- Option to skip directories related to gaming (e.g., Steam, Microsoft Store, Xbox, etc.).
- Displays a progress bar during the scan.
- Generates a list of unused files in `FoundFiles.txt`.
- Provides a link to the latest release.

## Installation

### Prerequisites

- Python 3.6 or higher

### Steps

1. Clone this repository or download the ZIP file and extract it.
2. Navigate to the project directory.
3. Install the required packages by running the `install.bat` script.

### Using the Install Script

To install the required dependencies, you can use the provided `install.bat` file.

```bat
@echo off
echo Installing required packages...
pip install -r requirements.txt
echo Installation complete. You can now run the application with 'python SFS.py'.
pause
