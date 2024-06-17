import os
import logging
from shared_utils import get_core_windows_dirs

def delete_files(file_list):
    """
    Delete files from the provided list.

    Parameters:
    file_list (list): List of file paths to delete.
    """
    core_windows_dirs = get_core_windows_dirs()

    for file_path in file_list:
        # Skip files in core Windows directories
        if any(file_path.startswith(core_dir) for core_dir in core_windows_dirs):
            logging.warning(f"Skipped (core system file): {file_path}")
            continue
        
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.info(f"Deleted file: {file_path}")
            else:
                logging.warning(f"File does not exist: {file_path}")
        except Exception as e:
            logging.error(f"Failed to delete file {file_path}", exc_info=True)
