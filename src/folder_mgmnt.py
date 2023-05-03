import os
import ctypes
import shutil
from typing import Final, Any

def clear_folder(folder:str):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

Downloads_path: Final[str] = os.getenv('USERPROFILE') + r"\Downloads"
def clear_downloads()->None:
    clear_folder(Downloads_path)

Documents_path: Final[str] = os.getenv('USERPROFILE') + r"\Documents"
def clear_documents()->None:
    clear_folder(Documents_path)

