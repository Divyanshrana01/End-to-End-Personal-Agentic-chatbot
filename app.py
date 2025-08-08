import streamlit as st
from src.chatbot import chatbot
from langchain_core.messages import HumanMessage
import uuid

# UTILITY FUNCTIONS

# TO generate a unique chat ID each time
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

# For starting a new chat  while already in a chat
def reset_chat():
    thread_id = generate_thread_id()  # generate the new chat ID
    st.session_state['thread_id'] = thread_id  # save this new ID in the session state
    add_thread(st.session_state['thread_id'])  # store this ID with other IDs too, to retrieve later
    st.session_state['message_history'] = []   # removing every message form chat for the new ID 


# to collect the chat ID  into session state
def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
        
# to used the thread id to fetch and load the chat whenever we want to load any chat
def load_conversation(thread_id):
    try:
        state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
        return state.values.get('messages',[])
    except Exception:
        return []


# SESSION SETUP 

# stores all the chat messages so far (both human and AI).
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
# Each new conversation gets its own ID so you can switch between conversations later.   
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
# This list stores all active chat IDs so you can show them in the sidebar and switch between them.
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []
    
# This ensures the current chat is stored in your "list of all chats" so it appears in the UI.
add_thread(st.session_state['thread_id'])


#  SIDEBAR UI 

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My Conversations')

# list of all conversation IDs & [::-1] means reverse the list — so the newest chats appear first.
for thread_id in st.session_state['chat_threads'][::-1]: 
    if st.sidebar.button(str(thread_id)): # loading all the chat threads in the form of buttons.
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role': role, 'content': msg.content})

        st.session_state['message_history'] = temp_messages


#  MAIN UI 

# loading the conversation history in the UI
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input) # Display the user’s message

    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config= CONFIG,
                stream_mode= 'messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})