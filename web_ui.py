# %%writefile app.py
from networkx import dfs_edges
import pandas as pd
import streamlit as st
from langchain.tools import BaseTool
from sentence_transformers import SentenceTransformer
import torch
from googleapiclient.discovery import build
import autogen
from langchain.vectorstores import Pinecone
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
import pinecone
from sentence_transformers import SentenceTransformer
import torch

config_list = autogen.config_list_from_json(
    env_or_file="/home/ggl/langchain/autogen/OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-3.5-turbo"],
    },
)

#-------------------------------------------pinecone----------------------------------------#

from langchain.vectorstores import Pinecone
from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA

text_field = "text"
# switch back to normal index for langchain
index = pinecone.Index('smedb')

# conversational memory
conversational_memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True
)

# Chat completion llm
llm = ChatOpenAI(
    openai_api_key="sk-tc4Lc7YF94uM6HPX74V4qViI4eeyW4Eqa6ADPu65hkYSBT8i",#'sk-413qYBqNnPBCQxKYGnmkwZ0JFNfbTerGwEbqvOxCoGysNyrl',#"sk-tc4Lc7YF94uM6HPX74V4qViI4eeyW4Eqa6ADPu65hkYSBT8i"
    model_name='gpt-3.5-turbo',
    base_url='https://api.chatanywhere.com.cn'
)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer('/home/ggl/langchain/Langchain-Chatchat/model/emb_model/distilbert-dot-tas_b-b256-msmarco', device=device)
pinecone.init(api_key="6c1151e5-731f-4844-8441-731855e4c412", environment="us-west1-gcp-free")
index = pinecone.Index("smedb")

class SMEPineconeQuery(BaseTool):
    name = 'sme_pinecone_query_tool'
    description = 'The "sme_pinecone_query_tool" is a specialized tool designed for handling queries related to molecular electronics. It employs a function to embed the query, matching it within the Pinecone vector store using similarity metrics. The tool then retrieves the top-related result and presents it as a message for input into a language model, facilitating the generation of an informative answer.'
    def _run(self, query):
        xq = model.encode(query).tolist()
        xc = index.query(xq, top_k=5, include_metadata=True)
        df = pd.DataFrame(
            {'text':[i['metadata']['text'] for i in xc['matches']]})
        print('Finish query in pinecone')
        df.to_csv('pinecone_result.csv')
        # st.dataframe(dataframe.style.highlight_max(axis=0))
        return [i['metadata']['text']+'\n' for i in xc['matches']]



#-------------------------------------------pinecone----------------------------------------#

#-------------------------------------------google----------------------------------------#

my_api_key = 'AIzaSyCkVIkZwCmV9KpylhcPTcukt6ZSuSZy7Ls'
my_cse_id = "f397f4e4d336848b3"

def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res

def find_metatags(json_data):
    metatags_values = []

    # 如果输入是字典类型，则检查其中的每一对键值对
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            # 如果键是 "metatags"，则将对应的值添加到结果列表中
            if key == "metatags":
                metatags_values.append(value)
            # 如果值是字典或列表类型，递归调用该函数
            elif isinstance(value, (dict, list)):
                metatags_values.extend(find_metatags(value))

    # 如果输入是列表类型，则递归调用该函数
    elif isinstance(json_data, list):
        for item in json_data:
            metatags_values.extend(find_metatags(item))

    return metatags_values

def query_google_research(input_keyword):
  data = google_search(input_keyword,my_api_key,my_cse_id)
  msg = []

  metatags = find_metatags(data)
  for i in metatags:
    for key, value in i[0].items():
      if 'title' in key and i[0][key] not in msg:
          msg.append(i[0][key])
      if 'description' in key and i[0][key] not in msg:
          msg.append(i[0][key])

  return msg

#后面关键词提取器加上
class GoogleSearch(BaseTool):
    name = 'google_search_query_tool'
    description = 'The google_search_query_tool is used to query keyword with google search api, if no related context is found with the sme_pinecone_query_tool, use the google_search_query_tool to perform a broader search.'
    def _run(self, input_keyword):
        return query_google_research(input_keyword)

#-------------------------------------------google----------------------------------------#


#-------------------------------------------pubchem----------------------------------------#
import pubchempy as pcp
from typing import List
property = """
'cid': PubChem Compound ID
'iupac_name': IUPAC Name
'molecular_formula': Molecular Formula
'canonical_smiles': Canonical SMILES (Simplified Molecular Input Line Entry System)
'inchi': International Chemical Identifier (InChI)
'inchikey': InChIKey
'xlogp': Calculated octanol/water partition coefficient (XLogP)
'charge': Charge
'rotatable_bond_count': Rotatable Bond Count
'h_bond_donor_count': Hydrogen Bond Donor Count
'h_bond_acceptor_count': Hydrogen Bond Acceptor Count
'mass': Molecular Weight
'monoisotopic_mass': Monoisotopic Mass
'tpsa': Topological Polar Surface Area
'complexity': Structural Complexity
'heavy_atom_count': Heavy Atom Count
'isotope_atom_count': Isotope Atom Count
'defined_atom_stereocenter_count': Number of Defined Atom Stereocenters
'undefined_atom_stereocenter_count': Number of Undefined Atom Stereocenters
'covalent_unit_count': Covalent Unit Count"""
class PubchemQuery(BaseTool):
    name = 'pubchem_molecule_query_tool'
    description = 'The "pubchem_molecule_query_tool" is for query molecule property. ' + property
    def _run(self, molecule, property_list: List[str]):
        return molecule.to_dict(properties=property_list)
#-------------------------------------------pubchem----------------------------------------#

#-------------------------------------------Neo4j----------------------------------------#
import os
import logging
from pathlib import Path

log_format = "%(asctime)s - %(levelname)s - %(message)s"
log_level_value = os.environ.get("LOG_LEVEL", logging.INFO)

logging.basicConfig(
    level=log_level_value,
    format=log_format,
)

logger = logging.getLogger("imdb")
from typing import List, Optional, Tuple, Dict
from neo4j import GraphDatabase
class Neo4jDatabase:
    def __init__(self, host: str = "neo4j://localhost:7687",
                 user: str = "neo4j",
                 password: str = "pleaseletmein"):
        """Initialize the movie database"""

        self.driver = GraphDatabase.driver(host, auth=(user, password))

    def query(
        self,
        cypher_query: str,
        params: Optional[Dict] = {}
    ) -> List[Dict[str, str]]:
        logger.debug(cypher_query)
        with self.driver.session() as session:
            result = session.run(cypher_query, params)
            # Limit to at most 50 results
            return [r.values()[0] for r in result][:50]
        


        
class QuerySMEGraph(BaseTool):
    name = 'query_sme_graph_tool'
    description = """when the query related citation and write relation, run the cypher in Neo4j Database and get answer
            Node Types:
            Publication: Represents publications with properties： id, title, tt_ab(title+abstract), publicationName, publicationDate, keep(using n.keep='keep' of Where limit the Publication is a SME Publication).
            Author: Represents authors with a property name.
            Concept: Represents concepts with a property name.
            Relationship Types:
            CITED_BY: Represents the relationship where one publication is cited by another.
            WROTE: Who(Author) wrote a publication.
            Related: between a concept and a publication."""
    def _run(self, query):
        database = Neo4jDatabase(host="bolt://49.234.22.192:7687",
                             user="neo4j", password="Ggl0609,")
        result = database.query(query)
        return f'query in sme graph database: {query}, got {result}'
#-------------------------------------------Neo4j----------------------------------------#


# Import things that are needed generically
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Optional, Type
import math
import os

from langchain.tools.file_management.read import ReadFileTool

# Define a function to generate llm_config from a LangChain tool
def generate_llm_config(tool):
    # Define the function schema based on the tool's args_schema
    function_schema = {
        "name": tool.name.lower().replace (' ', '_'),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    }

    if tool.args is not None:
      function_schema["parameters"]["properties"] = tool.args

    return function_schema


#查找原文
sme_pinecone_query_tool = SMEPineconeQuery()
#查找谷歌搜索
google_search_query_tool = GoogleSearch()
#查找pubchem分子信息
pubchem_query_tool = PubchemQuery()
#查找引用图数据库
query_sme_graph_tool = QuerySMEGraph()


tools = [
    sme_pinecone_query_tool,
    # google_search_query_tool,
    pubchem_query_tool,
    query_sme_graph_tool

]
# Construct the llm_config
llm_config = {
  #Generate functions config for the Tool
  "functions":[
      generate_llm_config(i) for i in tools
  ],
  "config_list": config_list,  # Assuming you have this defined elsewhere
  "timeout": 120,
}

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode='TERMINATE',
    max_consecutive_auto_reply=8,
    code_execution_config={"work_dir": "coding"},
)

# Register the tool and start the conversation
user_proxy.register_function(
    function_map={
        sme_pinecone_query_tool.name: sme_pinecone_query_tool._run,
        # google_search_query_tool.name: google_search_query_tool._run,
        pubchem_query_tool.name: pubchem_query_tool._run,
        query_sme_graph_tool.name: query_sme_graph_tool._run,

    }
)

chatbot = autogen.AssistantAgent(
    name="chatbot",
    system_message="only use the functions you have been provided with. If no message from user_proxy, just Summerize your query result and answer and end with TERMINATE",
    llm_config=llm_config,
)
def main(question):
    return user_proxy.initiate_chat(
      chatbot,
      message=question,
      llm_config=llm_config,
    )



import sys

# 获取命令行参数
arguments = sys.argv
main(arguments[1])








