import unittest
import signal
from fuzzer import * 

class TestRunner(unittest.TestCase):
    def test_run_pass(self):
        result = Runner('echo', ['AAAA'], b'AA', 0.2, True).run()
        print("[1] return code : ", result)
        self.assertEqual(result, RunStatus.PASS)

    def test_run_crash(self):
        result = Runner('./test', [str(signal.SIGSEGV.value)], b'AA', 0.2, True).run()
        print("[2] return code : ", result)
        self.assertEqual(result, RunStatus.CRASH)

    def test_is_hit(self):
        result = Runner('./test', [str(signal.SIGUSR2.value)], b'AA', 0.2, False).is_hit(0x40065d)
        print("[3] hit result : ", result)
        self.assertEqual(result, False)

if __name__ == "__main__":
    unittest.main()