import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

# Load backend modules
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extracter import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ==========================================
# PAGE CONFIGURATION & THEME (Minimalist & Neutral)
# ==========================================
st.set_page_config(
    page_title="Intellect - AI Meeting Intelligence",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Neutral, Elegant, Minimalist Dark Theme
st.markdown("""
<style>
    /* Main container background */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #21262D;
    }
    
    /* Cards and Container Boxes */
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Buttons Styling */
    .stButton>button {
        background-color: #21262D;
        color: #C9D1D9;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #30363D;
        color: #FFFFFF;
        border-color: #8B949E;
    }
    
    /* Custom Headers */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #F0F6FC;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #8B949E;
        margin-bottom: 2rem;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize Session State Variables
if "processed_data" not in st.session_state:
    st.session_state["processed_data"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ==========================================
# SIDEBAR: Input & Control Panel
# ==========================================
with st.sidebar:
    st.title("🎙️ Intellect AI")
    st.caption("Minimalist Video & Audio Intelligence")
    st.divider()

    input_type = st.radio(
        "Source Type",
        ["YouTube Link", "Upload Media File"],
        index=0
    )

    source_path = None

    if input_type == "YouTube Link":
        youtube_url = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v=...")
        if youtube_url:
            source_path = youtube_url
    else:
        uploaded_file = st.file_uploader(
            "Upload Audio or Video", 
            type=["mp4", "mp3", "wav", "m4a", "mov"]
        )
        if uploaded_file is not None:
            # Save uploaded file temporarily on disk for audio_processor.py
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.read())
                source_path = tmp_file.name

    language = st.selectbox("Transcription Language", ["english", "hinglish"])
    
    st.divider()
    
    process_btn = st.button("⚡ Run Pipeline", use_container_width=True)

    if process_btn:
        if not source_path:
            st.error("Please provide a valid YouTube link or local file.")
        else:
            with st.status("Processing audio pipeline...", expanded=True) as status:
                st.write("📥 Preparing source media...")
                chunks = process_input(source_path)

                st.write("🗣️ Transcribing speech with Whisper...")
                transcript = transcribe_all(chunks)

                st.write("🧠 Generating insights and RAG vectors...")
                title = generate_title(transcript)
                summary = summarize(transcript)
                action_items = extract_action_items(transcript)
                decisions = extract_key_decisions(transcript)
                questions = extract_questions(transcript)
                rag_chain = build_rag_chain(transcript)

                # Store result in state
                st.session_state["processed_data"] = {
                    "title": title,
                    "transcript": transcript,
                    "summary": summary,
                    "action_items": action_items,
                    "key_decisions": decisions,
                    "open_questions": questions,
                    "rag_chain": rag_chain,
                }
                # Reset chat history for new meeting
                st.session_state["chat_history"] = []
                status.update(label="Processing Complete!", state="complete", expanded=False)


# ==========================================
# MAIN CONTENT AREA
# ==========================================
data = st.session_state["processed_data"]

if data is None:
    # Empty State Dashboard
    st.markdown('<div class="main-title">Meeting & Video Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Extract summaries, action items, key decisions, and chat with your media.</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h4>📥 Multimodal Input</h4><p style="color:#8B949E; font-size:0.9rem;">Supports YouTube URLs along with local MP4, MP3, WAV, and MOV files.</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h4>⚡ Local Whisper</h4><p style="color:#8B949E; font-size:0.9rem;">Zero-dependency local transcription converted into clean, chucked segments.</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h4>💬 RAG Search</h4><p style="color:#8B949E; font-size:0.9rem;">Interact with vector memory using Chromadb and Mistral AI models.</p></div>', unsafe_allow_html=True)

else:
    # Active Workspace Dashboard
    st.markdown(f'<div class="main-title">{data["title"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Processed Intelligence Report</div>', unsafe_allow_html=True)

    # Navigation Tabs
    tab_summary, tab_details, tab_transcript, tab_chat = st.tabs([
        "📋 Executive Summary", 
        "📌 Key Takeaways", 
        "📝 Full Transcript", 
        "💬 Interactive Chat"
    ])

    # Tab 1: Executive Summary
    with tab_summary:
        st.markdown("### Summary")
        st.markdown(data["summary"])

    # Tab 2: Action Items, Decisions, Questions
    with tab_details:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### ✅ Action Items")
            st.markdown(data["action_items"])
            
            st.markdown("### 🔑 Key Decisions")
            st.markdown(data["key_decisions"])
            
        with col_b:
            st.markdown("### ❓ Open Questions")
            st.markdown(data["open_questions"])

    # Tab 3: Full Transcript with Download Option
    with tab_transcript:
        st.download_button(
            label="Download Transcript (.txt)",
            data=data["transcript"],
            file_name="transcript.txt",
            mime="text/plain"
        )
        st.text_area("Transcript Output", data["transcript"], height=400)

    # Tab 4: RAG Interactive Chat
    with tab_chat:
        st.markdown("### Chat with your Meeting Transcript")
        
        # Display existing messages
        for message in st.session_state["chat_history"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # User Question Input
        if user_query := st.chat_input("Ask a question about this meeting..."):
            st.session_state["chat_history"].append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.write(user_query)

            with st.chat_message("assistant"):
                with st.spinner("Searching transcript context..."):
                    answer = ask_question(data["rag_chain"], user_query)
                    st.write(answer)
                    st.session_state["chat_history"].append({"role": "assistant", "content": answer})