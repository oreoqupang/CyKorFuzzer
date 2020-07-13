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

if __name__ == "__main__":
    unittest.main()