import pandas as pd
import openai
from sqlalchemy import text
import datetime

# create a chatGPT_session class that takes a question each time and stores the response into a prompt
class ChatGPT_session:
    def __init__(self, user_id=None, max_tokens=3000, temperature=0.8, model='gpt-3.5-turbo', max_history=5):
        self.user_id = user_id
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.model = model
        self.max_history = max_history

        self.prompt = None
        self.total_tokens_used = 0
        self.completion_tokens = 0
        self.prompt_tokens = 0
        self.num_questions = 0

    def ask(self, question):
        if not self.prompt:
            self.prompt = [{"role": "user", "content": question}]
        else:
            self.prompt.append({"role": "user", "content": question})
        
        response = openai.ChatCompletion.create(
            model= self.model,
            messages=self.prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )
        response_content = response['choices'][0]['message']['content']

        self.total_tokens_used+=response['usage']['total_tokens']
        self.completion_tokens+=response['usage']['completion_tokens']
        self.prompt_tokens+=response['usage']['prompt_tokens']

        self.prompt.append({"role": "assistant", "content": response_content})
        self.num_questions+=1
        if self.num_questions>self.max_history:
            del self.prompt[0:2]
        print(response_content)

    def show_cost(self):
        price_per_ktoken = 0.002
        print(f"Completion tokens used: {self.completion_tokens}")
        print(f"Prompt tokens used: {self.prompt_tokens}")
        print(f"Total tokens used: {self.total_tokens_used}")
        print(f"Total cost: {self.total_tokens_used*price_per_ktoken/1000:.4f} USD")
        print(f"Total cost: {self.total_tokens_used*7*price_per_ktoken/1000:.4f} CNY")


# Use multi-step prompt to get the answer
def get_openai_response(prompt, temperature=0.2, max_tokens=1000, model='gpt-3.5-turbo'):
    full_response = openai.ChatCompletion.create(
            model=model,
            messages=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False
        )
    # answer_content = full_response['choices'][0]['message']['content'].strip()
    return full_response, model, temperature

def get_execute_output(second_answer, db_name):
    with db_name.connect() as conn:
        result = conn.execute(text(second_answer))
        execute_output = result.all()
    return execute_output

def create_prompt(df, stage, question, first_answer=None, comments=None, second_answer=None, output=None, table_name='df', language='SQL'):
    data_format = 'pandas dataframe' if language == 'python' else 'table'
    cols = ','.join(str(col) for col in df.columns)
    prompt = f'You are a sales analyst. My data is a {data_format} named {table_name}, the columns are: [{cols}]\nThe question I\'m trying to answer is: QUESTION: {question}\n'

    if comments:
        print('comments: ', comments)
        print('question: ', question)
        print('first_answer: ', first_answer)
        print('prompt: ', prompt)

    if stage == 1:
        prompt += 'Explain the logic step by step.\n'
        prompt += 'Now, without writing any code, just explain the logic, how to find answer to the following questions, do it step by step.'
        prompt += 'In case the question is irrelevant to the data, just replay "__irrelevant__" and nothing else.\n'
    elif stage == 2:
        prompt += f'The steps are:\n{first_answer}\n\nProvide the {language} code, just the code, nothing else\n'
    elif stage == 3:
        prompt += f'The steps are:\n{first_answer}'
        prompt += f'\n{language} code:\n{second_answer}\nOutput:\n{output}\nAnswer the question, don\'t introduce yourself.\n'

    return [{'role': 'user', 'content': prompt}]




def AIO_GPT35(df, question, questionID, db_name, temperature=0.2, max_tokens=500):
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    first_prompt = create_prompt(df, stage=1, question=question)
    first_answer, first_full_response = get_openai_response(first_prompt, temperature, max_tokens)

    if not "__irrelevant__" in first_answer.lower():
        second_prompt = create_prompt(df, stage=2, question=question, first_answer=first_answer)
        second_answer, second_full_response = get_openai_response(second_prompt, temperature, max_tokens)
        
        try:
            output = get_execute_output(second_answer, db_name)
        except:
            output = 'Error'
        
        if output == 'Error':
            return questionID, question, first_full_response, second_full_response, None, None, None, 2, temperature, created_at
        else:
            third_prompt = create_prompt(df, stage=3, question=question, first_answer=first_answer, second_answer=second_answer, output=output)
            third_answer, third_full_response = get_openai_response(third_prompt, temperature, max_tokens)
            return questionID, question, first_full_response, second_full_response, third_full_response, output, third_answer, 0, temperature, created_at
    else:
        return questionID, question, first_full_response, None, None, None, None, 1, temperature, created_at