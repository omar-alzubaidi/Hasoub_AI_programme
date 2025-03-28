import os
import sys
from openai import OpenAI




client = OpenAI()
prompt = sys.argv[1]

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content":prompt}
        

    ]
)

generated_text = response.choices[0].message.content
print(generated_text)

