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
    loginfo = [["Input", "Verifier", "LLM", "Verifier Timeout", "Only PostConditions"],[]]	
    log = [["filename"],["buggy: base"],["buggy: simple"],["buggy: baseNL"], ["buggy: simpleNL"], ["not buggy: base"], ["not buggy: simple"], ["not buggy: baseNL"], ["not buggy: simpleNL"], ["Useful Spec"]]
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
    loginfo[1].append(verifier)
    loginfo[1].append(llm)
    loginfo[1].append(verifierTimeout)
    loginfo[1].append(pc_only)

    if prompt_choice == "all":
        prompts = ["base", "simple", "baseNL", "simpleNL"]
    else:
        prompts = [prompt_choice]

    for prompt in prompts:
        #log.append(f'\n Prompt: {prompt} \n')
        stoplog +=1
        for file in files:
            if not file.endswith("_b.py"): 
                continue
            else:
            # Temp solution for single def files
                lines = util.read_file(file)
                num_funcs = 0
                for line in lines:
                    if "def " in line:
                        num_funcs += 1
                if num_funcs > 1:
                    continue
                else:
            # End temp solution
                    outputfile_b, outputfile_nb = mainMethods.process_file(file, prompt, llm, outputdir, pc_only)
                    if outputfile_b and outputfile_nb:
                        verification_file_b, exit_code_b = mainMethods.run_verifier(outputfile_b, outputdir, verifier, verifierTimeout, prompt)
                        verification_file_nb, exit_code_nb = mainMethods.run_verifier(outputfile_nb, outputdir, verifier, verifierTimeout, prompt) 
                        if stoplog == 1 :
                                log[0].append(file)
                        if prompt == "base":
                            log[1].append(exit_code_b)
                            log[5].append(exit_code_nb)
                        elif prompt == "simple":
                            log[2].append(exit_code_b)
                            log[6].append(exit_code_nb)
                        elif prompt == "baseNL":
                            log[3].append(exit_code_b)
                            log[7].append(exit_code_nb)
                        elif prompt == "simpleNL":
                            log[4].append(exit_code_b)
                            log[8].append(exit_code_nb)
    
    #WILL CAUSE AN ERROR WHEN NOT USING ALL PROMPTS!!!!!!
    for i in range(1, len(log[1])):
    if (log[1][i] == 1 and log[5][i] == 0) or (log[2][i] == 1 and log[6][i] == 0) or (log[3][i] == 1 and log[7][i] == 0) or (log[4][i] == 1 and log[8][i] == 0):
        log[9].append("Yes")
    else:
        log[9].append("No")
    
    # Create a DataFrame for the log data
    log_df = pd.DataFrame(log).transpose()
    log_df.columns = log_df.iloc[0]
    log_df = log_df[1:]

    # Create a DataFrame for the loginfo
    loginfo_df = pd.DataFrame(loginfo[1:], columns=loginfo[0])

    # Write to Excel file
    logname = os.path.join("log_", os.path.basename(outputdir), ".xlsx")
    logfile = os.path.join(outputdir, logname)
    with pd.ExcelWriter(logfile) as writer:
        loginfo_df.to_excel(writer, sheet_name='LogInfo', index=False)
        log_df.to_excel(writer, sheet_name='Log', index=False)