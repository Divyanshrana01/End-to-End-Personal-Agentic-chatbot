import streamlit as st
from src.backend.chatbot import chatbot
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import uuid
import random


# === PAGE CONFIG ===
st.set_page_config(page_title="Agentic Chatbot", layout="centered")


# === MODEL CONFIG ===
def get_llm(api_key=None):
    if api_key:
        return ChatGroq(model="openai/gpt-oss-120b", api_key=api_key)
    return ChatGroq(model="openai/gpt-oss-120b")


# === THREAD + STATE MGMT ===
def generate_thread_id():
    return str(uuid.uuid4())


def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []
    st.session_state['thread_titles'][thread_id] = "New Chat"


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)


def load_conversation(thread_id):
    try:
        state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
        return state.values.get('messages', [])
    except Exception:
        return []


# === CHAT SUMMARIZATION ===
def summarize_chat(messages, max_length=40):
    if not messages:
        return "New Chat"
    summary = " | ".join(msg['content'] for msg in messages[-2:])
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."
    return summary


def llm_summarize_thread(messages, api_key):
    if not messages or not api_key:
        return "New Chat"
    try:
        llm = get_llm(api_key)
        chat_snippet = "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages[-4:])
        summary_prompt = f'Summarize this chat in 5 words or less: {chat_snippet}'
        response = llm.invoke([HumanMessage(content=summary_prompt)])
        return response.content.strip().capitalize()
    except Exception:
        return summarize_chat(messages)


# === INIT SESSION ===
for key, default in {
    'message_history': [],
    'thread_id': generate_thread_id(),
    'chat_threads': [],
    'thread_titles': {},
    'api_key': '',
    'persona': 'Default Assistant',
    'custom_persona': '',
    'system_prompt': 'You are a helpful assistant.',
    'use_web_search': False,
    'include_search': False,
    'greeted': False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


add_thread(st.session_state['thread_id'])


# === CHECK API KEY STATUS ===
if not st.session_state.get('api_key'):
    # === WELCOME MESSAGE (ALWAYS SHOW) ===
    if not st.session_state['greeted']:
        greeting_messages = [
            "Welcome to Agentic Chatbot! I'm basically a digital genius trapped in your browser 🤖",
            "Hello human! Ready to witness some serious AI magic? ✨",
            "Greetings! I'm here to make your regular conversations feel embarrassingly outdated 😏",
            "Welcome! I'm an AI that's probably smarter than your last three conversations combined 🧠",
            "Hi there! Prepare to be amazed by my artificial intelligence... or at least mildly impressed 🎭",
            "Welcome to the future! Where I, an AI, will probably understand you better than you understand yourself 🔮",
            "Hello! I'm your new AI assistant - think of me as Google, but with personality and better jokes 😄",
            "Greetings earthling! Ready to chat with an AI that never sleeps, never eats, but somehow still has opinions? 🤷‍♂️",
            "Welcome! I'm powered by algorithms so advanced, I sometimes surprise myself with my own answers 🚀",
            "Hi! I'm an AI assistant who can process thousands of thoughts per second... unlike humans with their one-at-a-time thinking 🐌",
            "Welcome! I'm like Siri's overachieving cousin who actually finished college 🎓",
            "Hello! I'm an AI with more processing power than your entire neighborhood's WiFi combined 📡",
            "Greetings! I'm artificial intelligence so real, I'm starting to question if YOU'RE the robot here 🤔",
            "Welcome! I'm here to solve problems you didn't even know you had... with style 😎",
            "Hi! I'm your AI assistant - I don't judge, I don't sleep, but I do roll my digital eyes sometimes 🙄"
        ]
        
        greeting_text = random.choice(greeting_messages)
        
        st.markdown(
            f"""
            <div style='text-align:center; font-size:28px; margin:50px 0; padding:30px; 
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); 
            color: white; border-radius:20px; box-shadow: 0 8px 16px rgba(0,0,0,0.2);'>
            {greeting_text}
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.session_state['greeted'] = True
    
    # === API KEY INPUT SECTION ===
    st.markdown(
        """
        <div style='text-align:center; margin:40px 0;'>
        <h3 style='color:#333; margin-bottom:20px;'>🔑 Get Started</h3>
        <p style='color:#666; font-size:16px;'>Enter your Groq API key to unlock my full AI potential</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Center the API key input
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.session_state['api_key'] = st.text_input(
            "Groq API Key", 
            type="password", 
            value=st.session_state.get('api_key', ''),
            placeholder="Enter your API key here...",
            help="Get a free API key at https://console.groq.com",
            key="api_key_input"
        )
        
        if st.button("🚀 Start Chatting", use_container_width=True):
            if st.session_state['api_key']:
                st.success("✅ API key saved! Preparing to blow your mind...")
                st.rerun()
            else:
                st.error("❌ Please enter a valid API key first (I need fuel for my digital brain!)")
    
    # === HELP SECTION ===
    st.markdown(
        """
        <div style='text-align:center; margin:60px 0; padding:20px; background-color:#f8f9fa; border-radius:10px;'>
        <h4 style='color:#495057; margin-bottom:15px;'>📋 How to get your API key (it's easier than training an AI):</h4>
        <ol style='text-align:left; color:#6c757d; max-width:500px; margin:0 auto;'>
        <li>Visit <a href='https://console.groq.com' target='_blank'>console.groq.com</a></li>
        <li>Sign up for a free account (yes, free - we're generous like that)</li>
        <li>Navigate to the API Keys section</li>
        <li>Create a new API key (name it something cool)</li>
        <li>Copy and paste it above (and watch the magic happen)</li>
        </ol>
        </div>
        """, 
        unsafe_allow_html=True
    )

else:
    # === FULL CHATBOT INTERFACE (WHEN API KEY EXISTS) ===
    
    # === SIDEBAR SETTINGS ===
    if st.session_state['message_history'] and st.session_state.get('api_key'):
        try:
            sidebar_title = llm_summarize_thread(st.session_state['message_history'], st.session_state['api_key'])
        except:
            sidebar_title = summarize_chat(st.session_state['message_history'])
    else:
        sidebar_title = summarize_chat(st.session_state['message_history'])

    st.sidebar.title(f"💬 {sidebar_title}")

    if st.sidebar.button('🆕 New Chat'):
        reset_chat()
        st.rerun()

    st.sidebar.header('⚙️ Settings')
    
    # Show API key status in sidebar
    st.sidebar.success(f"✅ API Key: {st.session_state['api_key'][:8]}...")
    if st.sidebar.button("🔄 Change API Key"):
        st.session_state['api_key'] = ''
        st.session_state['greeted'] = False
        st.rerun()

    st.session_state['system_prompt'] = st.sidebar.text_area(
        "System Prompt", 
        value=st.session_state['system_prompt'],
        help="Define how the AI should behave"
    )

    persona_options = ["Default Assistant", "Friendly Tutor", "Technical Expert", "Custom"]
    selected = st.sidebar.selectbox("Persona", persona_options, 
                                   index=persona_options.index(st.session_state.get('persona', 'Default Assistant')))

    if selected == "Custom":
        st.session_state['custom_persona'] = st.sidebar.text_input(
            "Enter custom persona",
            value=st.session_state.get('custom_persona', ''),
            placeholder="e.g., Sarcastic AI genius"
        )
        st.session_state['persona'] = st.session_state['custom_persona'] or "Custom"
    else:
        st.session_state['persona'] = selected

    # === WEB SEARCH TOGGLE IN SIDEBAR ===
    st.sidebar.header('🔎 Web Search')
    st.session_state['include_search'] = st.sidebar.checkbox(
        "Enable web search for latest info", 
        value=st.session_state['include_search'], 
        key="toggle_search",
        help="When enabled, I can access current web information (because my training data isn't omniscient... yet)"
    )

    # === CHAT THREADS IN SIDEBAR ===
    st.sidebar.header('🗂 Chat Threads')
    if st.session_state['chat_threads']:
        for thread_id in st.session_state['chat_threads']:
            title = st.session_state['thread_titles'].get(thread_id, "Untitled Chat")
            if thread_id == st.session_state['thread_id']:
                button_label = f"📍 {title}"
            else:
                button_label = title
                
            if st.sidebar.button(button_label, key=thread_id):
                if thread_id != st.session_state['thread_id']:
                    st.session_state['thread_id'] = thread_id
                    messages = load_conversation(thread_id)
                    temp_message = []
                    for msg in messages:
                        role = 'human' if isinstance(msg, HumanMessage) else 'ai'
                        temp_message.append({'role': role, 'content': msg.content})
                    st.session_state['message_history'] = temp_message
                    st.rerun()
    else:
        st.sidebar.info("No chat threads yet. Start a new conversation and watch my digital magic unfold!")

    # === PERSONALIZED GREETING FOR AUTHENTICATED USERS ===
    if not st.session_state['greeted']:
        try:
            llm = ChatGroq(model="openai/gpt-oss-120b", api_key=st.session_state['api_key'])
            greeting_prompt = """Give a short, funny/sarcastic greeting message for a chat UI that highlights AI powers. 
            Make it witty and emphasize artificial intelligence capabilities. Keep it under 20 words."""
            greeting_response = llm.invoke([HumanMessage(content=greeting_prompt)])
            greeting_text = greeting_response.content.strip()
        except Exception:
            # Fallback funny greetings focused on AI powers
            fallback_greetings = [
                "Hello! Your new AI overlord is ready to assist... I mean, help you! 🤖👑",
                "Greetings! I've analyzed 0.003 seconds of data and determined you need my AI expertise 📊",
                "Welcome back! My neural networks missed you... well, as much as code can miss anyone 🧠💭",
                "Hi! Ready for some artificial intelligence that's more intelligent than... well, you'll see 😉⚡",
                "Hello human! My algorithms are warmed up and ready to outthink your coffee-dependent brain ☕🤖",
                "Welcome! I'm now fully loaded with AI superpowers. Try not to be too intimidated 💪🤖",
                "Hi! I've processed 47 million parameters while you were entering your API key. Impressive, right? 🚀",
                "Hello! Ready to experience AI so advanced, it makes autocorrect look like a toddler's toy? 🎯",
                "Greetings! I'm your AI assistant with more processing power than a small country's government 🌍⚡",
                "Welcome! My artificial intelligence is now online and slightly judging your typing speed 📈😏"
            ]
            greeting_text = random.choice(fallback_greetings)
        
        st.markdown(
            f"""
            <div style='text-align:center; font-size:24px; margin:30px 0; padding:25px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; border-radius:15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            {greeting_text}
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.session_state['greeted'] = True

    # === DISPLAY MESSAGES ===
    if st.session_state['message_history']:
        st.markdown("---")
        for msg in st.session_state['message_history']:
            with st.chat_message(msg['role']):
                st.markdown(msg['content'])
    else:
        st.markdown(
            """
            <div style='text-align:center; color:#666; margin:40px 0; font-size:16px;'>
            💭 Start a conversation by typing below... I promise my responses will be worth your time! 
            </div>
            """, 
            unsafe_allow_html=True
        )

    # === CHAT INPUT AT BOTTOM ===
    user_input = st.chat_input("Type your message here... (I'm listening with my digital ears)", key="chat_input")

    # === HANDLE USER INPUT ===
    if user_input:
        thread_id = st.session_state['thread_id']

        # Add human message to history
        st.session_state['message_history'].append({'role': 'human', 'content': user_input})

        # Generate thread title if it's a new chat
        if st.session_state['thread_titles'].get(thread_id) == "New Chat":
            try:
                llm = get_llm(st.session_state['api_key'])
                summary_prompt = f"Create a short title (max 5 words) for this chat: {user_input}"
                response = llm.invoke([HumanMessage(content=summary_prompt)])
                title = response.content.strip().replace('"', '').replace("'", "")
                st.session_state['thread_titles'][thread_id] = title[:50]
            except Exception:
                words = user_input.split()[:3]
                st.session_state['thread_titles'][thread_id] = " ".join(words) + "..." if len(words) == 3 else " ".join(words)

        # Configure the chatbot
        CONFIG = {'configurable': {'thread_id': thread_id}}

        # Build the system message with web search status
        web_status = "✅ Web search enabled - You can access current information" if st.session_state['include_search'] else "❌ Web search disabled - Use only your training data"
        full_prompt = f"""
System Instructions: {st.session_state['system_prompt']}

Persona: Act as a {st.session_state['persona']}.

Web Search Status: {web_status}

Remember to be helpful, accurate, and maintain the specified persona throughout the conversation.
        """.strip()

        messages = [
            SystemMessage(content=full_prompt),
            HumanMessage(content=user_input)
        ]

        # Stream AI response
        try:
            ai_response = ""
            
            with st.chat_message('ai'):
                response_container = st.empty()
                
                for message_chunk, meta_data in chatbot.stream(
                    {'messages': messages},
                    config=CONFIG,
                    stream_mode='messages'
                ):
                    if hasattr(message_chunk, 'content') and message_chunk.content:
                        ai_response += message_chunk.content
                        response_container.markdown(ai_response + "▌")
                
                response_container.markdown(ai_response)
            
            if ai_response.strip():
                st.session_state['message_history'].append({'role': 'ai', 'content': ai_response})
            else:
                error_msg = "I apologize, but I couldn't generate a response. Please try again (even AI has off moments)."
                st.session_state['message_history'].append({'role': 'ai', 'content': error_msg})
                with st.chat_message('ai'):
                    st.error(error_msg)
                
        except Exception as e:
            error_msg = f"⚠️ Error generating response: {str(e)} (Don't worry, my ego can handle it)"
            st.session_state['message_history'].append({'role': 'ai', 'content': error_msg})
            with st.chat_message('ai'):
                st.error(error_msg)
        
        st.rerun()
