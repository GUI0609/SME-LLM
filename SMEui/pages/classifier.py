import streamlit as st
import time
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import torch


# Set page configuration
st.set_page_config(page_title="Classify Text", page_icon="🔄")

# Page header
st.markdown("# Classify Text")
st.markdown("wait for 2 min to load classification model")
st.sidebar.header("Classify Text")

from tqdm import tqdm
import spacy
from transformers import pipeline
import os
device = '1' if torch.cuda.is_available() else 'cpu'
classifier = pipeline("zero-shot-classification",
                        model="facebook/bart-large-mnli",device= device)

nlp = spacy.load("en_core_web_sm")
# Introduction
st.write(
    """
    ## Overview

    The **Classifier** tool is a powerful natural language processing (NLP) model designed for zero-shot text classification. It utilizes the Hugging Face's Transformers library and Facebook's BART-large-MNLI pre-trained model to classify input text into predefined labels. The tool is implemented in Python and uses popular NLP libraries such as spaCy for text processing and the Transformers pipeline for zero-shot classification.

    ## Usage

    - Input your text in the provided text input box.
    - Input your candidate labels split with ; in the corresponding text input box. If not provided, default labels are used. (related or not related single molecule electronics)
    - Click the "Submit" button to trigger the classification process.
    - The tool outputs the classification result, displaying the input text and the predicted label.

    """
)


def get_si_it_ms(text,candidate_labels):
    result = classifier(text, candidate_labels.split(';'))
    data ={
        'Text': text,
        'Label': result['labels'][0],
    }
    return data 
text = st.text_input('Input your Text')
candidate_labels = st.text_input('Input your labels split with ;')
if candidate_labels is None:
    candidate_labels = "related to single molecule electronics;not related single molecule electronics"

if st.button("Submit"):
    data = get_si_it_ms(text,candidate_labels)
    st.markdown('# Output:')
    st.markdown(data)

