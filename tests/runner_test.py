import unittest
import signal
import sysv_ipc
from fuzzer import * 

class TestRunner(unittest.TestCase):
    def test_run_pass(self):
        result = Runner(['echo', 'AAAA'], 0.2, True).run_direct(b'AA')
        print("[1] return code : ", result)
        self.assertEqual(result, RunStatus.PASS)

    def test_run_crash(self):
        result = Runner(['./test', str(signal.SIGSEGV.value)], 0.2, True).run_direct(b'AA')
        print("[2] return code : ", result)
        self.assertEqual(result, RunStatus.CRASH)

    def test_is_hit(self):
        result = Runner(['./test', str(signal.SIGUSR2.value)], 0.2, False).is_hit(b'AA', 0x40065d)
        print("[3] hit result : ", result)
        self.assertEqual(result, False)
    
    def test_fuzz(self):
        fuzzer = Fuzzer(['./test2'], "out", "in", True, 0.2)
        result_mv = fuzzer.fuzz()
        print("[4]", len(result_mv.tobytes()))
        self.assertNotEqual(hash(result_mv.tobytes()), hash(bytes(sysv_ipc.PAGE_SIZE)) )

if __name__ == "__main__":
    unittest.main()