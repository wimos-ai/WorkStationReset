import pyautogui
import pygetwindow
import os
import subprocess
from typing import Final, Any
import time

def wait_for_Settings_to_load()->None:
    while pyautogui.locateCenterOnScreen("ConectedToIAStateDomainBanner.png") is None:
        time.sleep(1)

def locate_microsoft_logo()-> tuple[int,int]:
    return pyautogui.locateCenterOnScreen("MicrosoftLogo.png")

def locate_disconnect_button()->tuple[int,int]|None:
    return pyautogui.locateCenterOnScreen("DisconnectButton.png")

def locate_yes_button()->tuple[int,int]|None:
    return pyautogui.locateCenterOnScreen("Yes.png")


def close_all_settings_windows()->None:
    subprocess.run(["taskkill", "/F", "/IM",  "SystemSettings.exe"], creationflags=subprocess.CREATE_NO_WINDOW)


def clear_work_school_accounts()->None:
    """I could not find an easy way to do this, so we will just go through a GUI
    See: https://4sysops.com/wiki/list-of-ms-settings-uri-commands-to-open-specific-settings-in-windows-10/

    """
    # Open settings to proper section
    close_all_settings_windows()
    os.system("start ms-settings:workplace")
    settings_window_hdl = pygetwindow.getWindowsWithTitle('Settings')[0] # It should be the only one open


    wait_for_Settings_to_load()
    
    while True:
        logo_location = locate_microsoft_logo()
        if logo_location is not None:
            pyautogui.click(logo_location)
            time.sleep(1)# Wait for settings to load
            button_location = locate_disconnect_button()
            if logo_location is not None:
                 pyautogui.click(button_location)
                 time.sleep(1)# Wait for settings to load
                 yes_location = locate_yes_button()
                 if logo_location is not None:
                     pyautogui.click(yes_location)
                     time.sleep(15)
        else:
            break

