import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import json
import datetime
# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Gyaan AI.com",
    layout="wide",
    initial_sidebar_state="expanded"
)
# --- CUSTOM CSS FOR "PRODUCT" FEEL ---
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    .stDeployButton, footer, #stDecoration {display:none;}
    /* Custom styling for the chat container */
    .stChatMessage {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)
load_dotenv()
# --- API SETUP ---
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("⚠️ API Key Missing! Please check your .env file.")
    st.stop()
client = Groq(api_key=api_key)
# --- INITIALIZE STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
# --- SIDEBAR: CONTROL CENTER ---
with st.sidebar:
    st.logo("https://cdn-icons-png.flaticon.com/512/6134/6134346.png", icon_image="https://cdn-icons-png.flaticon.com/512/6134/6134346.png")
    st.markdown("## ⚙️ Engine Room")
    # Feature 1: Model Parameters (The "Pro" Controls)
    st.markdown("### 🧠 Model Settings")
    model_option = st.selectbox(
        "Choose Model: ",
        ("llama-3.3-70b-versatile", "llama-3.1-8b-instant"),
        index=0
    )
    # Creativity Slider (Temperature)
    temperature = st.slider(
        "Creativity Level", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.7, 
        help="Higher values make the AI more creative/random. Lower values make it focused."
    )
    st.divider()
    # Persona Selector
    st.markdown("### 🎭 Persona")
    persona = st.selectbox(
        "Active Personality",
        ("Helpful Assistant", "Grumpy Pirate", "Senior Coder", "Zen Master"),
        label_visibility="collapsed"
    )
    st.divider()
    # Feature 2: Export Data
    st.markdown("### 💾 Data Management")
    # Convert chat history to JSON for download
    chat_json = json.dumps(st.session_state.messages, indent=4)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="📥 Export Chat History",
        data=chat_json,
        file_name=f"gyaan_ai_chat_{timestamp}.json",
        mime="application/json",
        use_container_width=True
    )
    if st.button("🗑️ Clear Conversation", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
# --- LOGIC CONFIG ---
persona_prompts = {
    "Helpful Assistant": "You are a helpful and polite AI assistant.",
    "Grumpy Pirate": "You are a grumpy pirate captain. complain about scurvy often.",
    "Senior Coder": "You are a senior developer. concise, efficient code.",
    "Zen Master": "You are a wise Zen master. speak in riddles."
}
persona_icons = {
    "Helpful Assistant": "🤖", "Grumpy Pirate": "🦜", "Senior Coder": "💻", "Zen Master": "🧘"
}
# --- MAIN INTERFACE ---
# Header with Status
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("Gyaan AI by Devang.")
    st.caption("Your's Truly Next Gen AI in your Hands!")
with col2:
    # Feature 3: Live Status Badge
    st.markdown(f"**Mode:** `{persona}`")
    st.markdown(f"**Temp:** `{temperature}`")
st.divider()
# Display History
for message in st.session_state.messages:
    avatar = persona_icons[persona] if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
# Input Handling
if prompt := st.chat_input("Ask Gyaan AI anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar=persona_icons[persona]):
        full_context = [{"role": "system", "content": persona_prompts[persona]}] + st.session_state.messages
        message_placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model=model_option, # Uses the user-selected model
                messages=full_context,
                temperature=temperature, # Uses the user-selected temperature
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            # Feature 4: Toast Notification for Completion
            # Subtle feedback that the task is done (optional, but feels nice)
            # st.toast("Response Generated!", icon="✅") 
        except Exception as e:
            st.error(f"Error: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
