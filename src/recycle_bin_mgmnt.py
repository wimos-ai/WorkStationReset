import ctypes
from typing import Final, Any

shellLib: Final[ctypes.WinDLL] = ctypes.WinDLL("Shell32")

HWND_NULL: Final[ctypes.c_int32] = ctypes.c_uint32(0)

SHERB_NOCONFIRMATION: Final[ctypes.c_int32] = ctypes.c_int32(0x1)
SHERB_NOPROGRESSUI: Final[ctypes.c_int32] = ctypes.c_int32(0x2)
SHERB_NOSOUND: Final[ctypes.c_int32] = ctypes.c_int32(0x4)

NULL_STRING: Final[bytes] = b""

def load_SHEmptyRecycleBinA() -> ctypes.WINFUNCTYPE:
    SHEmptyRecycleBinA = shellLib.SHEmptyRecycleBinA
    SHEmptyRecycleBinA.argtypes = [ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32]
    SHEmptyRecycleBinA.restype = ctypes.HRESULT
    return SHEmptyRecycleBinA

SHEmptyRecycleBinA: Final[ctypes.WINFUNCTYPE] = load_SHEmptyRecycleBinA()

class SHQUERYRBINFO(ctypes.Structure):
    """ creates a struct to match SHQUERYRBINFO """

    _fields_ = [('cbSize', ctypes.c_uint32),
                ('i64Size', ctypes.c_int64),
                ('i64NumItems', ctypes.c_int64)]

def load_SHQueryRecycleBinA() -> ctypes.WINFUNCTYPE:
    SHQueryRecycleBinA = shellLib.SHQueryRecycleBinA
    SHQueryRecycleBinA.argtypes = [ctypes.c_char_p, ctypes.POINTER(SHQUERYRBINFO)]
    SHQueryRecycleBinA.restype = ctypes.HRESULT
    return SHQueryRecycleBinA

SHQueryRecycleBinA = load_SHQueryRecycleBinA()




def get_recycle_bin_info()-> dict:
    info_struct = SHQUERYRBINFO()
    info_struct.cbSize = ctypes.c_uint32(ctypes.sizeof(SHQUERYRBINFO))
    info_struct.i64Size = 0
    info_struct.i64NumItems = 0

    SHQueryRecycleBinA(NULL_STRING, ctypes.byref(info_struct))

    return {"size_bytes": int(info_struct.i64Size),
            "num_items": int(info_struct.i64NumItems)}


def clear_recycle_bin()->None:
    """see https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shemptyrecyclebina"""
    flags = ctypes.c_uint32(SHERB_NOCONFIRMATION.value + SHERB_NOPROGRESSUI.value + SHERB_NOSOUND.value)

    if  get_recycle_bin_info()["num_items"] > 0:
        SHEmptyRecycleBinA(HWND_NULL,NULL_STRING,flags)

clear_recycle_bin()
