import numpy as np
import pandas as pd



from openai import OpenAI
client = OpenAI(
api_key = 'sk-413qYBqNnPBCQxKYGnmkwZ0JFNfbTerGwEbqvOxCoGysNyrl',
base_url = 'https://api.chatanywhere.com.cn'
)
def chat(text):
    chat_completion = client.chat.completions.create(
      messages=[
          {
              "role": "user",
              "content": text,
          }
      ],
      model="gpt-3.5-turbo",
    )
    return chat_completion.choices[0].message.content

import sys
# 获取命令行参数
arguments = sys.argv
chat(arguments[1])