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
st.set_page_config(page_title="SME Neo4j Database Query", page_icon="🗄️")

# Page header
st.markdown("# Neo4j Database Query")
st.sidebar.header("Neo4j Database Query")

# Introduction
st.write(
    """
    ## Overview

    The **sme_neo4j_query_tool** is a specialized application designed for handling queries related to molecular electronics citations and relationships. It integrates with a Neo4j Database, running Cypher queries to extract relevant information. The tool utilizes node types such as Publication, Author, and Concept, along with relationship types like CITED_BY, WROTE, and Related.

    ## Functionality

    1. **Query Handling:** Input queries related to molecular electronics citations and relationships.
    2. **Neo4j Database Integration:** Execute Cypher queries in the Neo4j Database to gather information.
    3. **Node Types:**
       - *Publication:* Represents publications with properties such as id, title, tt_ab (title + abstract), publicationName, publicationDate, and keep (using n.keep='keep' to limit the Publication to SME Publications).
       - *Author:* Represents authors with a property name.
       - *Concept:* Represents concepts with a property name.
    4. **Relationship Types:**
       - *CITED_BY:* Represents the relationship where one publication is cited by another.
       - *WROTE:* Indicates who (Author) wrote a publication.
       - *Related:* Denotes the relationship between a concept and a publication.

    ## Usage

    - Enter your query in the provided input box.
    - Explore relationships and citations through the Neo4j Database integration.
    - Gain insights into the connections between publications, authors, and concepts.

    """
)

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
            records = [record.values() for record in result]
            
            # Convert records to DataFrame
            columns = result.keys()
            df = pd.DataFrame(records, columns=columns)

            return df.head(50)  # Limit to at most 50 results
    
database = Neo4jDatabase(host="bolt://49.234.22.192:7687",
                             user="neo4j", password="Ggl0609,")
input_query = st.text_input('Input your Query Cypher')
if st.button("Submit"):
    result = database.query(input_query)
    st.dataframe(result)


st.markdown("""
            ## Query Example


1. Titles and journal of all SME publications
`MATCH (n:Publication)
WHERE n.keep = 'keep'
RETURN n.id, n.title, n.publicationName AS journal`

2. Publications cited by a specific SME document
`MATCH (n:Publication)-[:CITED_BY]->(p:Publication)
WHERE n.keep = 'keep' AND p.keep='keep' AND n.id = 'specific id'
RETURN n.id, n.title, n.publicationDate.year AS year`

3. Authors of SME publications and their collaboration relationships
`MATCH (au:Author)-[:WROTE]->(n:Publication)-[:WROTE]->(coAuthor:Author)
WHERE n.keep = 'keep'
RETURN au.name AS author, COLLECT(DISTINCT coAuthor.name) AS coAuthors`

4. Search for the relevant SME literature using keywords in the title or title + abstract (n.tt_ab).  
a. For long but fuzzy query
`MATCH (n:Publication)
WHERE n.keep='keep'
RETURN n.title
ORDER BY apoc.text.sorensenDiceSimilarity(n.title, 'query keyword') DESC`  
b. For short but exact query
`MATCH (k:Concept)-[:Related]-(n:Publication)
WHERE n.keep = 'keep' AND toLower(k.name)='specific concept'
RETURN n.title`
""")