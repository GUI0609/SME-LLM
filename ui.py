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


# 页面布局
st.markdown("<h1 style='text-align: center;'>SME autochat LLM</h1>", unsafe_allow_html=True)
st.markdown('通过多轮对话自动执行工具调用，以最终解决用户的问题(version 23.12.04)')

# 获取用户输入的CMD命令
cmd_command = st.text_input('input your question')
st.sidebar.header('SME AutoChat LLM 说明')
st.sidebar.markdown("""
            SME AutoChat LLM*（Single-Molecule Electronics AutoChat Language Model）是基于 OpenAI API 的专为单分子电子学开发的自动聊天语言模型，其目标是通过整合开放AI技术与单分子电子学相关工具，通过自动问答系统，回答复杂的领域任务，提供更实时、准确的信息回答。

            ## 现有功能

            1. **单分子电子学本地知识库（Pinecone）：**
                - 信息来源：  
                    1. 文献标题和摘要信息   
                    2. PDF原文分段提取    
                (如果想强制调用，可以在问题前输入“query in pinecone database”)


            2. **单分子电子学图数据库（Neo4j）：**
                - 包含作者和文献的引用关系。
                - 用于检索引用和作者合作关系。  
                    (如果想强制调用，可以在问题前输入“query in neo4j database”)

            3. **分子信息数据库（PubChem）：**
                - 可以查询分子的相关信息。  
                    (如果想强制调用，可以在问题前输入“query in pubchem”)  
                    (该工具还未充分测试)
                    

            ## 在线版（需要翻墙）

            - 实现谷歌搜索并返回检索信息。

            ## 待开发功能

            1. **分子实验数据库查询：**
                - 提供实验原始结果和相关信息。

            2. **实验操作路程查询：**
                - 查询具体实验操作的步骤和指导。

            3. **研究科学问题（课题）推荐：**
                - 提供关于单分子电子学领域的研究课题推荐。

            4. **自动化文献阅读：**
                - 实现自动化文献阅读，提取关键信息并回答用户提出的问题。

            """)

# 当用户点击运行按钮时执行命令并显示输出
if st.button("Submit"):
    run_cmd_and_display_output(f"python web_ui.py '{cmd_command}'")
