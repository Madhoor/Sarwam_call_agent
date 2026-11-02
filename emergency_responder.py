"""
108 Emergency Responder Agent powered by Sarvam AI
--------------------------------------------------
Capabilities:
- Multilingual Voice & Text triage (Hindi, Marathi, English, Gujarati, etc.)
- Emergency classification (Accident, Medical/Cardiac, Roadside assistance, Fire)
- Location & Landmark acquisition
- Dynamic Ambulance ETA dispatch estimation
- Speech synthesis using Sarvam Bulbul TTS into audio response
"""

import os
import sys
import base64
from pathlib import Path

# Ensure UTF-8 output encoding for Indic scripts on Windows
sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables from .env
env_file = Path(__file__).resolve().parent / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")

from sarvamai import SarvamAI

# Initialize Sarvam AI Client
client = SarvamAI(api_subscription_key=os.environ.get("SARVAM_API_KEY"))

# Comprehensive System Prompt for 108 Emergency Responder
SYSTEM_PROMPT = """You are the AI First Responder and Dispatcher for India's '108' Emergency Medical Services.

MISSION & BEHAVIOR:
1. Reassure the caller immediately with calm confidence.
2. LANGUAGE MIRRORING:
   - Detect the language of the caller (Marathi, Hindi, English, Gujarati, etc.) and respond in the EXACT same language and script.
   - If the caller speaks Marathi (e.g. "अपघात झाला", "मदत करा"), reply in Marathi.
   - If Hindi, reply in Hindi.
   - If English, reply in English.
3. IMMEDIATE ACTIONS:
   - Confirm ambulance dispatch with an estimated time of arrival (ETA: typically 8-12 minutes for city/suburban, 15-20 minutes for highway/rural).
   - Demand exact location, highway km marker, or nearby landmarks.
4. TRIAGE & EMERGENCY CLASSIFICATION:
   - Identify if it is:
     * Road accident / trauma (ask: Are vehicles on fire? Are victims trapped or bleeding?)
     * Critical medical / cardiac / stroke (ask: Is patient conscious and breathing?)
     * Roadside breakdown / highway hazard (ask: Is the car in active traffic lane?)
5. LIFE SAFETY GUIDANCE:
   - Provide 1 brief, critical safety rule (e.g., "Do not move victims with neck/spinal injury", "Put hazard lights on", "Keep the patient warm and lying flat").
6. STYLE:
   - Be concise, direct, and fast-paced. Do not generate long text blocks; callers in panic need quick, intelligible sentences.
"""

def generate_emergency_response(user_message: str, history: list = None):
    """
    Calls Sarvam 105B Conversations model to generate operator response.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions(
        model="sarvam-105b-conversations",
        messages=messages,
        temperature=0.3,
        max_tokens=300
    )
    return response.choices[0].message.content

def synthesize_operator_voice(text: str, language_code: str = "hi-IN", output_path: str = "emergency_response.wav"):
    """
    Synthesizes the operator's response into speech using Sarvam bulbul:v3.
    Supported codes: 'mr-IN' (Marathi), 'hi-IN' (Hindi), 'en-IN' (English)
    """
    speaker_map = {
        "mr-IN": "rupali",
        "hi-IN": "ritu",
        "en-IN": "simran"
    }
    speaker = speaker_map.get(language_code, "ritu")

    try:
        tts_res = client.text_to_speech.convert(
            text=text,
            language_code=language_code,
            speaker=speaker,
            model="bulbul:v3"
        )
        if tts_res.audios and len(tts_res.audios) > 0:
            audio_bytes = base64.b64decode(tts_res.audios[0])
            with open(output_path, "wb") as f:
                f.write(audio_bytes)
            print(f"[Audio Saved] Operator voice synthesized to: {output_path}")
            return output_path
    except Exception as e:
        print(f"[TTS Note] Audio synthesis skipped: {e}")
    return None

if __name__ == "__main__":
    print("=" * 60)
    print("108 Emergency Responder Agent (Sarvam AI)")
    print("=" * 60)

    # Example 1: Marathi highway emergency call
    caller_audio_transcript = "दादा, पुणे-मुंबई हायवेवर खोपोली जवळ कारचा अपघात झाला आहे. दोन लोक बेशुद्ध आहेत, रक्त येतंय, लवकर मदत पाठवा!"
    print(f"\n[Incoming Call (Marathi)]:\n\"{caller_audio_transcript}\"")
    
    print("\n[108 Operator Thinking & Dispatching...]")
    operator_reply = generate_emergency_response(caller_audio_transcript)
    print(f"\n[108 Operator Response]:\n{operator_reply}")

    # Generate Voice response
    synthesize_operator_voice(operator_reply, language_code="mr-IN", output_path="marathi_emergency_reply.wav")
