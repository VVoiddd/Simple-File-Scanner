import os
import shutil
import logging
from concurrent.futures import ThreadPoolExecutor

def move_file(file_path, destination_folder):
    """Move a single file to the destination folder."""
    try:
        if os.path.isfile(file_path):
            destination_path = os.path.join(destination_folder, os.path.basename(file_path))
            shutil.move(file_path, destination_path)
            logging.info(f"Moved file {file_path} to {destination_path}")
        else:
            logging.warning(f"File does not exist or is not a file: {file_path}")
    except shutil.Error as e:
        logging.error(f"Failed to move file {file_path}. {str(e)}")
    except OSError as e:
        logging.error(f"OS error occurred while moving file {file_path}. {str(e)}")

def move_files(file_list, destination_folder):
    """Move files from the provided list to the destination folder using threads."""
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        logging.info(f"Created destination folder: {destination_folder}")

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for file_path in file_list:
            executor.submit(move_file, file_path, destination_folder)
