import os
import logging
from shared_utils import get_core_windows_dirs
from concurrent.futures import ThreadPoolExecutor

def delete_file(file_path):
    """Delete a single file."""
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            logging.info(f"Deleted file: {file_path}")
        else:
            logging.warning(f"Not a file or does not exist: {file_path}")
    except FileNotFoundError:
        logging.warning(f"File not found during deletion attempt: {file_path}")
    except PermissionError:
        logging.error(f"Permission denied while trying to delete file: {file_path}")
    except Exception as e:
        logging.error(f"Failed to delete file {file_path}. Error: {str(e)}", exc_info=True)

def delete_files(file_list):
    """Delete files from the provided list using threads."""
    core_windows_dirs = get_core_windows_dirs()

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for file_path in file_list:
            if any(os.path.abspath(file_path).startswith(core_dir) for core_dir in core_windows_dirs):
                logging.warning(f"Skipped (core system file): {file_path}")
                continue
            
            executor.submit(delete_file, file_path)
