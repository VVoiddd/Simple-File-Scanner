#MoveFiles.py

import os
import shutil

def move_files(file_list, destination):
    if not os.path.exists(destination):
        os.makedirs(destination)

    for file in file_list:
        try:
            shutil.move(file, destination)
            print(f"Moved: {file}")
        except Exception as e:
            print(f"Failed to move {file}: {e}")
