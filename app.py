import os
import sys
import base64
import hashlib
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Ensure UTF-8 output encoding for Indic characters
sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()
api_key = os.getenv("SARVAM_API_KEY")

# Streamlit Page Configuration
st.set_page_config(
    page_title="108 Emergency Response — National Dispatch",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Realistic Emergency Hotline UI Styling (Less AI-like, Professional Dispatch Center)
st.markdown("""
<style>
    .stApp {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    .dispatch-header {
        background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
        color: white;
        padding: 1.2rem 1.8rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(185, 28, 28, 0.15);
    }
    .dispatch-title {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .dispatch-subtitle {
        font-size: 0.95rem;
        color: #fecaca;
        margin-top: 0.3rem;
        font-weight: 500;
    }
    .call-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.2rem;
    }
    .call-active {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: #16a34a;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .pulse-dot {
        width: 10px;
        height: 10px;
        background-color: #16a34a;
        border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(22, 163, 74, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(22, 163, 74, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(22, 163, 74, 0); }
    }
    .msg-card {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        max-width: 85%;
        line-height: 1.5;
        font-size: 1rem;
    }
    .caller-msg {
        background-color: #f1f5f9;
        color: #1e293b;
        border-left: 4px solid #64748b;
        margin-right: auto;
    }
    .operator-msg {
        background-color: #eff6ff;
        color: #1e3a8a;
        border-left: 4px solid #2563eb;
        margin-left: auto;
        border-radius: 12px;
    }
    .speaker-tag {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
        display: block;
    }
    .status-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .pill-eta {
        background-color: #fef3c7;
        color: #b45309;
    }
    .pill-dispatched {
        background-color: #dcfce7;
        color: #15803d;
    }

    /* Cool Emergency Dispatch Equalizer Loader Animation */
    .loader-box {
        background: #090d16;
        border-radius: 14px;
        padding: 1.6rem;
        border: 1px solid #1e293b;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        margin: 1.2rem 0;
        text-align: center;
    }
    .eq-bars {
        display: inline-flex;
        align-items: flex-end;
        gap: 6px;
        height: 52px;
        margin-bottom: 1rem;
    }
    .eq-bar {
        width: 6px;
        background: linear-gradient(180deg, #ef4444 0%, #f97316 50%, #38bdf8 100%);
        border-radius: 4px;
        animation: eq-anim 0.9s ease-in-out infinite alternate;
    }
    .eq-bar:nth-child(1) { height: 16px; animation-delay: 0.0s; }
    .eq-bar:nth-child(2) { height: 40px; animation-delay: 0.2s; }
    .eq-bar:nth-child(3) { height: 50px; animation-delay: 0.4s; }
    .eq-bar:nth-child(4) { height: 28px; animation-delay: 0.1s; }
    .eq-bar:nth-child(5) { height: 46px; animation-delay: 0.3s; }
    .eq-bar:nth-child(6) { height: 22px; animation-delay: 0.5s; }
    .eq-bar:nth-child(7) { height: 44px; animation-delay: 0.25s; }
    .eq-bar:nth-child(8) { height: 18px; animation-delay: 0.15s; }

    @keyframes eq-anim {
        0% { height: 8px; opacity: 0.35; }
        100% { height: 50px; opacity: 1; }
    }

    .loader-title {
        color: #f8fafc;
        font-weight: 800;
        font-size: 1.1rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    .loader-desc {
        color: #94a3b8;
        font-size: 0.88rem;
        margin-top: 0.4rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# System Prompt for conversational multi-turn emergency operator
SYSTEM_PROMPT = """You are the official emergency dispatcher on the '108' Emergency Medical and Disaster Services telephone hotline in India.

ROLE & BEHAVIOR:
1. TALK LIKE A REAL 108 OPERATOR:
   - You are in an active, ongoing phone conversation with a caller in distress.
   - Speak in clear, natural, human conversational phrases.
   - Never sound like an AI assistant. Never say "As an AI" or list bullet points.
   - Keep each turn concise (2-4 sentences max). Panicked callers on phone lines cannot process long paragraphs.

2. MULTILINGUAL AUTO-DETECTION & MIRRORING:
   - Detect the language of the caller (Hindi, Marathi, English, Gujarati, Tamil, etc.).
   - Respond fluently in the EXACT same language and script as the caller.
   - If Marathi ("अपघात झालाय", "रक्त येतंय"), speak pure Marathi.
   - If Hindi ("गाड़ी का एक्सीडेंट हो गया", "सांस नहीं आ रही"), speak Hindi.
   - If English, speak English.

3. CONVERSATIONAL DISPATCH PROTOCOL:
   - Turn 1: Calm the caller, confirm immediate ambulance dispatch with an ETA (e.g. "8 to 10 minutes"), and ask for the exact location/road/landmark.
   - Turn 2+: Ask follow-up questions to assess victim condition (conscious/breathing, bleeding, pinned under vehicle, roadside hazard).
   - Instruct 1 vital immediate action while they wait (e.g. "Do not move the neck", "Put hazard lights on", "Apply pressure with a clean cloth").
"""

# Initialize Sarvam Client
def get_sarvam_client(key: str):
    if not key:
        return None
    from sarvamai import SarvamAI
    return SarvamAI(api_subscription_key=key, timeout=120.0)

# Voice mapping based on detected language
def get_voice_for_language(lang_code: str):
    mapping = {
        "mr-IN": ("mr-IN", "rupali"),
        "hi-IN": ("hi-IN", "ritu"),
        "en-IN": ("en-IN", "simran"),
        "gu-IN": ("gu-IN", "pooja"),
        "ta-IN": ("ta-IN", "gokul"),
        "te-IN": ("te-IN", "kavitha"),
        "bn-IN": ("bn-IN", "roopa_bn_conversational"),
        "kn-IN": ("kn-IN", "suchitra_kn_narration"),
    }
    return mapping.get(lang_code, ("hi-IN", "ritu"))

# Header banner
st.markdown("""
<div class="dispatch-header">
    <div class="dispatch-title">🚨 108 Emergency Response System</div>
    <div class="dispatch-subtitle">Government of India — National Health Mission Emergency Dispatch Terminal</div>
</div>
""", unsafe_allow_html=True)

# Sidebar for API Configuration (Clean & minimal)
with st.sidebar:
    st.subheader("Terminal Settings")
    active_key = st.text_input("Sarvam Access Key", value=api_key or "", type="password", help="Loaded from .env by default")
    st.markdown("---")
    st.markdown("**Hotline Protocol**: 108 Emergency Dispatch")
    st.markdown("**Voice Model**: Sarvam Bulbul v3")
    st.markdown("**Speech Model**: Sarvam Saaras v3")
    st.markdown("**Intelligence**: Sarvam 105B Conversations")
    if st.button("Reset / Clear Call History", use_container_width=True):
        st.session_state["live_conversation"] = []
        st.session_state["last_audio_hash"] = None
        st.session_state["last_audio_bytes"] = None
        st.session_state["autoplay_latest"] = False
        st.rerun()

# Application Tabs
tab_live, tab_sim, tab_guide = st.tabs([
    "🎙️ Live 108 Emergency Call", 
    "📝 Text Scenarios & Triage", 
    "⚙️ System Architecture"
])

# =========================================================================
# TAB 1: LIVE CONVERSATION (MIC & IMMEDIATE REAL-TIME VOICE REPLAY)
# =========================================================================
with tab_live:
    if "live_conversation" not in st.session_state:
        st.session_state["live_conversation"] = [
            {
                "role": "assistant",
                "content": "108 आपातकालीन सेवा / 108 Emergency Services. Please speak, what is your emergency and where are you located?",
                "audio": None,
                "lang": "hi-IN"
            }
        ]
    if "last_audio_hash" not in st.session_state:
        st.session_state["last_audio_hash"] = None
    if "last_audio_bytes" not in st.session_state:
        st.session_state["last_audio_bytes"] = None
    if "autoplay_latest" not in st.session_state:
        st.session_state["autoplay_latest"] = False

    # Status Bar
    st.markdown("""
    <div class="call-bar">
        <div class="call-active">
            <div class="pulse-dot"></div>
            <span>LINE 108 ACTIVE — CONVERSATION IN PROGRESS</span>
        </div>
        <div style="display: flex; gap: 0.5rem;">
            <span class="status-pill pill-dispatched">🚑 AMBULANCE READY</span>
            <span class="status-pill pill-eta">⏱ AUTO-DISPATCH</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Display Conversation History
    chat_container = st.container()
    total_msgs = len(st.session_state["live_conversation"])
    
    with chat_container:
        for idx, msg in enumerate(st.session_state["live_conversation"]):
            is_latest = (idx == total_msgs - 1)

            if msg["role"] == "user":
                st.markdown(f"""
                <div class="msg-card caller-msg">
                    <span class="speaker-tag" style="color: #475569;">📞 Caller</span>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-card operator-msg">
                    <span class="speaker-tag" style="color: #1d4ed8;">🚨 108 Dispatch Operator</span>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                if msg.get("audio"):
                    # Standard player
                    st.audio(msg["audio"], format="audio/wav", autoplay=(is_latest and st.session_state["autoplay_latest"]))
                    
                    # Direct speech trigger for immediate loud playback
                    if is_latest and st.session_state["autoplay_latest"]:
                        b64_audio = base64.b64encode(msg["audio"]).decode("utf-8")
                        components.html(f"""
                        <audio id="live-operator-speaker" autoplay>
                            <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
                        </audio>
                        <script>
                            (function() {{
                                var a = document.getElementById("live-operator-speaker");
                                if (a) {{
                                    a.currentTime = 0;
                                    var promise = a.play();
                                    if (promise !== undefined) {{
                                        promise.catch(function(err) {{
                                            console.warn("Direct autoplay suppressed by browser:", err);
                                        }});
                                    }}
                                }}
                            }})();
                        </script>
                        """, height=0)

    # Reset autoplay trigger once rendered
    if st.session_state["autoplay_latest"]:
        st.session_state["autoplay_latest"] = False

    st.markdown("---")

    # Animated Loader Placeholder (Shows cool equalizer when calling APIs)
    loader_placeholder = st.empty()

    # Mic Input Widget
    col_mic, col_act = st.columns([4, 1], vertical_alignment="center")
    with col_mic:
        st.markdown("**Speak into the microphone (Hindi, Marathi, English, etc.):**")
        mic_audio = st.audio_input("Hold to speak to 108 operator")

    with col_act:
        if st.button("🔴 End Call", use_container_width=True, type="secondary"):
            st.session_state["live_conversation"] = [
                {
                    "role": "assistant",
                    "content": "108 आपातकालीन सेवा / 108 Emergency Services. Please speak, what is your emergency and where are you located?",
                    "audio": None,
                    "lang": "hi-IN"
                }
            ]
            st.session_state["last_audio_hash"] = None
            st.session_state["last_audio_bytes"] = None
            st.session_state["autoplay_latest"] = False
            st.rerun()

    # Process Voice Input Real-time
    if mic_audio is not None:
        audio_bytes = mic_audio.getvalue()
        audio_hash = hashlib.md5(audio_bytes).hexdigest()

        if audio_hash != st.session_state["last_audio_hash"]:
            st.session_state["last_audio_hash"] = audio_hash

            if not active_key:
                st.error("⚠️ Sarvam API Key missing. Please check your `.env` file or enter it in the left sidebar.")
            else:
                # 1. Show Cool Animated Equalizer Loader
                loader_placeholder.markdown("""
                <div class="loader-box">
                    <div class="eq-bars">
                        <div class="eq-bar"></div>
                        <div class="eq-bar"></div>
                        <div class="eq-bar"></div>
                        <div class="eq-bar"></div>
                        <div class="eq-bar"></div>
                        <div class="eq-bar"></div>
                        <div class="eq-bar"></div>
                        <div class="eq-bar"></div>
                    </div>
                    <div class="loader-title">📡 108 Emergency Network Connected</div>
                    <div class="loader-desc">Transcribing Audio (Saaras v3) • Triaging Ambulance Dispatch (Sarvam 105B) • Generating Voice (Bulbul v3)...</div>
                </div>
                """, unsafe_allow_html=True)

                try:
                    client = get_sarvam_client(active_key)

                    # Step 1: Transcribe Caller Audio with Saaras v3 (Auto Language Detection)
                    stt_res = client.speech_to_text.transcribe(
                        file=("caller_audio.wav", audio_bytes, "audio/wav"),
                        model="saaras:v3",
                        language_code="unknown"
                    )
                    caller_text = stt_res.transcript.strip()
                    detected_lang = getattr(stt_res, "language_code", "hi-IN") or "hi-IN"

                    if not caller_text:
                        loader_placeholder.empty()
                        st.warning("Could not detect clear speech. Please speak closer to the mic.")
                    else:
                        # Step 2: Add caller message to conversation history
                        st.session_state["live_conversation"].append({
                            "role": "user",
                            "content": caller_text,
                            "lang": detected_lang
                        })

                        # Build message context for Sarvam-105B Conversations
                        conversation_context = [{"role": "system", "content": SYSTEM_PROMPT}]
                        for turn in st.session_state["live_conversation"]:
                            conversation_context.append({
                                "role": turn["role"],
                                "content": turn["content"]
                            })

                        # Step 3: Call Sarvam-105B Conversations
                        llm_res = client.chat.completions(
                            model="sarvam-105b-conversations",
                            messages=conversation_context,
                            temperature=0.3,
                            max_tokens=250
                        )
                        operator_text = llm_res.choices[0].message.content.strip()

                        # Step 4: Synthesize Operator Voice with Bulbul v3
                        lang_code, voice_speaker = get_voice_for_language(detected_lang)
                        tts_audio_bytes = None
                        try:
                            tts_res = client.text_to_speech.convert(
                                text=operator_text,
                                language_code=lang_code,
                                speaker=voice_speaker,
                                model="bulbul:v3"
                            )
                            if tts_res.audios and len(tts_res.audios) > 0:
                                tts_audio_bytes = base64.b64decode(tts_res.audios[0])
                        except Exception as tts_err:
                            try:
                                tts_res = client.text_to_speech.convert(
                                    text=operator_text,
                                    language_code="hi-IN",
                                    speaker="ritu",
                                    model="bulbul:v3"
                                )
                                if tts_res.audios and len(tts_res.audios) > 0:
                                    tts_audio_bytes = base64.b64decode(tts_res.audios[0])
                            except Exception:
                                pass

                        # Append operator response and arm autoplay
                        st.session_state["live_conversation"].append({
                            "role": "assistant",
                            "content": operator_text,
                            "audio": tts_audio_bytes,
                            "lang": lang_code
                        })
                        st.session_state["autoplay_latest"] = True

                        # Clear loader and rerun to speak immediately
                        loader_placeholder.empty()
                        st.rerun()

                except Exception as err:
                    loader_placeholder.empty()
                    st.error(f"Call Processing Error: {str(err)}")

# =========================================================================
# TAB 2: TEXT SIMULATION & SCENARIOS (FOR TESTING PRESETS)
# =========================================================================
with tab_sim:
    st.subheader("Simulate Pre-Recorded Emergency Scenarios")
    scenario_choice = st.selectbox(
        "Select an incident preset:",
        [
            "🚨 Marathi: Highway Multi-Vehicle Crash (खोपोली / पुणे-मुंबई हायवे)",
            "🏥 Hindi: Severe Heart Attack / Breathing Distress (करोल बाग, दिल्ली)",
            "🚗 English: Vehicle Breakdown in Active Expressway Lane"
        ]
    )

    preset_data = {
        "🚨 Marathi: Highway Multi-Vehicle Crash (खोपोली / पुणे-मुंबई हायवे)": {
            "text": "दादा, पुणे-मुंबई हायवेवर खोपोली जवळ कारचा मोठा अपघात झाला आहे. दोन माणसं बेशुद्ध आहेत आणि रक्त येतंय, लवकर एम्बुलेंस पाठवा!",
            "lang": "mr-IN",
            "voice": "rupali"
        },
        "🏥 Hindi: Severe Heart Attack / Breathing Distress (करोल बाग, दिल्ली)": {
            "text": "हेलो 108! मेरे पिताजी को अचानक सीने में बहुत तेज़ दर्द हो रहा है और पसीना आ रहा है, सांस लेने में बहुत तकलीफ है। हम करोल बाग, नई दिल्ली में हैं, जल्दी एम्बुलेंस भेजिए!",
            "lang": "hi-IN",
            "voice": "ritu"
        },
        "🚗 English: Vehicle Breakdown in Active Expressway Lane": {
            "text": "Hello 108 emergency! My car broke down on the Outer Ring Road near toll plaza, thick smoke is coming from the engine and we are stranded in the middle lane.",
            "lang": "en-IN",
            "voice": "simran"
        }
    }

    selected = preset_data[scenario_choice]
    sim_text = st.text_area("Caller Statement", value=selected["text"], height=100)

    if st.button("Dispatch Ambulance & Generate Response", type="primary"):
        if not active_key:
            st.error("Sarvam API key required.")
        else:
            with st.spinner("Dispatching..."):
                try:
                    c = get_sarvam_client(active_key)
                    resp = c.chat.completions(
                        model="sarvam-105b-conversations",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": sim_text}
                        ],
                        temperature=0.3
                    )
                    reply = resp.choices[0].message.content
                    st.success("Response Received:")
                    st.write(reply)

                    # TTS
                    tts = c.text_to_speech.convert(
                        text=reply,
                        language_code=selected["lang"],
                        speaker=selected["voice"],
                        model="bulbul:v3"
                    )
                    if tts.audios:
                        st.audio(base64.b64decode(tts.audios[0]), format="audio/wav", autoplay=True)
                except Exception as ex:
                    st.error(f"Error: {ex}")

# =========================================================================
# TAB 3: SYSTEM ARCHITECTURE
# =========================================================================
with tab_guide:
    st.subheader("108 Voice Operator Pipeline")
    st.markdown("""
    ```
    Panicked Caller (Audio Voice)
             ↓
    Sarvam Saaras v3 STT  ─── (Automatic Language Detection: Marathi / Hindi / English)
             ↓
    Sarvam-105B Conversations ─── (Real-time Triage, ETA Calculation & First-aid Directives)
             ↓
    Sarvam Bulbul v3 TTS  ─── (Calm, Authoritative Operator Voice in Caller's Language)
             ↓
    Caller Hears 108 Operator Voice in Real-time (Direct Autoplay)
    ```
    """)
