import os
import subprocess
import signal
from enum import Enum

class RunState(Enum):
    PASS = 0
    CRASH = 1
    EXCEPTION = 2

class Runner(object):
    def __init__(self, args, 
                 shell = False,
                 as_file = False, 
                 signals = None,
                 timeout = 0.2):  
        """Runner class that executes target binary and watch. 

        Args:
            args (str): Args to execute with. 
            shell (bool): If true, binary will be executed through shell. Defaults to False.
            as_file (bool): Provide input data as temporary file, and . Defaults to False.
            signals (list): List of signals to catch. Defaults to [ SIGBUS, SIGFPE, SIGILL, 
                SIGSEGV, SIGSYS ].
            timeout (float): [description]. Defaults to 0.1.
        """
        self.args = args
        self.shell = shell
        self.as_file = as_file
        self.timeout = timeout

        # TODO: Reference from other fuzzers. 
        if signals is None:
            self._signals = map(lambda a: a.value, [ signal.SIGBUS, signal.SIGFPE, signal.SIGILL, 
                signal.SIGSEGV, signal.SIGSYS ])
        else:
            self._signals = signals

        if self.as_file:
            if '@@' not in self.args:
                # TODO: Generate warning that program may not know the path of input data file. 
                pass

        if self.shell:
            raise ValueError('Setting shell to True is not yet supported. ')

    def run(self, input_data):
        """Run binary once with given input data, and get result. 

        Args:
            input_data (bytes): Input data passed to binary. 

        Returns:
            dict: Result of execution. 
        """
        
        try:
            process = subprocess.Popen(self.args, shell=self.shell, stdin=subprocess.PIPE, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                close_fds=True)
            
            try:
                process.communicate(input=input_data, timeout=self.timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                return { 'state': RunState.EXCEPTION, 'message': 'Timeout reached. ' }
            exitcode = process.poll()
            if exitcode == None:
                return { 'state': RunState.EXCEPTION, 'message': 'Something wrong with the code. ' }

            # TODO: Handle cases when binary executed through shell, this case exit code will not get negative (maybe)
            if exitcode < 0:
                exitsignal = -exitcode

                # Return code indicating that binary exited due to signal. 
                if exitsignal in self._signals:
                    return { 'state': RunState.CRASH, 'message': 'Crashed with signal. ', 'signal': exitsignal }

        except Exception as e:
            return { 'state': RunState.EXCEPTION, 'message': 'Something wrong with the code. ', 'error': e }

        return { 'state': RunState.PASS }
