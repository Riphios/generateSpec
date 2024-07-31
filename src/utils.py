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
    parser.add_argument("--verifier", "-v", help="Verifier to use")
    parser.add_argument("--llm", "-l", default="gpt4", help="LLM to use")
    parser.add_argument("--llmTimeout", "-lt", type=int, help="Timeout value")
    parser.add_argument("--verifierTimeout", "-vt", default="10", type=int, help="Timeout value")
    parser.add_argument("--prompt", "-p", default="base", help="Prompt to use")
    parser.add_argument("--postcondition-only", "-pc", action="store_true", help="Only generate postconditions")

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
        files = os.listdir(directory)
        files.sort()  # Sort files alphabetically
        if search_string == "":
            return [os.path.join(directory, f) for f in files]
        else:
            return [os.path.join(directory, f) for f in files if re.match(search_string, f)]

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
    
    #tries check what kind of program should be verified and sets the verifier accordingly
    @staticmethod
    def set_default_verifier(inputfile, inputdir):
        if inputfile:
            if inputfile.endswith('.c') or inputfile.endswith('.i'):
                return "frama-c"
            elif inputfile.endswith('.py'):
                return "crosshair"
            else:
                print('Only C and Python files are supported for verification currently.')
                return None
        elif inputdir:
            files = Utils.get_files(inputdir)
            for file in files:
                if file.endswith('.c') or file.endswith('.i'):
                    return "frama-c"
                elif file.endswith('.py'):
                    return "crosshair"
            print('Only C and Python files are supported for verification currently.')
            return None


    #get the input from the command line
    @staticmethod    
    def get_input():
        parser = argparse.ArgumentParser(description="Command line interface")
        parser.add_argument("--inputfile", "-i", help="Path to the input file")
        parser.add_argument("--inputdir", "-d", help="Path to the input directory")
        parser.add_argument("--outputdir", "-o", help="Path to the output directory")
        parser.add_argument("--verifier", "-v", help="Verifier to use")
        parser.add_argument("--llm", "-l", default="gpt4", help="LLM to use")
        parser.add_argument("--verifierTimeout", "-vt", default="10", type=int, help="Timeout value")
        parser.add_argument("--prompt", "-p", default="base", help="Prompt to use")
        parser.add_argument("--postcondition-only", "-pc", action="store_true", help="Only generate postconditions")

        args = parser.parse_args()

        if not args.inputfile and not args.inputdir:
            parser.error("Please specify an input file or directory")
        elif args.inputfile and args.inputdir:
            parser.error("Please specify only one of input file or directory")

        if args.outputdir is None:
            args.outputdir = Utils.set_default_outputdir(args.inputfile, args.inputdir, args.prompt)

        if args.verifier is None:
            args.verifier = Utils.set_default_verifier(args.inputfile, args.inputdir)

        inputfile = args.inputfile
        inputdir = args.inputdir
        outputdir = args.outputdir
        verifier = args.verifier
        llm = args.llm
        prompt_choice = args.prompt
        verifierTimeout = args.verifierTimeout
        pc_only = args.postcondition_only

        return inputfile, inputdir, outputdir, verifier, llm, prompt_choice, verifierTimeout, pc_only

    
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
        
    #extracts the ACSL specification from the text response (from the llm)
    @staticmethod
    def get_ACSL_specs(api_result):
        pattern = r'//@.*|/\*@.*?\*/'
        matches = re.findall(pattern, api_result, re.DOTALL)
        if matches:
            return matches
        else:
            print("No specifications found in the response")
            return None  
        
    #extracts the icontract specification from the text response (from the llm)
    @staticmethod
    def get_icontract_specs(api_result, pc_only):
        if pc_only:
            pattern = r'@icontract.ensure.*?(?=\ndef)'
        else:
            pattern = r'@.*?(?=\ndef)'
        matches = re.findall(pattern, api_result, re.DOTALL)
        if matches:
            return matches
        else:
            print("No specifications found in the response")
            return None
        
    #inserts the generated specifications (without requires) into the code
    @staticmethod
    def insert_specs(generated_specs, lines):
        code_with_specs = []
        if isinstance(generated_specs, list):
            generated_specs = '\n'.join(generated_specs)
        if isinstance(generated_specs, str):
            generated_specs = generated_specs.split('\n')
        #generated_specs = [spec for spec in generated_specs if 'requires' not in spec]

        code_with_specs.append("import icontract")
        for line in lines: 
            line_without_spaces = line.lstrip()
            if line_without_spaces.startswith("def "):              
                for spec in generated_specs:
                    code_with_specs.append(spec)
            code_with_specs.append(line)
        return '\n'.join(code_with_specs)
    
    #find the prompt from HumanEval that is the function def and the docstring
    @staticmethod
    def find_function_def(lines):
        function_def = ''
        flag = 0
        for line in lines: 
            if '"""' in line:
                flag += 1
            function_def = function_def + line + '\n'
            if flag < 2:
                break
        return function_def

    #write the output to a file
    @staticmethod
    def create_output_file(filepath, outputdir, prompt_choice, content = "", type = "result"):
        filename = os.path.basename(filepath)
        if filename.endswith('.c') or  filename.endswith('.i'):
            ending = filename[-2:]
            name = filename[:-2]
        elif filename.endswith('.py'):
            ending = ".py"
            name = filename[:-3]
        else:
            print('Only C and Pathon files are supported for verification currently.')
            return None

        if type == "verification":
            ending = ".txt"    
            prompt_choice = ""
            
        outputfile_name = name + "_" + prompt_choice + "_" + type + ending
            
        outputfile = os.path.join(outputdir, outputfile_name)
        with open(outputfile, "w") as f:
            f.write(content)
        return outputfile






