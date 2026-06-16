import openai 
from dotenv import load_dotenv
import os

load_dotenv(".env")
openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')
openai.azure_endpoint =os.getenv('AZURE_OPENAI_ENDPOINT')
openai.api_type = os.getenv('OPENAI_API_TYPE')
openai.api_version =  os.getenv('AZURE_OPENAI_API_VERSION')

while True:
    _input = input()
    if _input == 'exit':
        break


    response = openai.chat.completions.create(
        model = 'dev-gpt-5.4-mini',
        messages = [

            {
                "role": "system",
                "content": "You are a awesome assistant."
            },
            {
                "role": "user",
                "content": _input
            }
        ]
    )

    print(f"{response.choices[0].message.content}\n")


