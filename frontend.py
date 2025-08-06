import streamlit as st
from src.backend.chatbot import chatbot
from langchain_core.messages import HumanMessage


# to save conversation history.

thread_id = '1'
CONFIG = {'configurable':{'thread_id':thread_id}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
    
# to load/show the conversation history as new messages keeps on generating.
for msg in st.session_state['message_history']:
    with st.chat_message(msg['role']):
        st.text(msg['content'])


user_input = st.chat_input('Type here:')

if user_input:
    st.session_state['message_history'].append({'role':'human','content':user_input}) # first add the message to the st.session_state['message_history']
    with st.chat_message('human'):
        st.text(user_input)
     
     

    with st.chat_message('ai'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, meta_data in chatbot.stream(
                {'messages': [HumanMessage(content=user_input) ]},
                config={'configurable': {'thread_id': 'thread-1'}},
                stream_mode='messages'
            )
        
    )

    st.session_state['message_history'].append({'role':'ai','content':ai_message})  











 






