import subprocess
import signal
import enum
import ptrace.debugger

class RunStatus(enum.Enum):
    PASS=1
    CRASH=2
    USER_CRASH=3
    EXCEPT=4

class Runner(object):
    def __init__(self, bin_name, args, _input, timeout, shell=False, extra_signal=None):
        self.args = [bin_name] + args
        if shell == True:
            self.args = " ".join(self.args)
        self.shell = shell
        self.input = _input
        self.timeout = timeout
        self.default_signal = [signal.SIGSEGV, signal.SIGHUP]
        self.extra_signal = extra_signal
    
    def run(self):
        try:
            running = subprocess.Popen(self.args, stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE,
                stderr = subprocess.PIPE,
                shell=self.shell)

            try:
                (out, err)= running.communicate(self.input, self.timeout)
                signal = None
                if self.shell == True:
                    if running.returncode > 128 and running.returncode < 255:
                        signal = running.returncode - 128
                else:
                    if running.returncode < 0:
                        signal = -running.returncode
                
                if signal in self.default_signal:
                    return RunStatus.CRASH
                elif (self.extra_signal != None) and  (signal in self.extra_signal):
                    return Runstatus.USER_CRASH
                    
            except subprocess.TimeoutExpired as e:
                print("time out!!", e)
                running.kill()
                return RunStatus.EXCEPT

        except subprocess.SubprocessError as e:
            print("Popen error", e)
            return RunStatus.EXCEPT
        
        return RunStatus.PASS

    def is_hit(self, target_addr):
        try:
            proc_pid = ptrace.debugger.child.createChild(self.args, False)
            
            debugger = ptrace.debugger.PtraceDebugger()
            proc = debugger.addProcess(proc_pid, True)
            proc.createBreakpoint(target_addr)
            
            res = False
            proc.cont()
            while 1:
                event = proc.waitEvent()
                event_cls = event.__class__

                if event_cls == ptrace.debugger.ProcessExit:
                    print("child exit")
                    proc.detach()
                    debugger.quit()
                    break

                if event_cls != ptrace.debugger.ProcessSignal:
                    raise event

                if event.signum == signal.SIGTRAP and proc.getInstrPointer() == target_addr+1:
                    print("hit!")
                    res = True

                signum = event.signum
                if signum not in (signal.SIGTRAP, signal.SIGSTOP):
                    proc.cont(signum)
                else:
                    proc.cont()

            return res

        except subprocess.SubprocessError as e:
            print("Popen error", e)
            return RunStatus.EXCEPT
