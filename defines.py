from ctypes import *

# Thread constants for CreateToolhelp32Snapshot()
TH32CS_SNAPPROCESS  = 0x00000002

INT = c_int
CHAR = c_char
BYTE = c_ubyte
WORD = c_ushort
DWORD = c_ulong
LPBYTE = POINTER(c_ubyte)
LPTSTR = POINTER(c_char)
HANDLE = c_void_p
PVOID = c_void_p
LPVOID = c_void_p
UINT_PTR = c_ulong
SIZE_T = c_ulong

class PROCESSENTRY32(Structure):
    _fields_ = [
        ('dwSize',              DWORD),
        ('th32ProcessID',       DWORD),
        ('szExeFile',           CHAR * 260)
    ]

INVALID_HANDLE_VALUE=0xFFFFFFFF
PROCESS_ALL_ACCESS = 0x001F0FFF

CREATE_BREAKAWAY_FROM_JOB=0x01000000
CREATE_DEFAULT_ERROR_MODE=0x04000000
CREATE_NEW_CONSOLE=0x00000010
CREATE_NEW_PROCESS_GROUP=0x00000200
CREATE_NO_WINDOW=0x08000000
CREATE_PROTECTED_PROCESS=0x00040000
CREATE_PRESERVE_CODE_AUTHZ_LEVEL=0x02000000
CREATE_SECURE_PROCESS=0x00400000
CREATE_SEPARATE_WOW_VDM=0x00000800
CREATE_SHARED_WOW_VDM=0x00001000
CREATE_SUSPENDED=0x00000004
CREATE_UNICODE_ENVIRONMENT=0x00000400
DEBUG_ONLY_THIS_PROCESS=0x00000002
DEBUG_PROCESS=0x00000001
DETACHED_PROCESS=0x00000008
EXTENDED_STARTUPINFO_PRESENT=0x00080000
INHERIT_PARENT_AFFINITY=0x00010000
WAIT_FAILED=0xFFFFFFFF

## for CreateProcessA() function
# STARTUPINFO describes how to spawn the process
class STARTUPINFO(Structure):
    _fields_ = [
        ("cb", DWORD),
        ("lpReserved", LPTSTR),
        ("lpDesktop", LPTSTR),
        ("lpTitle", LPTSTR),
        ("dwX", DWORD),
        ("dwY", DWORD),
        ("dwXSize", DWORD),
        ("dwYSize", DWORD),
        ("dwXCountChars", DWORD),
        ("dwYCountChars", DWORD),
        ("dwFillAttribute", DWORD),
        ("dwFlags", DWORD),
        ("wShowWindow", WORD),
        ("cbReserved2", WORD),
        ("lpReserved2", LPBYTE),
        ("hStdInput", HANDLE),
        ("hStdOutput", HANDLE),
        ("hStdError", HANDLE),
    ]

# PROCESS_INFORMATION receives its information
## after the target process has been successfully
# started.
class PROCESS_INFORMATION(Structure):
    _fields_ = [
        ("hProcess", HANDLE),
        ("hThread", HANDLE),
        ("dwProcessId", DWORD),
        ("dwThreadId", DWORD),
    ]