import apiHandler
import utils
import mainMethods
import sys
import os
import pandas as pd

class Main:

    args = sys.argv
    util = utils.Utils()
    api = apiHandler.ApiHandler()
    mainMethods = mainMethods.MainMethods()
    loginfo = [["Input", "Verifier", "LLM", "Verifier Timeout"],[]]	
    log = [["filename"],["base"],["simple"],["baseNL"], ["simpleNL"]]
    stoplog = 0

    #get the input from the command line
    inputfile, inputdir, outputdir, verifier, llm, prompt_choice, verifierTimeout, pc_only \
        = util.get_input()
    if inputfile and not inputdir:
        files = [inputfile]
        loginfo[1].append(inputfile)
    elif inputdir and not inputfile:
        files = util.get_files(inputdir)
        loginfo[1].append(inputdir)
    loginfo[1].append(verifier),
    loginfo[1].append(llm),
    loginfo[1].append(verifierTimeout)

    if prompt_choice == "all":
        prompts = ["base", "simple", "baseNL", "simpleNL"]
    else:
        prompts = [prompt_choice]

    for prompt in prompts:
        #log.append(f'\n Prompt: {prompt} \n')
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
                    outputfile = mainMethods.process_file(file, prompt, llm, outputdir, pc_only)
                    if outputfile:
                        verification_file, exit_code = mainMethods.run_verifier(outputfile, outputdir, verifier, verifierTimeout, prompt)
                        if stoplog == 0 :
                            if file == log[0]:
                                stoplog = 1
                            else:
                                log[0].append(file)
                        if prompt == "base":
                            log[1].append(exit_code)
                        elif prompt == "simple":
                            log[2].append(exit_code)
                        elif prompt == "baseNL":
                            log[3].append(exit_code)
                        elif prompt == "simpleNL":
                            log[4].append(exit_code)

    
    # Create a DataFrame for the log data
    log_df = pd.DataFrame(log).transpose()
    log_df.columns = log_df.iloc[0]
    log_df = log_df[1:]

    # Create a DataFrame for the loginfo
    loginfo_df = pd.DataFrame(loginfo[1:], columns=loginfo[0])

    # Write to Excel file
    logfile = os.path.join(outputdir, "log.xlsx")
    with pd.ExcelWriter(logfile) as writer:
        loginfo_df.to_excel(writer, sheet_name='LogInfo', index=False)
        log_df.to_excel(writer, sheet_name='Log', index=False)