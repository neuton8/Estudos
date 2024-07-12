from dotenv import load_dotenv
import os
from openai import OpenAI
import time

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI()

print("Bem vindo ao chatbot do neutão") 
log_conversation = []

while True:
    input_msg = str(input("user: "))
    if input_msg == 'exit':
       break
    log_conversation.append({"role": "user", "content": input_msg})
    stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    temperature=0,
    max_tokens=1000,
    messages=log_conversation,
    stream=True,)

    log_sys_response = ""
    for message in stream:
        if message.choices[0].delta.content is not None:
            print(message.choices[0].delta.content,end='')
        log_sys_response = log_sys_response + str(message.choices[0].delta.content)
    log_conversation.append({"role": "assistant", "content": log_sys_response})
    print('\n')
    


