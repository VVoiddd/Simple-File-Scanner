import os
from shared_utils import get_core_windows_dirs

def delete_files(file_list):
    core_windows_dirs = get_core_windows_dirs()

    for file in file_list:
        # Skip files in core Windows directories
        if any(file.startswith(core_dir) for core_dir in core_windows_dirs):
            print(f"Skipped (core system file): {file}")
            continue
        
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Failed to delete {file}: {e}")
