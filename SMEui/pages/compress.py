import streamlit as st
import time
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import pinecone
import torch
from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA

# Set page configuration
st.set_page_config(page_title="Compress Text", page_icon="🔄")

# Page header
st.markdown("# Compress Text")
st.sidebar.header("Compress Text")
import streamlit as st
from selective_context import SelectiveContext



# Web Page Introduction with Text Compression
st.write(
    """
    ## Text Compression Overview

    The **Text Compression Tool** is designed to efficiently compress text while preserving its essential content. It uses advanced natural language processing techniques to reduce the length of the input text while maintaining its key information.

    ### How it Works

    1. **Input Your Text:** Enter the text you want to compress in the provided input box.
    2. **Click "Compress Text":** Press the button to initiate the text compression process.
    3. **View Results:** The tool will display the compressed text for your reference.

    ### Benefits

    - Efficiently reduce the length of text.
    - Preserve essential content.
    - Ideal for summarization and saving space.

    """
)
# Text Compression

sc = SelectiveContext(model_type='gpt2', lang='en')

text = st.text_input('Input your Text to Compress')

from transformers import GPT2Tokenizer
def count_gpt2_tokens(input_text, model_name="/home/ggl/langchain/Langchain-Chatchat/model/emb_model/gpt2"):
    # 加载 GPT-2 Tokenizer
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)

    # 使用 Tokenizer 编码文本
    tokens = tokenizer.encode(input_text, add_special_tokens=True)

    # 输出 token 数量
    return len(tokens)
def process_text(text, reduce_ratio=0.8, max_tokens=1020):
    if count_gpt2_tokens(text) < max_tokens:
        return sc(text, reduce_ratio)[0].replace('�','')

    text_list = [text]
    while any(count_gpt2_tokens(t) >= max_tokens for t in text_list):
        new_text_list = []
        for t in text_list:
            if count_gpt2_tokens(t) >= max_tokens:
                half_index = len(t) // 2
                new_text_list.append(t[:half_index])
                new_text_list.append(t[half_index:])
            else:
                new_text_list.append(t)

        text_list = new_text_list

    results = []
    for t in text_list:
        results.append(sc(t, reduce_ratio)[0])

    return ' '.join(results).replace('�','')


reduce_ratio = st.number_input("Select value for reduce_ratio:", min_value=0.0, step=0.1, max_value=1.0, value=0.5)
max_tokens = st.number_input("Select value for reduce_ratio:", min_value=500, step=100, value=1020)

import subprocess

def run_cmd_and_display_output(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
    while True:
        output = process.stdout.readline()
        if output:
            st.markdown(output)


from selective_context import SelectiveContext
if st.button("Submit"):
    result = process_text(text,reduce_ratio)
    st.markdown('# Output:')
    st.markdown(result)
    # question = st.text_input('input your question')
    # if st.button("Chat"):
    #     question = question.replace("'","")
    #     result = result.replace("'","")
    #     run_cmd_and_display_output(f"python SMEui/pages/simple_chat.py 'answer Question: {question} Message:{result}'")




