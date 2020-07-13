from ctypes import *
TH32CS_SNAPPROCESS  = 0x00000002
PROCESS_ALL_ACCESS = 0x001F0FFF
INVALID_HANDLE_VALUE = 0xFFFFFFFF
DWORD=c_ulong
CHAR=c_char

class PROCESSENTRY32(Structure):
    _fields_ = [
        ('dwSize',              DWORD),
        ('th32ProcessID',       DWORD),
        ('szExeFile',           CHAR * 260)
    ]