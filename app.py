import os
import sys
import base64
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for Indic characters
sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()
api_key = os.getenv("SARVAM_API_KEY")

# Streamlit Page Configuration
st.set_page_config(
    page_title="108 Emergency Responder — Sarvam AI",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Emergency Dashboard Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #d90429;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #495057;
        margin-bottom: 1.5rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
    }
    .badge-critical {
        background-color: #fee2e2;
        color: #b91c1c;
        border: 1px solid #f87171;
    }
    .badge-dispatched {
        background-color: #dcfce7;
        color: #15803d;
        border: 1px solid #4ade80;
    }
    .badge-eta {
        background-color: #fef3c7;
        color: #b45309;
        border: 1px solid #fcd34d;
    }
    .chat-bubble {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    .caller-bubble {
        background-color: #f1f5f9;
        border-left: 5px solid #64748b;
    }
    .dispatcher-bubble {
        background-color: #eff6ff;
        border-left: 5px solid #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Star_of_life2.svg/300px-Star_of_life2.svg.png", width=70)
    st.title("108 Control Room")
    st.markdown("**National Emergency Medical Services**")
    
    st.markdown("---")
    user_api_key = st.text_input("Sarvam API Key", value=api_key or "", type="password", help="Reads from .env by default")
    if user_api_key:
        active_key = user_api_key
    else:
        active_key = api_key

    st.markdown("---")
    st.subheader("Model Configuration")
    llm_model = st.selectbox("LLM Model", ["sarvam-105b-conversations", "sarvam-105b"], index=0)
    tts_model = st.selectbox("TTS Model", ["bulbul:v3", "bulbul:v2"], index=0)
    
    st.markdown("---")
    st.info("💡 **Languages Supported**: Marathi, Hindi, English, Gujarati, Bengali, Tamil, Telugu, Kannada, etc.")

# System Prompt
SYSTEM_PROMPT = """You are the AI First Responder and Dispatcher for India's '108' Emergency Medical and Disaster Services.

CORE PROTOCOL:
1. Reassure the caller immediately with calm confidence.
2. LANGUAGE MIRRORING:
   - Identify the language and script of the caller (Marathi, Hindi, English, Gujarati, etc.).
   - Respond in the EXACT same language and script.
3. IMMEDIATE ACTIONS:
   - Confirm ambulance dispatch immediately with a realistic ETA (8-12 minutes for city/suburban, 15-20 minutes for highway/rural).
   - Demand exact location, highway km marker, or nearby landmark.
4. TRIAGE & CATEGORY IDENTIFICATION:
   - Road accident / trauma: Ask if vehicles are on fire, or if victims are trapped/bleeding.
   - Medical / cardiac / stroke: Ask if patient is conscious and breathing.
   - Roadside breakdown / highway hazard: Ask if the vehicle is stopped in an active lane.
5. LIFE-SAFETY DIRECTIVE:
   - Give 1 quick, essential safety command (e.g. "Do not move victims with neck/spinal trauma", "Turn on hazard lights", "Apply firm cloth on bleeding").
6. STYLE:
   - Short, punchy, clear sentences. Never use long paragraphs; panicked callers need rapid instructions.
"""

def get_sarvam_client(key: str):
    if not key:
        return None
    from sarvamai import SarvamAI
    return SarvamAI(api_subscription_key=key)

# Main Header
st.markdown('<div class="main-header">🚨 108 Emergency AI Voice Responder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Multilingual Emergency Triage, ETA Estimation & Dispatcher Voice Agent powered by Sarvam AI</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📞 Live Emergency Simulator", "📊 Dispatcher Telemetry & Logs", "🛠 Architecture & Deployment"])

with tab1:
    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("1. Incoming Emergency Call")
        
        # Presets
        preset = st.radio(
            "Select a real-world emergency scenario:",
            [
                "🚨 Marathi — Highway Car Crash (Trauma / Accident)",
                "🏥 Hindi — Father Heart Attack / Breathing Distress (Cardiac)",
                "🚗 English — Outer Ring Road Breakdown (Roadside Assistance)",
                "✍️ Custom Caller Input"
            ],
            index=0
        )

        default_texts = {
            "🚨 Marathi — Highway Car Crash (Trauma / Accident)": {
                "text": "दादा, पुणे-मुंबई हायवेवर खोपोली जवळ कारचा मोठा अपघात झाला आहे. दोन माणसं बेशुद्ध आहेत आणि रक्त येतंय, लवकर एम्बुलेंस पाठवा!",
                "lang": "mr-IN",
                "voice": "rupali"
            },
            "🏥 Hindi — Father Heart Attack / Breathing Distress (Cardiac)": {
                "text": "हेलो 108! मेरे पिताजी को अचानक सीने में बहुत तेज़ दर्द हो रहा है और पसीना आ रहा है, सांस लेने में तकलीफ है। हम करोल बाग, नई दिल्ली में हैं, जल्दी एम्बुलेंस भेजिए!",
                "lang": "hi-IN",
                "voice": "ritu"
            },
            "🚗 English — Outer Ring Road Breakdown (Roadside Assistance)": {
                "text": "Hello 108 emergency! My car broke down on the Outer Ring Road near toll plaza, thick smoke is coming from the engine and we are stranded in the middle lane.",
                "lang": "en-IN",
                "voice": "simran"
            },
            "✍️ Custom Caller Input": {
                "text": "",
                "lang": "hi-IN",
                "voice": "ritu"
            }
        }

        selected_preset = default_texts[preset]

        caller_text = st.text_area(
            "Caller Audio Transcript:",
            value=selected_preset["text"],
            height=130,
            placeholder="Type or simulate speech transcription..."
        )

        col_l, col_v = st.columns(2)
        with col_l:
            target_lang = st.selectbox(
                "Voice Language Code",
                ["mr-IN", "hi-IN", "en-IN", "gu-IN", "ta-IN", "te-IN", "bn-IN"],
                index=["mr-IN", "hi-IN", "en-IN", "gu-IN", "ta-IN", "te-IN", "bn-IN"].index(selected_preset["lang"])
            )
        with col_v:
            speaker_voice = st.selectbox(
                "Operator Voice Persona",
                ["rupali", "soham", "ritu", "aditya", "simran", "shubh", "priya", "ishita"],
                index=0 if target_lang == "mr-IN" else (2 if target_lang == "hi-IN" else 4)
            )

        call_button = st.button("🚨 Answer 108 Call & Dispatch", type="primary", use_container_width=True)

    with col_output:
        st.subheader("2. 108 Dispatcher Response")

        if call_button:
            if not active_key:
                st.error("⚠️ Please enter a Sarvam API Key in the sidebar or check `.env`.")
            elif not caller_text.strip():
                st.warning("Please provide incoming caller text or select a preset.")
            else:
                with st.spinner("Dispatching 108 Ambulance and synthesizing operator voice..."):
                    try:
                        client = get_sarvam_client(active_key)

                        # 1. LLM Call
                        response = client.chat.completions(
                            model=llm_model,
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": caller_text}
                            ],
                            temperature=0.3,
                            max_tokens=300
                        )
                        reply_text = response.choices[0].message.content

                        # 2. TTS Voice Call
                        tts_res = client.text_to_speech.convert(
                            text=reply_text,
                            language_code=target_lang,
                            speaker=speaker_voice,
                            model=tts_model
                        )
                        audio_data = None
                        if tts_res.audios and len(tts_res.audios) > 0:
                            audio_data = base64.b64decode(tts_res.audios[0])

                        # Display Telemetry
                        st.markdown("""
                        <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem;">
                            <span class="status-badge badge-critical">🚨 LIVE EMERGENCY</span>
                            <span class="status-badge badge-dispatched">🚑 AMBULANCE DISPATCHED</span>
                            <span class="status-badge badge-eta">⏱ ETA: 8-12 MINS</span>
                        </div>
                        """, unsafe_allow_html=True)

                        # Audio Player
                        if audio_data:
                            st.audio(audio_data, format="audio/wav")
                            st.caption("🎙️ Sarvam Bulbul:v3 Operator Voice Output")

                        # Dispatcher Response Box
                        st.markdown(f"""
                        <div class="chat-bubble dispatcher-bubble">
                            <strong>108 Operator:</strong><br>{reply_text}
                        </div>
                        """, unsafe_allow_html=True)

                        # Save to session state
                        if "call_history" not in st.session_state:
                            st.session_state["call_history"] = []
                        st.session_state["call_history"].append({
                            "caller": caller_text,
                            "response": reply_text,
                            "lang": target_lang
                        })

                    except Exception as e:
                        st.error(f"Error executing Sarvam API: {str(e)}")
        else:
            st.info("👆 Click **'Answer 108 Call & Dispatch'** to initiate the AI responder triage pipeline.")

with tab2:
    st.subheader("📋 Live Dispatcher Incident Log")
    if "call_history" in st.session_state and st.session_state["call_history"]:
        for idx, call in enumerate(reversed(st.session_state["call_history"]), 1):
            with st.expander(f"Incident #{len(st.session_state['call_history']) - idx + 1} — Language: {call['lang']}", expanded=True):
                st.markdown(f"**Caller Statement:**\n> {call['caller']}")
                st.markdown(f"**Operator Action:**\n> {call['response']}")
    else:
        st.write("No emergency calls logged yet. Run a call in Tab 1 to see live triage logs.")

with tab3:
    st.subheader("🏗️ Architecture & Deployment Guide")
    st.markdown("""
    ### Pipeline Architecture
    1. **Caller Audio Input**: Can be captured through WebRTC / Twilio / LiveKit or local mic.
    2. **ASR / Language Detection**: Sarvam `saaras:v3` transcribes audio and determines language code (`hi-IN`, `mr-IN`, etc.).
    3. **Triage & Dialogue**: Sarvam `sarvam-105b-conversations` classifies the emergency (Accident, Trauma, Roadside, Cardiac), triggers ambulance dispatch ETA, and commands immediate safety steps.
    4. **Operator Voice Synthesis**: Sarvam `bulbul:v3` produces real-time natural Indic voice streams.

    ---
    ### How to Deploy to GitHub / GitLab & Streamlit Cloud
    1. **GitHub / GitLab Push**:
       ```bash
       git add .
       git commit -m "feat: 108 emergency responder app with Sarvam AI"
       git remote add origin https://github.com/YOUR_USERNAME/sarvam-108-emergency.git
       git push -u origin main
       ```
    2. **Deploying on Streamlit Cloud (share.streamlit.io)**:
       - Connect your GitHub repo.
       - Set main file path as `app.py`.
       - In **Advanced Settings -> Secrets**, add:
         ```toml
         SARVAM_API_KEY = "your_sarvam_api_key_here"
         ```
       - Click **Deploy**!
    """)
