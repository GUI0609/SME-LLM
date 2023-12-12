import streamlit as st

st.set_page_config(
    page_title="LLM for SME",
    page_icon="🏠",
)
import subprocess
import streamlit as st
import pandas as pd
import asyncio

def run_cmd_and_display_output(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
    # 添加一个标志以指示是否开始输出
    start_output = False

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            if "user_proxy (to chatbot):" in output:
                start_output = True

            if start_output:
                if output.startswith('[') or 'HTTP Request' in output:
                    continue
                elif 'Press enter to skip' in output:
                    user_input = st.text_input('Input or TERMINATE')
                    process.stdin.write(user_input)

                elif "to user_proxy" in output or "to chatbot" in output:
                    # 如果是角色行，使用大写字母表示
                    st.markdown(f"**{output.strip().upper()}**")
                elif 'Finish query in pinecone' in output:
                    try:
                        df = pd.read_csv('pinecone_result.csv')
                        st.dataframe(df)
                        # df_html = df.to_html(classes="dataframe")
                        # st.components.v1.html(f'<div id="custom-html-div">{df_html}</div>', height=500, scrolling=True)
                    except:
                        print('cant output df')
                        
                else:
                    # 对于其他文本，使用Markdown格式输出
                    st.markdown(output.strip())

    return process.returncode
st.image('/home/ggl/langchain/autogen/web_page/smellm.png')
# st.image('/home/ggl/langchain/autogen/web_page/xmu-logo.jpg')
# Use HTML and CSS to center the image


# 页面布局
st.markdown("<h1 style='text-align: center;'>SME autochat LLM</h1>", unsafe_allow_html=True)
st.markdown('''Automatically execute tool calls through multi-turn dialogues to ultimately solve user problems.  
            (version 23.12.04)''')

# 获取用户输入的CMD命令
cmd_command = st.text_input('# Input your question')

st.sidebar.header('SME AutoChat LLM Introduce')
st.sidebar.markdown("""
                    
            
**SME AutoChat LLM (Single-Molecule Electronics AutoChat Language Model)** is an automatic chat language model developed specifically for single-molecule electronics, based on the OpenAI API. Its goal is to provide more real-time and accurate information answers by integrating AI technologies with tools related to single-molecule electronics through an automatic question-and-answer system.

## AI Tools

1. **Single-Molecule Electronics Local Knowledge Base (Pinecone):**
    - Information Sources:
        1. Title and abstract information from literature
        2. Paragraph extraction from PDF full texts
    (To forcibly invoke, type "query in pinecone database" before the question.)

2. **Single-Molecule Electronics Graph Database (Neo4j):**
    - Includes citation relationships between authors and literature.
    - Used for retrieving citation and author collaboration relationships.
    (To forcibly invoke, type "query in neo4j database" before the question.)
    (Using this tool requires setting a higher number of dialogue turns for accuracy in generating query statements.)

3. **Google Scholar:**
    - Can query real-time and more relevant literature information.
    (To forcibly invoke, type "query in google scholar" before the question.)
    (Based on a mirror site, accessible within China)

4. **Molecular Information Database (PubChem):**
    - Can query relevant information about molecules.
    (To forcibly invoke, input "query in pubchem" before the question.)
    (This tool is not thoroughly tested yet.)

## Online Version (VPN required)

- Implements Google search and returns search results.

## Planned Features

1. **Molecular Experimental Database Query:**
    - Provides original experimental results and related information.

2. **Experimental Procedure Query:**
    - Queries the steps and guidance for specific experimental operations.
    (Contributed by Yansong Liao)

3. **Research Scientific Questions (Topics) Recommendations:**
    - Provides research topic recommendations in the field of single-molecule electronics.

4. **Automated Literature Reading:**
    - Implements automated literature reading, extracts key information, and answers user questions.


            """)

# 当用户点击运行按钮时执行命令并显示输出
if st.button("Submit"):
    run_cmd_and_display_output(f"python web_ui.py '{cmd_command}'")
