import argparse

import fuzzer.runner as runner
from pprint import pprint

class Fuzzer(object):
    def __init__(self, argv, output_folder,
                 input_folder = None):
        '''
        :param binary_path: path to 
        '''
        self.argv = argv
        self.output_folder = output_folder
        self.input_folder = input_folder
        self.runner_instance = runner.Runner(self.argv)
    
    def start(self):
        # TODO: implement mutation, apply
        print(self.runner_instance.run(b'AAAA'))
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fuzz binary. ')
    
    parser.add_argument('-i', '--input-folder', type=str, nargs=1, help='Input folder path that seed files are located. ')
    parser.add_argument('-o', '--output-folder', type=str, nargs=1, help='Output folder path that results will be located. ')
    parser.add_argument('argv', type=str, nargs=argparse.REMAINDER, help='Argv to be passed. ')

    parsed_args = parser.parse_args()

    argv = parsed_args.argv
    input_folder = parsed_args.input_folder
    output_folder = parsed_args.output_folder

    fuzzer = Fuzzer(argv, output_folder, input_folder=input_folder)
    fuzzer.start()