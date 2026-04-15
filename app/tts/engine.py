import os
import uuid
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from gtts import gTTS


class TTSEngine:
    def __init__(self, config):
        load_dotenv()

        self.config = config
        self.output_dir = config["app"]["output_dir"]
        os.makedirs(self.output_dir, exist_ok=True)

        self.provider = config["tts"]["provider"]
        self.fallback = config["tts"].get("fallback", "gtts")

        # ElevenLabs setup
        self.api_key = os.getenv("ELEVEN_LABS")
        self.voice_id = config["tts"]["voice_id"]

        if self.provider == "elevenlabs" and self.api_key:
            self.client = ElevenLabs(api_key=self.api_key)
        else:
            self.client = None

    def generate(self, text, voice_params):
        filename = f"{uuid.uuid4()}.mp3"
        path = os.path.join(self.output_dir, filename)

        # 🔥 TRY ElevenLabs
        if self.provider == "elevenlabs" and self.client:
            try:
                audio = self.client.text_to_speech.convert(
                    voice_id=self.voice_id,
                    output_format="mp3_44100_128",
                    text=text,
                    model_id="eleven_multilingual_v2",
                    voice_settings=VoiceSettings(
                        stability=voice_params["stability"],
                        similarity_boost=voice_params["similarity_boost"],
                        style=voice_params["style"],
                        use_speaker_boost=True,
                        speed=voice_params["speed"],
                    ),
                )

                with open(path, "wb") as f:
                    for chunk in audio:
                        f.write(chunk)

                print("✅ ElevenLabs audio generated")
                return path

            except Exception as e:
                print("⚠️ ElevenLabs failed, switching to fallback...")
                print(e)

        # 🔁 FALLBACK → gTTS
        if self.fallback == "gtts":
            try:
                tts = gTTS(text=text, lang=self.config["tts"]["language"])
                tts.save(path)

                print("✅ gTTS fallback audio generated")
                return path

            except Exception as e:
                raise RuntimeError("❌ Both ElevenLabs and gTTS failed") from e

        raise RuntimeError("❌ No valid TTS provider available")