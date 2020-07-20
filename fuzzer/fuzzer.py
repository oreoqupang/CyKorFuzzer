import sysv_ipc
import os, sys
import fuzzer.runner as runner

class Fuzzer(object):
    def __init__(self, argv, output_folder, input_folder, qemu_mode=False, time_out=0.2):
        self.shmid = None
        self.trace_bits = None

        if qemu_mode == True:
            self.argv = ['./afl-qemu-trace', '--'] + argv
        else:
            self.argv = argv
        self.output_folder = output_folder
        self.input_folder = input_folder
        self.qemu_mode = qemu_mode
        self.time_out = time_out
        self.runner_instance = runner.Runner(argv, self.time_out)
    
    def setup_shm(self):
        try:
            self.trace_bits = sysv_ipc.SharedMemory(sysv_ipc.IPC_PRIVATE, sysv_ipc.IPC_CREX)
           
            self.shmid = self.trace_bits.id

            os.environ['__AFL_SHM_ID'] = str(self.shmid)
        except:
            print("shm_memory create error")
            return -1

    def init_forkserver(self):
        st_r, st_w = os.pipe()
        ctl_r, ctl_w = os.pipe()
        dev_null_fd = os.open(os.devnull, os.O_RDWR)
        
        os.set_inheritable(st_r, True)
        os.set_inheritable(st_w, True)
        os.set_inheritable(ctl_r, True)
        os.set_inheritable(ctl_w, True)

        pid = os.fork()
        if pid == 0: # child process
            os.setsid()
            os.dup2(dev_null_fd, 1)
            os.dup2(dev_null_fd, 2)
            os.dup2(self.out_fd, 0)

            os.dup2(ctl_r, 198, True)
            os.dup2(st_w, 199, True)

            os.close(st_r)
            os.close(st_w)
            os.close(ctl_r)
            os.close(ctl_w)
            os.close(dev_null_fd)

            try:
                os.execve(self.argv[0], self.argv, os.environ)
            except OSError as e:
                raise e

        else: # parent process
            os.close(ctl_r)
            os.close(st_w)

            self.fsrv_ctl_fd = ctl_w
            self.fsrv_st_fd = st_r

        
            rstr = os.read(self.fsrv_st_fd, 4)
            if len(rstr) == 4:
                return True
            else:
                raise Exception('fail to init forkserver')

    def fuzz(self):
        if self.qemu_mode == True and os.access('afl-qemu-trace', os.X_OK) == False:
            raise Exception('can not execute afl-qemu-trace')
        
        self.out_fd = os.open(".cur_input", os.O_RDWR|os.O_CREAT)
        self.setup_shm()
        self.init_forkserver()
        
        _input = b'input' #TODO
        mv = memoryview(self.trace_bits)
        for i in range(sysv_ipc.PAGE_SIZE):
            mv[i] = 0
        
        if self.qemu_mode == True:
            result = self.runner_instance.run_qemu(_input, self.fsrv_ctl_fd, self.fsrv_st_fd)
        else:
            reuslt = self.runner_instance.run_direct(_input)

        return mv