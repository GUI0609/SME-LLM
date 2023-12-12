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
st.set_page_config(page_title="SME Pinecone Database Query", page_icon="📄")

# Page header
st.markdown("# Pinecone Database Query")
st.sidebar.header("Pinecone Database Query")

# Introduction
st.write(
    """
    ## Overview

    The **sme_pinecone_query_tool** is a specialized application designed for handling queries related to molecular electronics. It leverages advanced techniques to embed user queries and matches them within the Pinecone vector store using similarity metrics. The tool then retrieves the top-related results and presents them as messages for input into a language model.

    ## Functionality

    1. **Query Handling:** Users can input queries related to molecular electronics into the tool.
    2. **Vector Store Matching:** The tool employs a function to embed the query and matches it within the Pinecone vector store.
    3. **Top-Related Results:** The tool retrieves the top-related results based on similarity metrics.
    4. **Language Model Input:** The results are presented as messages for input into a language model.
    5. **Informative Answers:** Facilitates the generation of informative answers using the language model.

    ## Usage

    - Enter your query in the provided input box.
    - Adjust the value of 'k' to control the number of top-related results.
    - Click the "Run Query" button to execute the query and view the results.

    """
)


# Initialize Pinecone index and model
pinecone.init(api_key="6c1151e5-731f-4844-8441-731855e4c412", environment="us-west1-gcp-free")
index = pinecone.Index("smedb")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('/home/ggl/langchain/Langchain-Chatchat/model/emb_model/distilbert-dot-tas_b-b256-msmarco', device=device)

# Function to run the query
def run_query(query, k):
    xq = model.encode(query).tolist()
    xc = index.query(xq, top_k=k, include_metadata=True)
    df = pd.DataFrame({'text': [i['metadata']['text'] for i in xc['matches']]})
    return df

# Streamlit UI components
query_input = st.text_input("Enter your query:")
k_value = st.number_input("Select value for k:", min_value=1, step=1, value=5)

# Button to execute the query
if st.button("Run Query"):
    st.text("Running query...")
    result_df = run_query(query_input, k_value)
    st.text('Finish query in Pinecone')
    st.dataframe(result_df)
    result_df.to_csv('pinecone_result.csv', index=False)