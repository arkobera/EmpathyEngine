from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVEN_LABS"))

voices = client.voices.get_all()

print("\nAvailable Voices:\n")

for v in voices.voices:
    print(f"{v.name} → {v.voice_id}")