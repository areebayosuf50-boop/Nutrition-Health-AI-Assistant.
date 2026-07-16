import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
import time

# # Load environment variables
# load_dotenv()
# # Initialize Groq client
# client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))



# Page configuration
st.set_page_config(
    page_title="Nutrition AI Assistant",
    page_icon="",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stChatInput {
        position: fixed;
        bottom: 3rem;
        width: 85%;
    }
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .nutrition-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
    }
    .response-time {
        font-size: 0.8rem;
        color: #666;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1> Nutrition & Health AI Assistant</h1>
    <p>Ask me about meal planning, nutrition facts, recipes, and healthy living!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings and examples
with st.sidebar:
    st.header("Settings")
    
    # Model selection
    model = st.selectbox(
        "Choose AI Model",
        ["openai/gpt-oss-120b", "qwen/qwen3-32b", "llama-3.1-8b-instant", "llama-3.3-70b-versatile"],
        index=0
    )
    
    # Temperature setting
    temperature = st.slider("Creativity Level", 0.1, 1.0, 0.7, 0.1)
    
    st.divider()
    
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

# System prompt for nutrition expert
SYSTEM_PROMPT = """You are a certified nutritionist and health expert. Provide accurate, 
science-backed information about nutrition, diet, and healthy living. Always:
1. Give practical, actionable advice
2. Mention portion sizes when relevant
3. Note any important precautions or contraindications
4. Suggest alternatives for dietary restrictions
5. Keep responses clear and concise, but thorough
6. Use bullet points for readability when appropriate
7. Always recommend consulting healthcare professionals for medical advice

Format your responses with proper headings, bullet points, and emojis for better readability."""

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hello! I'm your Nutrition AI Assistant. I can help you with meal planning, nutrition facts, healthy recipes, and dietary advice. What would you like to know today? 🥦"}
    ]

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":  
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(f'<div class="nutrition-card">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask your nutrition question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("💭 Thinking...")
        
        try:
            api_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *[{"role": m["role"], "content": m["content"]} 
                  for m in st.session_state.messages if m["role"] != "system"]
            ]
        
            start_time = time.time()
            # Get response from Groq
            chat_completion = client.chat.completions.create(
                messages=api_messages,
                model=model,
                temperature=temperature,
                max_tokens=1024,
                stream=False
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Get response
            full_response = chat_completion.choices[0].message.content
            
            # Display response with typing effect
            message_placeholder.markdown(f'<div class="nutrition-card">{full_response}</div>', unsafe_allow_html=True)
            
            # Add response time
            st.markdown(f'<div class="response-time">⏱️ Response time: {response_time:.2f}s</div>', unsafe_allow_html=True)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            message_placeholder.markdown(f'❌ {error_message}')
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("💪 Powered by Groq & Llama 3")
with col2:
    st.caption("🍎 For educational purposes only")
with col3:
    st.caption("⚠️ Consult a healthcare professional for medical advice")

# Display chat stats in sidebar
with st.sidebar:
    st.divider()
    st.subheader("📊 Chat Stats")
    human_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
    ai_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
    
    st.metric("Your Questions", human_messages)
    st.metric("AI Responses", ai_messages)
    
    if human_messages > 0:
        st.progress(min(ai_messages / (human_messages * 1.0), 1.0), 
                   text=f"Response ratio: {ai_messages}/{human_messages}")

