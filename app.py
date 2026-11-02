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

# Page Configuration - Dark Mode
st.set_page_config(
    page_title="108 Emergency Voice Responder — Sarvam AI",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ElevenLabs & ChatGPT Voice-Inspired Dark Theme CSS
st.markdown("""
<style>
    /* Global Obsidian Theme */
    .stApp {
        background-color: #08090d;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif;
    }
    
    /* Background Ambient Radial Glow */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 800px;
        height: 400px;
        background: radial-gradient(ellipse at center, rgba(220, 38, 38, 0.15) 0%, rgba(220, 38, 38, 0.03) 50%, transparent 80%);
        pointer-events: none;
        z-index: 0;
    }

    /* Top Glassmorphic Navigation Bar */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.9rem 1.4rem;
        background: rgba(18, 20, 29, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
    }
    .brand-section {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .brand-logo {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .brand-badge {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        background: rgba(220, 38, 38, 0.2);
        color: #f87171;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }
    .live-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.8rem;
        font-weight: 600;
        color: #4ade80;
        background: rgba(34, 197, 94, 0.1);
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        border: 1px solid rgba(34, 197, 94, 0.25);
    }
    .status-pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 10px #22c55e;
        animation: pulse-dot 1.8s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.3); opacity: 0.5; }
    }

    /* ChatGPT / ElevenLabs Voice Orb Visualizer */
    .orb-stage {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2.5rem 1rem 1.5rem 1rem;
        position: relative;
    }
    .voice-orb {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, #ff4d4d, #dc2626 55%, #7f1d1d 95%);
        box-shadow: 0 0 50px rgba(220, 38, 38, 0.5),
                    0 0 100px rgba(220, 38, 38, 0.2),
                    inset 0 0 25px rgba(255, 255, 255, 0.4);
        position: relative;
        animation: orb-breathe 4s ease-in-out infinite;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .voice-orb:hover {
        transform: scale(1.05);
    }
    .voice-orb::after {
        content: '';
        position: absolute;
        top: -14px; left: -14px; right: -14px; bottom: -14px;
        border-radius: 50%;
        border: 1.5px solid rgba(239, 68, 68, 0.45);
        animation: orb-ring 3s ease-out infinite;
    }
    .voice-orb::before {
        content: '';
        position: absolute;
        top: -28px; left: -28px; right: -28px; bottom: -28px;
        border-radius: 50%;
        border: 1px solid rgba(239, 68, 68, 0.2);
        animation: orb-ring 3s ease-out infinite 0.9s;
    }
    @keyframes orb-breathe {
        0%, 100% { transform: scale(1); filter: brightness(1); }
        50% { transform: scale(1.08); filter: brightness(1.25); box-shadow: 0 0 75px rgba(220, 38, 38, 0.7), 0 0 130px rgba(239, 68, 68, 0.35); }
    }
    @keyframes orb-ring {
        0% { transform: scale(0.9); opacity: 0.8; }
        100% { transform: scale(1.45); opacity: 0; }
    }

    /* Soundwave bars underneath Orb */
    .sound-bars {
        display: flex;
        align-items: center;
        gap: 5px;
        height: 36px;
        margin-top: 1.8rem;
    }
    .sound-bar {
        width: 4px;
        background: linear-gradient(180deg, #f87171 0%, #ef4444 100%);
        border-radius: 2px;
        animation: sound-wave 1.1s ease-in-out infinite alternate;
    }
    .sound-bar:nth-child(1) { height: 12px; animation-delay: 0.0s; }
    .sound-bar:nth-child(2) { height: 26px; animation-delay: 0.2s; }
    .sound-bar:nth-child(3) { height: 36px; animation-delay: 0.4s; }
    .sound-bar:nth-child(4) { height: 20px; animation-delay: 0.15s; }
    .sound-bar:nth-child(5) { height: 32px; animation-delay: 0.35s; }
    .sound-bar:nth-child(6) { height: 16px; animation-delay: 0.25s; }
    .sound-bar:nth-child(7) { height: 28px; animation-delay: 0.05s; }
    .sound-bar:nth-child(8) { height: 10px; animation-delay: 0.3s; }
    @keyframes sound-wave {
        0% { height: 6px; opacity: 0.3; }
        100% { height: 34px; opacity: 1; }
    }

    .orb-caption {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-top: 0.7rem;
    }

    /* Message Stream Cards */
    .chat-stream {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        max-width: 760px;
        margin: 0 auto 1.5rem auto;
    }
    .stream-bubble {
        padding: 1.1rem 1.35rem;
        border-radius: 16px;
        line-height: 1.6;
        font-size: 0.95rem;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
    }
    .caller-stream {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        color: #e2e8f0;
        margin-right: auto;
        border-bottom-left-radius: 4px;
        max-width: 82%;
    }
    .operator-stream {
        background: linear-gradient(135deg, rgba(20, 24, 38, 0.85) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(239, 68, 68, 0.25);
        color: #f1f5f9;
        margin-left: auto;
        border-bottom-right-radius: 4px;
        max-width: 86%;
        box-shadow: 0 4px 20px rgba(220, 38, 38, 0.1);
    }
    .stream-meta {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* Bottom Floating Action Dock */
    .control-dock {
        background: rgba(15, 18, 28, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1rem 1.5rem;
        max-width: 760px;
        margin: 0 auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    }

    /* Equalizer Processing Card */
    .processing-card {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 16px;
        padding: 1.4rem;
        text-align: center;
        max-width: 760px;
        margin: 0 auto 1.5rem auto;
        box-shadow: 0 8px 32px rgba(220, 38, 38, 0.2);
    }
    .proc-title {
        font-size: 0.95rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        color: #f87171;
        margin-bottom: 0.3rem;
    }
    .proc-desc {
        font-size: 0.8rem;
        color: #94a3b8;
    }

    /* Tab Styling Overrides */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        background-color: transparent;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.9rem;
        border: none;
        padding: 0.5rem 0.2rem;
    }
    .stTabs [aria-selected="true"] {
        color: #f87171 !important;
        border-bottom: 2px solid #ef4444 !important;
    }
</style>
""", unsafe_allow_html=True)

# System Prompt for 108 Emergency Operator
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

# Top Glass Navigation Bar
st.markdown("""
<div class="top-nav">
    <div class="brand-section">
        <div class="brand-logo">🚨 108 DISPATCH</div>
        <div class="brand-badge">NATIONAL EMS</div>
    </div>
    <div style="display: flex; align-items: center; gap: 0.8rem;">
        <span style="font-size: 0.78rem; color: #94a3b8; font-weight: 500;">Multilingual • Indic Voice</span>
        <div class="live-status">
            <div class="status-pulse-dot"></div>
            <span>HOTLINE ACTIVE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar (Clean, Dark Config)
with st.sidebar:
    st.markdown("### Terminal Settings")
    active_key = st.text_input("Sarvam Access Key", value=api_key or "", type="password", help="Loaded from .env by default")
    st.markdown("---")
    st.markdown("**Hotline Protocol**: 108 Emergency Dispatch")
    st.markdown("**Voice Synthesis**: Sarvam Bulbul v3")
    st.markdown("**Speech Recognition**: Sarvam Saaras v3")
    st.markdown("**Intelligence Core**: Sarvam 105B Conversations")
    if st.button("🔄 Reset / Clear Call Session", use_container_width=True):
        st.session_state["live_conversation"] = []
        st.session_state["last_audio_hash"] = None
        st.session_state["last_audio_bytes"] = None
        st.session_state["autoplay_latest"] = False
        st.rerun()

# Top-level Tabs
tab_voice, tab_triage, tab_specs = st.tabs([
    "🎙️ Voice Hotline (Live)", 
    "📊 Triage Log & Presets", 
    "⚡ Architecture & Specs"
])

# =========================================================================
# TAB 1: ELEVENLABS / CHATGPT VOICE-INSPIRED MINIMALIST LIVE CALL
# =========================================================================
with tab_voice:
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

    # Central Voice Orb Stage
    st.markdown("""
    <div class="orb-stage">
        <div class="voice-orb"></div>
        <div class="sound-bars">
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
            <div class="sound-bar"></div>
        </div>
        <div class="orb-caption">108 DISPATCH OPERATOR • LISTENING READY</div>
    </div>
    """, unsafe_allow_html=True)

    # Conversation Transcript Stream (ChatGPT Style)
    st.markdown('<div class="chat-stream">', unsafe_allow_html=True)
    total_msgs = len(st.session_state["live_conversation"])
    
    for idx, msg in enumerate(st.session_state["live_conversation"]):
        is_latest = (idx == total_msgs - 1)

        if msg["role"] == "user":
            st.markdown(f"""
            <div class="stream-bubble caller-stream">
                <div class="stream-meta" style="color: #94a3b8;">
                    <span>📞 CALLER</span>
                </div>
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="stream-bubble operator-stream">
                <div class="stream-meta" style="color: #f87171;">
                    <span>🚨 108 OPERATOR</span>
                    <span style="color: #4ade80; margin-left: auto;">● DISPATCHED</span>
                </div>
                {msg["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            if msg.get("audio"):
                # Audio player widget
                st.audio(msg["audio"], format="audio/wav", autoplay=(is_latest and st.session_state["autoplay_latest"]))
                
                # Direct autoplay trigger for seamless speech aloud
                if is_latest and st.session_state["autoplay_latest"]:
                    b64_audio = base64.b64encode(msg["audio"]).decode("utf-8")
                    components.html(f"""
                    <audio id="direct-voice-player" autoplay>
                        <source src="data:audio/wav;base64,{b64_audio}" type="audio/wav">
                    </audio>
                    <script>
                        (function() {{
                            var el = document.getElementById("direct-voice-player");
                            if (el) {{
                                el.currentTime = 0;
                                var p = el.play();
                                if (p !== undefined) {{
                                    p.catch(function(err) {{
                                        console.warn("Autoplay audio handled:", err);
                                    }});
                                }}
                            }}
                        }})();
                    </script>
                    """, height=0)

    st.markdown('</div>', unsafe_allow_html=True)

    # Reset autoplay arm once rendered
    if st.session_state["autoplay_latest"]:
        st.session_state["autoplay_latest"] = False

    # Processing Animation Placeholder
    proc_placeholder = st.empty()

    # Floating Bottom Control Dock
    st.markdown('<div class="control-dock">', unsafe_allow_html=True)
    col_input, col_reset = st.columns([5, 1], vertical_alignment="center")

    with col_input:
        st.markdown("<span style='font-size:0.82rem; font-weight:600; color:#cbd5e1; text-transform:uppercase; letter-spacing:0.04em;'>Speak to 108 Operator (Marathi, Hindi, English, etc.):</span>", unsafe_allow_html=True)
        mic_audio = st.audio_input("Hold to speak")

    with col_reset:
        if st.button("🔴 End Call", use_container_width=True):
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

    st.markdown('</div>', unsafe_allow_html=True)

    # Real-Time Voice Processing
    if mic_audio is not None:
        audio_bytes = mic_audio.getvalue()
        audio_hash = hashlib.md5(audio_bytes).hexdigest()

        if audio_hash != st.session_state["last_audio_hash"]:
            st.session_state["last_audio_hash"] = audio_hash

            if not active_key:
                st.error("⚠️ Sarvam API Key missing. Please check your `.env` file or enter it in the left sidebar.")
            else:
                # Show Glowing Processing Card
                proc_placeholder.markdown("""
                <div class="processing-card">
                    <div class="proc-title">⚡ 108 Emergency Intelligence Active</div>
                    <div class="sound-bars" style="justify-content: center; margin: 0.8rem 0;">
                        <div class="sound-bar"></div>
                        <div class="sound-bar"></div>
                        <div class="sound-bar"></div>
                        <div class="sound-bar"></div>
                        <div class="sound-bar"></div>
                        <div class="sound-bar"></div>
                    </div>
                    <div class="proc-desc">Transcribing Audio (Saaras v3) • Triaging Emergency (Sarvam 105B) • Synthesizing Voice (Bulbul v3)...</div>
                </div>
                """, unsafe_allow_html=True)

                try:
                    client = get_sarvam_client(active_key)

                    # Step 1: Transcribe Caller Audio with Saaras v3
                    stt_res = client.speech_to_text.transcribe(
                        file=("caller_audio.wav", audio_bytes, "audio/wav"),
                        model="saaras:v3",
                        language_code="unknown"
                    )
                    caller_text = stt_res.transcript.strip()
                    detected_lang = getattr(stt_res, "language_code", "hi-IN") or "hi-IN"

                    if not caller_text:
                        proc_placeholder.empty()
                        st.warning("Could not clearly detect speech. Please speak closer to the microphone.")
                    else:
                        # Step 2: Append caller statement
                        st.session_state["live_conversation"].append({
                            "role": "user",
                            "content": caller_text,
                            "lang": detected_lang
                        })

                        # Multi-turn context for Sarvam-105B
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

                        # Step 4: Synthesize Voice with Bulbul v3
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
                        except Exception:
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

                        # Append response and arm autoplay
                        st.session_state["live_conversation"].append({
                            "role": "assistant",
                            "content": operator_text,
                            "audio": tts_audio_bytes,
                            "lang": lang_code
                        })
                        st.session_state["autoplay_latest"] = True

                        proc_placeholder.empty()
                        st.rerun()

                except Exception as err:
                    proc_placeholder.empty()
                    st.error(f"Error processing call: {str(err)}")

# =========================================================================
# TAB 2: TRIAGE LOG & PRESETS (STRUCTURED DASHBOARD)
# =========================================================================
with tab_triage:
    st.subheader("Simulate Pre-Recorded Emergency Incidents")
    
    col_preset, col_meta = st.columns([2, 1], gap="medium")
    
    with col_preset:
        preset_options = [
            "🚨 Marathi: Highway Multi-Vehicle Crash (खोपोली / पुणे-मुंबई हायवे)",
            "🏥 Hindi: Severe Heart Attack / Breathing Distress (करोल बाग, दिल्ली)",
            "🚗 English: Vehicle Breakdown in Active Expressway Lane"
        ]
        chosen = st.selectbox("Select Incident Scenario", preset_options)
        
        preset_bank = {
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
        item = preset_bank[chosen]
        sim_input = st.text_area("Caller Audio Transcript", value=item["text"], height=110)
        
        if st.button("🚨 Run Scenario Dispatch", type="primary"):
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
                                {"role": "user", "content": sim_input}
                            ],
                            temperature=0.3
                        )
                        reply = resp.choices[0].message.content
                        st.markdown(f"**Operator Reply:**\n> {reply}")

                        tts = c.text_to_speech.convert(
                            text=reply,
                            language_code=item["lang"],
                            speaker=item["voice"],
                            model="bulbul:v3"
                        )
                        if tts.audios:
                            st.audio(base64.b64decode(tts.audios[0]), format="audio/wav", autoplay=True)
                    except Exception as e:
                        st.error(f"Error: {e}")

    with col_meta:
        st.markdown("#### Live Telemetry")
        st.info("🚑 **Dispatch SLA**: < 10 mins\n\n📶 **Network**: Sarvam AI v3\n\n🗣️ **Languages**: Hindi, Marathi, English, Gujarati, Tamil, etc.")

# =========================================================================
# TAB 3: ARCHITECTURE & SPECS
# =========================================================================
with tab_specs:
    st.subheader("System Architecture")
    st.markdown("""
    ```
    ┌─────────────────────────┐
    │ Panicked Caller (Voice) │
    └────────────┬────────────┘
                 ▼
    ┌─────────────────────────┐
    │   Sarvam Saaras v3      │ ── Auto Language Identification (Marathi / Hindi / English)
    └────────────┬────────────┘
                 ▼
    ┌─────────────────────────┐
    │ Sarvam-105B Conversation│ ── Emergency Triage, Priority ETA & First-Aid Protocol
    └────────────┬────────────┘
                 ▼
    ┌─────────────────────────┐
    │   Sarvam Bulbul v3      │ ── Direct Autoplay Voice Output in Caller's Language
    └─────────────────────────┘
    ```
    """)
