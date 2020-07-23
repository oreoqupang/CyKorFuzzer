from ctypes import *
from defines import *
import sys
import os
import signal
import subprocess
import win32.lib.win32con as win32con
import win32event

kernel32=windll.kernel32

class fuzzing:
    #[O]PID 얻기
    #   - [O] 프로세스 목록 얻기 : get_process_id 
    #   - [O] 원하는 프로세스 열기 : open_process

    #[_]PID에 해당하는 메모리 정보, 레지스터 정보 얻기
    #   - [_] 메모리 접근
    #   - [_] 레지스터 접근 (특히 eip)

    #[_]지정한 바이너리에 INPUT 넣고 crash 나는지 안 나는지 확인
    #   - [_] 지정한 바이너리에 INPUT 넣기 - run_with_input()(subprocess.popen) 이용
    #   - [_] SIGNAL 받아서 검사하기  - signal.signal() 이용
    def __init__(self):
        self.shell = False,
        self.timeout = 0.2,
        self.h_Process=None
        self.pid=None
        self.err= lambda msg: sys.stderr.write("ERROR: "+msg+"\n")
        self.startupinfo=STARTUPINFO()
        self.process_information=PROCESS_INFORMATION()

    def get_process_id(self):
        pe           = PROCESSENTRY32()
        process_list = []
        snapshot     = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
         #args: TH32CS_SNAPPROCESS : 모든 프로세스를 snapshot, 0을 매개변수로 전달 시, 현재 실행중인 모든 프로세스를 스냅한다.
        if snapshot == INVALID_HANDLE_VALUE:
            self.err("CreateToolhelp32Snapshot returns INVALID_HANDLE_VALUE :: get_process_id()")
            raise ValueError

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

    # 질문할 거 많은 애
    # 1. 자식 프로세스를 열어서 걔한테 stdin으로 입력을 주려면 어케해야 하는지
    #   - 자식 프로세스로 여는 애가 gets()로 입력 받는 애
    #   - 핸들을 받아서 프로세스를 제어하려고 kernel32.CreateProcessW()를 쓴건데
    #     subprocess.Popen() 후 communicate가 stdin 으로 넣기 젤 편한거 같음.
    #   - windows에서 subprocess.Popen()는 CreateProcess()를 쓴다고 함.
    #   - 그러면 핸들은 어케 받누? 
    def run_with_input(self,path_to_exe, input_data, commandLine=None):
        path_to_exe=os.path.abspath(path_to_exe)
        #input_data=input("Input: ") # 
        creationFlags=DEBUG_PROCESS

        self.startupinfo.dwFlags=0x1
        self.startupinfo.wShowWindow=0x5 
        self.startupinfo.cb=sizeof(self.startupinfo)
        if kernel32.CreateProcessW(path_to_exe,
                                        commandLine,
                                        None,
                                        None,
                                        None,
                                        creationFlags,
                                        None,
                                        None,
                                        byref(self.startupinfo),
                                        byref(self.process_information)
                                        ):

            self.pid=self.process_information.dwProcessId
            print("[*] Successfully launched the process.")
            print("[*] PID: %d" %self.pid)
            self.h_Process=self.open_process(self.process_information.dwProcessId)
        else:
            print ("[*] Error: 0x%08x" %kernel32.GetLastError())

        process = subprocess.Popen(path_to_exe, shell=self.shell, stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            close_fds=True)
        
        try:
            process.communicate(input=input_data, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            raise TimeoutError("Timeout.")

    # 종료시점의 종료 상태를 반환하는 애 이용해서 상태 점검
    def checkProcessStatus(self):
        i=INT(0)
        pi=pointer(i)
        # GetExitCodeProcess : Retrieves the termination status of the specified process.
        if kernel32.GetExitCodeProcess(self.h_Process,pi)==0:
            print ("[*] Error: GetExitCodeProcess--- %d" %kernel32.GetLastError())
            return False
        else:
            # 259 = STILL_ACTIVE
            if pi == win32con.STILL_ACTIVE:
                print ("[*] Process is not done.")
                return win32con.STILL_ACTIVE
            else:
                return False
    def stopProcess(self):
        pi=self.h_Process
        #Check if handle is invalid
        if(pi == None):
            print ("Process handle invalid. possibly already closed")
            return False
        #Terminate Process
        if(kernel32.TerminateProcess(pi,1)==0):
            print("ExitPorcess failed %d" %kernel32.GetLastError())
            return False
        #Wait until child process exits.
        if(kernel32.WaitForSingleObject( pi.hProcess, win32event.INFINITE ) == WAIT_FAILED):
            print("Wait for exit process failed: %d" %kernel32.GetLastError())
            return False
        
        #Close process
        if (kernel32.CloseHandle(pi)==0):
            print("Cannot close process handle %d" %kernel32.GetLastError())
            return False
        else:
            pi=None
        return True
