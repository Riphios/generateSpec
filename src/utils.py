import argparse
import os
import re
from datetime import datetime

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
    def get_files(directory, search_string=""):
        if search_string == "":
            return [os.path.join(directory, f) for f in os.listdir(directory)]
        else:
            return [os.path.join(directory, f) for f in os.listdir(directory) if re.match(search_string, f)]

    #set default output directory based on input name
    @staticmethod
    def set_default_outputdir(inputfile, inputdir, prompt):
        if inputfile:
            input = os.path.basename(inputfile)
        elif inputdir:
            input = os.path.basename(os.path.dirname(inputdir))
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)            # Get the directory containing the current file
        results_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "results"))
        
        # Create the new directory 
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_dir_name = f"{input}_{prompt}_results_{current_datetime}"
        default_output_dir = os.path.join(results_dir, new_dir_name)
        os.makedirs(default_output_dir, exist_ok=True)
        
        return default_output_dir
   


    #get the input from the command line
    @staticmethod    
    def get_input():
        parser = argparse.ArgumentParser(description="Command line interface")
        parser.add_argument("--inputfile", "-i", help="Path to the input file")
        parser.add_argument("--inputdir", "-d", help="Path to the input directory")
        parser.add_argument("--outputdir", "-o", help="Path to the output directory")
        parser.add_argument("--verifier", "-v", default="frama-c", help="Verifier to use")
        parser.add_argument("--llm", "-l", default="gpt3.5", help="LLM to use")
        parser.add_argument("--verifierTimeout", "-vt", default="10", type=int, help="Timeout value")
        parser.add_argument("--prompt", "-p", default="base", help="Prompt to use")

        args = parser.parse_args()

        if not args.inputfile and not args.inputdir:
            parser.error("Please specify an input file or directory")
        elif args.inputfile and args.inputdir:
            parser.error("Please specify only one of input file or directory")

        if args.outputdir is None:
            args.outputdir = Utils.set_default_outputdir(args.inputfile, args.inputdir, args.prompt)

        inputfile = args.inputfile
        inputdir = args.inputdir
        outputdir = args.outputdir
        verifier = args.verifier
        llm = args.llm
        prompt_choice = args.prompt
        verifierTimeout = args.verifierTimeout

        return inputfile, inputdir, outputdir, verifier, llm, prompt_choice, verifierTimeout

    
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
        pattern = r"```c(.*?)```"
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






