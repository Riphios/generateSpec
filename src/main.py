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

    #get the input from the command line
    inputfile, inputdir, outputdir, verifier, llm, prompt_choice, verifierTimeout \
        = util.get_input()
    if inputfile and not inputdir:
        files = [inputfile]
    elif inputdir and not inputfile:
        files = util.get_files(inputdir)

    for file in files:
        outputfile = mainMethods.process_file(file, prompt_choice, llm, outputdir)
        if outputfile:
            verification_file = mainMethods.run_verifier(outputfile, outputdir, verifier, verifierTimeout)
    