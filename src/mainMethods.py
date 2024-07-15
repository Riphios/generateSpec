import utils
import apiHandler
import subprocess

class MainMethods():

    util = utils.Utils()
    api = apiHandler.ApiHandler()

    #sends the given code to the LLM and saves the generated specifications into a file
    @classmethod
    def process_file(cls, file, prompt, llm, outputdir):
        print("Processing file: " + file)
        lines = cls.util.read_file(file)

        #TODO: Implement parsing the file if necessary

        api_result = cls.api.handle_prompt(lines, prompt, llm)

        code_response = cls.util.get_code_response(api_result)

        print('The following specifications were generated into the code by the LLM:')
        print(code_response)

        #TODO: Implement parser for inserting specifications into the code / all 
        # similar programs from buggy / not buggy batch

        outputfile = cls.util.create_output_file(file, outputdir, content = code_response)
        
        return outputfile


    #runs the verifier on the generated code, writes the results to a file and returns the filepath
    @classmethod
    def run_verifier(cls, file, outputdir, verifier, verifier_timeout):
        print("Running " + verifier + " on file: " + file)
        verification_file = cls.util.create_output_file(file, outputdir, type = "verification")
        if verifier == 'frama-c':
            frama_c_cmd = ['frama-c', '-wp', file, '-wp-timeout', verifier_timeout, '-wp-prover', 'alt-ergo']
            with open(verification_file, 'w') as f:
                subprocess.run(frama_c_cmd, stdout=f, stderr=subprocess.STDOUT)
        print("Verification results are written to " + verification_file)
        return verification_file






