from ctypes import *
from defines import *
import sys

kernel32=windll.kernel32

class fuzzing:
    #[O]PID 얻기
    #   - [O] 프로세스 목록 얻기 : get_process_id )
    #   - [O] 원하는 프로세스 열기 : open_process

    #[_]PID에 해당하는 메모리 정보, 레지스터 정보 얻기
    #   - [_] 메모리 접근
    #   - [_] 레지스터 접근 (특히 eip)
    def __init__(self):
        self.pid=0
        self.err= lambda msg: sys.stderr.write("ERROR: "+msg+"\n")


    def get_process_id(self):
        pe           = PROCESSENTRY32()
        process_list = []
        snapshot     = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
         #args: TH32CS_SNAPPROCESS : 모든 프로세스를 snapshot, 0을 매개변수로 전달 시, 현재 실행중인 모든 프로세스를 스냅한다.
        if snapshot == INVALID_HANDLE_VALUE:
            self.err("CreateToolhelp32Snapshot returns INVALID_HANDLE_VALUE :: get_process_id()")

        # we *must* set the size of the structure prior to using it, otherwise Process32First() will fail.
        pe.dwSize = sizeof(PROCESSENTRY32)

        running_procs = kernel32.Process32First(snapshot, byref(pe))
        #Retrieves information about the first process encountered in a system snapshot.
        #args: CreateToolhelp32Snapshot() 함수로부터 리턴되는 핸들, PROCESSENTRY32 구초제의 주소. byref()는 포인터 반환

        while running_procs:
            process_list.append((pe.th32ProcessID, pe.szExeFile))
            running_procs = kernel32.Process32Next(snapshot, byref(pe))

        kernel32.CloseHandle(snapshot)
        return process_list
        # (pid,name) => name으로 원하는 process 찾기 가능할 거 같다.
    def open_process(self,pid):
        self.target_process=kernel32.OpenProcess(PROCESS_ALL_ACCESS,False,pid)
        #If the function succeeds, the return value is an open handle to the specified process.
        #If the function fails, the return value is NULL. To get extended error information, call GetLastError.
        if not self.target_process:
            self.err("target_process is NULL :: open_process()")
        return self.target_process
        





