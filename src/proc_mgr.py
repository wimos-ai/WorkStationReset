import ctypes
from typing import Final, Any
from enum import IntEnum
import os
from itertools import filterfalse
from ctypes.wintypes import LPARAM, WPARAM, HANDLE, DWORD, BOOL, HWND, UINT, HMODULE, LPSTR, MAX_PATH   

kernal32Lib: Final[ctypes.WinDLL] = ctypes.WinDLL("Kernel32")
psapiLib: Final[ctypes.WinDLL] = ctypes.WinDLL("Psapi.dll")
user32Lib: Final[ctypes.WinDLL] = ctypes.windll.user32

# See: https://learn.microsoft.com/en-us/previous-versions/windows/desktop/legacy/ms633498(v=vs.85)
WNDENUMPROC: Final[type] = ctypes.WINFUNCTYPE(BOOL, HWND,LPARAM)
DWORD_ARRAY_10K = DWORD * 10000

def load_func(dlls: ctypes.WinDLL | list[ctypes.WinDLL], identifier: str, args: list, return_type: Any) -> ctypes.WINFUNCTYPE:
    """Searches the provided DLL(s) for the given function, and loads it"""
    dll = None
    if hasattr(dlls, '__iter__'):
        for dll_i in dlls:
            if hasattr(dll_i, identifier):
                dll = dll_i
                break
    else:
        dll = dlls

    func  = getattr(dll, identifier)
    func.argtypes = args
    func.restype = return_type
    return func

class Process_Security_And_Access_Rights(IntEnum):
    DELETE = 0x00010000
    READ_CONTROL = 0x00020000
    SYNCHRONIZE = 0x00100000
    WRITE_DAC = 0x00040000

    PROCESS_CREATE_PROCESS = 0x0080
    PROCESS_CREATE_THREAD = 0x0002
    PROCESS_DUP_HANDLE = 0x0040
    PROCESS_QUERY_INFORMATION = 0x0400
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    PROCESS_SET_INFORMATION  = 0x0200
    PROCESS_SET_QUOTA = 0x0100
    PROCESS_SUSPEND_RESUME  = 0x0800
    PROCESS_TERMINATE = 0x0001 # See  https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess
    PROCESS_VM_OPERATION = 0x0008
    PROCESS_VM_READ = 0x0010
    PROCESS_VM_WRITE  = 0x0020
    
OpenProcess = load_func(kernal32Lib, "OpenProcess",[DWORD, BOOL,DWORD], HANDLE)
GetWindowThreadProcessId = load_func(user32Lib, "GetWindowThreadProcessId", [HWND, ctypes.POINTER(DWORD)], DWORD)
IsWindowVisible = load_func(user32Lib, "IsWindowVisible", [HWND], BOOL)
IsIconic = load_func(user32Lib, "IsIconic", [HWND], BOOL)
EnumWindows = load_func(user32Lib, "EnumWindows", [WNDENUMPROC, LPARAM], BOOL )
GetCurrentProcessId = load_func(kernal32Lib, "GetCurrentProcessId", [], DWORD )
TerminateProcess = load_func(kernal32Lib, "TerminateProcess", [HANDLE, UINT], BOOL)
CloseHandle  = load_func(kernal32Lib, "CloseHandle", [HANDLE], BOOL)
GetModuleFileNameExA = load_func([kernal32Lib,psapiLib], "GetModuleFileNameExA", [HANDLE, HMODULE, LPSTR, DWORD], BOOL)
IsProcessCritical  = load_func(kernal32Lib, "IsProcessCritical", [HANDLE, ctypes.POINTER(BOOL)], BOOL)
SendMessage = load_func(user32Lib, "SendMessageA", [HWND, UINT, WPARAM , LPARAM], ctypes.POINTER(ctypes.c_long))

@WNDENUMPROC
def c_get_processes_with_windows_cb(hwnd, lparam)->BOOL:
    """We need to get the PID attached to the HWND, then append it to the array in lparam"""
    if IsWindowVisible(hwnd) or IsIconic(hwnd):
        # Extract the DWORD pointer from the lparam
        void_ptr = ctypes.c_void_p(lparam)
        array_of_proc_IDs = ctypes.cast(void_ptr, ctypes.POINTER(DWORD))
        # Make Call
        pid = DWORD(0)
        thdID = GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if thdID != 0:
            array_of_proc_IDs[array_of_proc_IDs[0]] = pid
            array_of_proc_IDs[0] = array_of_proc_IDs[0] + 1
    return 1
        

def get_processes_with_windows()->list[int]:
    array_of_proc_IDs = DWORD_ARRAY_10K()
    # The first element in this array will be the index of the next empty spot
    array_of_proc_IDs[0] = 1

    #Now cram &array_of_proc_IDs[0] into an LPARAM
    ptr = ctypes.cast(array_of_proc_IDs, ctypes.c_void_p)
    lparam = LPARAM(ptr.value)
    
    #Make call
    if EnumWindows(c_get_processes_with_windows_cb, lparam.value) == 0:
        raise OSError("EnumWindows failed")

    return list({array_of_proc_IDs[x] for x in range(1,array_of_proc_IDs[0])})

def open_processes(process_identifiers: list[int]) -> list[HANDLE]:
    par = Process_Security_And_Access_Rights
    handles: list[HANDLE] = []
    desired_access: DWORD = DWORD(par.PROCESS_TERMINATE + par.PROCESS_QUERY_INFORMATION + par.PROCESS_VM_READ)
    for pid in process_identifiers:
        handle = OpenProcess(desired_access, BOOL(0),DWORD(pid))
        if handle:
            handles.append(handle)
    return handles
    
def kill_processes_from_handles(handles: list[HANDLE]) -> None:
    for handle in handles:
        TerminateProcess(handle,0)

def close_handles(handles: list[HANDLE]) -> None:
    for handle in handles:
        CloseHandle(handle)
        
def get_proc_name_from_handle(handle:HANDLE) -> str:
    bts = bytes(MAX_PATH)
    if GetModuleFileNameExA(handle, None,bts, MAX_PATH) == 0:
        raise OSError("GetModuleFileNameExA failed")
    return bts.decode("ASCII").strip('\0')

def is_process_critical(handle: HANDLE)-> bool:
    my_bool = BOOL(0)
    if IsProcessCritical(handle, ctypes.byref(my_bool)) == 0:
        raise OSError("IsProcessCritical failed")
    return bool(my_bool)

def kill_windowed_processes(whitelisted_names: list[str] = ["py.exe","pythonw.exe","explorer.exe"])->None:
    """See: https://stackoverflow.com/questions/28406832/detect-if-external-process-is-interactive-and-has-any-visible-ui
       And: https://devblogs.microsoft.com/oldnewthing/20171219-00/?p=97606
       And: https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-enumprocesses

       The general idea is to loop over all processes and to kill any that have an active window and are not marked as critical and are not VI's
    """
    # Get processes with open windows
    canidate_list = get_processes_with_windows()

    # If we are a canidate for termination, avoid killing ourselves
    if GetCurrentProcessId() in canidate_list: 
        canidate_list.remove(GetCurrentProcessId())

    # Open handles to all processes
    handles = open_processes(canidate_list)

    # Remove citical processes from canidates list
    def citical_processes_filter(handle: HANDLE)-> bool:
        if is_process_critical(handle):
            CloseHandle(handle)
            return False
        return True
    handles = [h for h in handles if citical_processes_filter(h)]
            
    # Remove white listed names from  canidates list
    def white_list_filter(handle: HANDLE)-> bool:
        if os.path.basename(get_proc_name_from_handle(handle)) in whitelisted_names:
            CloseHandle(handle)
            return False
        return True
    handles = [h for h in handles if white_list_filter(h)]

    
    print("Killing:")
    for handle in handles:
        print(os.path.basename(get_proc_name_from_handle(handle)))

    kill_processes_from_handles(handles)
    close_handles(handles)
