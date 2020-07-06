import unittest
import signal
from fuzzer import * 

class TestRunner(unittest.TestCase):
    def test_run_pass(self):
        result = Runner(['echo', 'AAAA']).run(b'AA')
        print(result)
        self.assertEqual(result['state'], RunState.PASS)

    def test_run_crash(self):
        result = Runner(['./test', str(signal.SIGSEGV.value)]).run(b'AA')
        print(result)
        self.assertEqual(result['state'], RunState.CRASH)
        self.assertEqual(result['signal'], signal.SIGSEGV.value)

if __name__ == "__main__":
    unittest.main()