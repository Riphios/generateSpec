import argparse
import os
import re

#parse the arguments from the command line
def parse_arguments():
    parser = argparse.ArgumentParser(description="Command line interface")
    parser.add_argument("--inputfile", "-i", help="Path to the input file")
    parser.add_argument("--inputdir", "-d", help="Path to the input directory")
    parser.add_argument("--outputdir", "-o", default="../../results/", help="Path to the output directory")
    parser.add_argument("--verifier", "-v", default="frama-c", help="Verifier to use")
    parser.add_argument("--llm", "-l", default="gpt3.5", help="LLM to use")
    parser.add_argument("--llmTimeout", "-lt", type=int, help="Timeout value")
    parser.add_argument("--verifierTimeout", "-vt", default="10", type=int, help="Timeout value")
    parser.add_argument("--prompt", "-p", default="base", help="Prompt to use")

    args = parser.parse_args()

    if not args.inputfile and not args.inputdir:
        parser.error("Please specify an input file or directory")
    elif args.inputfile and args.inputdir:
        parser.error("Please specify only one of input file or directory")

    return parser.parse_args()

class Utils:
    #initialize the class 
    def __init__(self):
        self.args = parse_arguments()

    #get the file names from the directory (if they match the search string)
    @staticmethod
    def get_file_names(directory, search_string=""):
        if search_string == "":
            return os.listdir(directory)
        else:
            return [f for f in os.listdir(directory) if re.match(search_string, f)]

    #get the input from the command line
    @staticmethod    
    def get_input(self):
        inputfile = self.args.inputfile
        inputdir = self.args.inputdir
        outputdir = self.args.outputdir
        verifier = self.args.verifier
        llm = self.args.llm
        prompt_choice = self.args.prompt
        verifierTimeout = self.args.verifierTimeout
        llmTimeout = self.args.llmTimeout

        return inputfile, inputdir, outputdir, verifier, llm, prompt_choice, verifierTimeout, llmTimeout

    #Read the input file and return the lines
    @staticmethod
    def read_file(filepath):
        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
                lines = [line.rstrip() for line in lines]
            return lines
        except FileNotFoundError:
            print(f"File '{filepath}' not found")
            return None
        
    #extracts the c code from the text response (from the llm)
    @staticmethod
    def get_code_response(api_result):
        pattern = r"´´´c(.*?)´´´"
        match = re.search(pattern, api_result, re.DOTALL)
        if match:
            return match.group(1)
        return None  

    #write the output to a file
    @staticmethod
    def create_output_file(filepath, outputdir, content = "", type = "result"):
        filename = os.path.basename(filepath)
        if filename.endswith('.c') or  filename.endswith('.i'):
            ending = filename[-2:]
            outputfilename = filename[:-2] + "_" + type + ending
        else:
            print('Only C files are supported for verification.')
        outputfile = os.path.join(outputdir, outputfilename)
        with open(outputfile, "w") as f:
            f.write(content)
        return outputfile






