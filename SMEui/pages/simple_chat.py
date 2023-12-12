import streamlit as st
import time
import numpy as np
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Simple chat", page_icon="🔄")

# Page header
st.markdown("# Simple chat")
st.sidebar.header("Simple chat")

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

text = st.text_input('Input your Text to Compress')
if st.button("Chat"):
    chat_result = chat(text)
    st.markdown(chat_result)