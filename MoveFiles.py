import os
import shutil
import logging

def move_files(file_list, destination_folder):
    """
    Move files from the provided list to the destination folder.

    Parameters:
    file_list (list): List of file paths to move.
    destination_folder (str): The folder where files will be moved.
    """
    try:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            logging.info(f"Created destination folder: {destination_folder}")

        for file_path in file_list:
            if os.path.isfile(file_path):
                try:
                    destination_path = os.path.join(destination_folder, os.path.basename(file_path))
                    shutil.move(file_path, destination_path)
                    logging.info(f"Moved file {file_path} to {destination_path}")
                except shutil.Error as e:
                    logging.error(f"Failed to move file {file_path}. {str(e)}")
                except OSError as e:
                    logging.error(f"OS error occurred while moving file {file_path}. {str(e)}")
            else:
                logging.warning(f"File does not exist or is not a file: {file_path}")
    except Exception as e:
        logging.error("An unexpected error occurred while moving files", exc_info=True)

