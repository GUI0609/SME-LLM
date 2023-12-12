from tkinter.messagebox import QUESTION
import streamlit as st
import time
import numpy as np

st.set_page_config(page_title="Chatpdf", page_icon="📈")

st.markdown("# Chatpdf")
st.sidebar.header("Chatpdf")
st.write(
    """Chatpdf"""
)

import spacy

import streamlit as st
import io
import os
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    file_contents = uploaded_file.getvalue()
    # 将字节流转换为文件对象
    file_obj = io.BytesIO(file_contents)
    upload_path = os.path.join('/home/ggl/langchain/autogen/SMEui/files_upload',uploaded_file.name)
    # 将文件保存到本地文件系统
    with open(upload_path, "wb") as f:
        f.write(file_contents)
    # 获取文件路径
    file_path = f.name
    st.write(f"Success upload'{uploaded_file.name}', processing it...")

#处理pdf
import PyPDF2

import pandas as pd
from tqdm import tqdm
import spacy
from transformers import pipeline
import os

classifier = pipeline("zero-shot-classification",
                        model="facebook/bart-large-mnli")
nlp = spacy.load("en_core_web_sm")
def extract_text_from_pdf(pdf_path):
    """
    从 PDF 文件中提取文本
    """

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    text = ' '.join(text.split('\n'))

    try:
        text.lower().index('reference')
        text = text[:text.lower().index('reference')]
    except:
        pass
    return text

text = extract_text_from_pdf(upload_path)
import re
exclude_keywords = ["journal", "society", "support", "accept", "department", "founda", "univers", "open acces", "doi", "http", "publish", "©", "@"]
exclude_years = [str(j) for j in range(1997, 2024)]



QUESTION = st.text_input('Input your question')
def get_most_related_sentense(text,QUESTION):
    doc = nlp(text)
    q = nlp(QUESTION)
    # 计算相似度并排序
    similarities = [(sentence.text, q.similarity(sentence)) for sentence in doc.sents if len(sentence.text)>35 and not any(substring in sentence.text.lower() for substring in exclude_keywords + exclude_years)]
    sorted_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

    # 打印前5个结果
    return [sorted_similarities[i][0] for i in range(min(10, len(sorted_similarities)))]
if st.button("Submit"):
    st.markdown('Related sentenses:')
    st.markdown(get_most_related_sentense(text,QUESTION))








