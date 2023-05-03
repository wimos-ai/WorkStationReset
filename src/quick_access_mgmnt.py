import os
from folder_mgmnt import clear_folder
from typing import Final, Any

APP_DATA_PATH: Final[str] = os.getenv("AppData")
QUICK_ACCESS_LINK_PATH = APP_DATA_PATH + r"\Microsoft\Windows\Recent"
"""Information extrapolated from https://winaero.com/reset-quick-access-pinned-folders-in-windows-10/"""
def clear_quick_access()->None:
    clear_folder(QUICK_ACCESS_LINK_PATH)
