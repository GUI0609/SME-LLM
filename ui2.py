import streamlit as st

# 设置初始页面为Home
session_state = st.session_state
session_state['page'] = 'Home'

# 导航栏
page = st.sidebar.radio('Query type', ['Langchain', 'Autogen'])

if page == 'Langchain':
    st.title('Langchain')
    # 在Home页面中显示数据和功能组件

elif page == 'Autogen':
    st.title('Autogen')
    # 在About页面中显示数据和功能组件
