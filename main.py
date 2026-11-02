import os
from pathlib import Path

# Load environment variables from .env
env_file = Path(__file__).resolve().parent / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip("'\"")

from sarvamai import SarvamAI

# Initialize client reading key from environment
client = SarvamAI(api_subscription_key=os.environ.get("SARVAM_API_KEY"))

# Call chat completion with sarvam-105b-conversations
response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[
        {"role": "user", "content": "Hello! Give a brief one-sentence greeting."}
    ],
)

# Print the reply
print(response.choices[0].message.content)
