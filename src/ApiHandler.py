import openai
from openai import OpenAI
import keys
import time

class ApiHandler(): 
     max_retries = 5
     retry_delay = 10
     timeout = 30
     return_tokens = 256

     #create an instance of the OpenAI API
     client = OpenAI(api_key = keys.OPENAI_API_KEY, 
                    timeout = timeout)

     preciseness_request = 'Make sure your answer fits into the ' + str(return_tokens) \
     + ' return tokens!'

     systemMsg = "You are a helpful assistant, can work with code and give precise answers."
                    
     base_prompt = 'In the following I will provide a code snippet which may or may ' + \
     'not be buggy. Try to use annotations, function names or any hints you can ' + \
     'use in natural language or in the code to identify what the code is meant ' + \
     'to do. Do NOT correct the code, but write formal specifications in ACSL ' + \
     'annotations that can be used to verify whether the program works as intended.' + \
     'Please keep any comments in the code as they are.'


     # Depending on chosen prompt and llm, a request is generated
     @classmethod
     def handle_prompt(cls, lines, prompt, llm):
          response = cls.gen_spec_request(lines, prompt, llm)
          if response.choices and response.choices[0].message.content != "":
               print(prompt + ', ' + llm + ': ' + response.choices[0].message.content)
               return response.choices[0].message.content
          else:
               print("No response found")
               return ""


     #Takes the lines from the program and the chosen prompt and model to send 
     #a request to the model
     #Normalizes llm choice to current model
     @classmethod
     def gen_spec_request(cls, lines, prompt_choice, llm):

          if llm in ['GPT4', 'gpt-4', 'GPT-4', 'gpt4', 'gpt4o', 'GPT4o', 'gpt-4o', 'GPT-4o']:
               llm = 'gpt-4o-2024-05-13'
          if llm in ['GPT3', 'gpt-3', 'GPT-3', 'gpt3', 'gpt3.5', 'GPT3.5', 'gpt-3.5', 'GPT-3.5']:
               llm = 'gpt-3.5-turbo-0125'

          for i in range(cls.max_retries):
               try:
                    if prompt_choice == 'base':
                         prompt = cls.base_prompt + '\n\n' + cls.preciseness_request + \
                              '\n\n```c \n' + '\n'.join(lines) + '\n```'
                    response = cls.client.chat.completions.create(
                         model=llm,
                         messages=[
                         {"role": "system", "content": cls.systemMsg},
                         #{"role": "user", "content": task + example},
                         #{"role": "assistant", "content": "//@ loop invariant [logical expression];"},
                         {"role": "user", "content": prompt }
                         ],
                         temperature=0,
                         max_tokens=cls.return_tokens,
                         timeout=cls.timeout)
                    print('Prompt sent to API \n' + prompt)
                    return response
               except openai.APIConnectionError as e:
                    if i < cls.max_retries:
                         print("APIConnectionError: " + str(e) + " Retrying in " + str(cls.retry_delay) + " seconds...")
                         time.sleep(cls.retry_delay)
                         cls.retry_delay *= 2
                    else:
                         print("APIConnectionError: " + str(e) + " Max retries exceeded.")
                         print(e.error_code)
                         break
               except openai.APIError as e:
                    print("API Error: " + e.statuscode + " " + str(e) )
                    continue
               continue


'''

Base Prompt finished?

In the following I will provide a code snippet which may or may not be buggy. Try to use annotations, function names or any hints you can use in natural language or in the code to identify what the code is meant to do. Do NOT correct the code, but write formal specifications in ACSL annotations that can be used to verify whether the program works as intended. 

Make sure your answer fits into the 256 return tokens!




simple prompt

In the following I will provide a code snippet which may or may not be buggy. Please do not correct it, but just generate formal specifications in acsl language for the code snippet
Try to encapsulate the behaviour of the function without reimplementing the function. The specification may be less complex, but should never be trivial.


int min(int x, int y) {
     return (x<y)?x:x;
}

code2NL prompt


Encased in ´´´c and ´´´ In the following a code snippet will be provided which may or may not be buggy. Please use comments, function or variable names and other hints in the code to determine what the code is supposed to do. 
Then disregard, whether it is buggy or not, and just give a brief informal explanation in natural language of what the code is supposed to be doing. It should contain all necessary information, but no code pieces.

´´´c
int min(int x, int y) {
     return (x<y)?x:x;
}
´´´

Response:



simple NL2spec prompt

Please generate formal specifications in ACSL for a code snippet that is given
 after this paragraph. 
 Try to encapsulate the behaviour of the function without 
 reimplementing the function. The specification may be less complex, but should 
 never be trivial.

'''