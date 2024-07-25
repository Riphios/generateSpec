import apiHandler
import utils
import mainMethods
import sys
import os

class Main:

    args = sys.argv
    util = utils.Utils()
    api = apiHandler.ApiHandler()
    mainMethods = mainMethods.MainMethods()
    log = []

    #get the input from the command line
    inputfile, inputdir, outputdir, verifier, llm, prompt_choice, verifierTimeout \
        = util.get_input()
    if inputfile and not inputdir:
        files = [inputfile]
        log.append(inputfile)
    elif inputdir and not inputfile:
        files = util.get_files(inputdir)
        log.append(inputdir)
    log.append(f'Verifier: {verifier}, LLM: {llm}, Verifier Timeout: {verifierTimeout} \n')

    if prompt_choice == "all":
        prompts = ["base", "simple", "baseNL", "simpleNL"]
    else:
        prompts = [prompt_choice]

    for prompt in prompts:
        log.append(f'\n Prompt: {prompt} \n')
        for file in files:
            # Temp solution for single def files
            if not file.endswith("_b.py"): 
                continue
            else:
                lines = util.read_file(file)
                num_funcs = 0
                for line in lines:
                    if "def " in line:
                        num_funcs += 1
                if num_funcs > 1:
                    continue
                else:
            # End temp solution
                    outputfile = mainMethods.process_file(file, prompt, llm, outputdir)
                    if outputfile:
                        verification_file, exit_code = mainMethods.run_verifier(outputfile, outputdir, verifier, verifierTimeout, prompt)
                        log.append(f'{file} EXIT CODE: {exit_code}')
    
    logfile = os.path.join(outputdir, "log.txt")
    with open(logfile, 'w') as f:
        f.write('\n'.join(log)) 