import os
import uuid
from dotenv import load_dotenv

# Google
from google.cloud import texttospeech

# ElevenLabs
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# Fallback
from gtts import gTTS
from app.tts.ssml_generator import SSMLGenerator


class TTSEngine:
    def __init__(self, config):
        load_dotenv()

        self.config = config
        self.output_dir = config["app"]["output_dir"]
        os.makedirs(self.output_dir, exist_ok=True)

        self.providers = config["tts"]["fallback_order"]

        # Google
        self.google_client = None
        if "google" in self.providers:
            try:
                self.google_client = texttospeech.TextToSpeechClient()
            except Exception as e:
                print("⚠️ Google TTS init failed:", e)

        # ElevenLabs
        self.eleven_client = None
        self.api_key = os.getenv("ELEVEN_LABS")
        if "elevenlabs" in self.providers and self.api_key:
            self.eleven_client = ElevenLabs(api_key=self.api_key)

        self.voice_id = config["tts"].get("voice_id")

        self.ssml_generator = SSMLGenerator()

    def generate(self, text, voice_params):
        filename = f"{uuid.uuid4()}.mp3"
        path = os.path.join(self.output_dir, filename)

        for provider in self.providers:
            try:
                if provider == "google" and self.google_client:
                    self._generate_google(text, voice_params, path)
                    return path, "Google TTS"

                elif provider == "elevenlabs" and self.eleven_client:
                    self._generate_elevenlabs(text, voice_params, path)
                    return path, "ElevenLabs"

                elif provider == "gtts":
                    self._generate_gtts(text, path)
                    return path, "gTTS"

            except Exception as e:
                print(f"⚠️ {provider} failed:", e)

        # ✅ FIXED: properly indented inside function
        raise RuntimeError("❌ All TTS providers failed")

    # 🔥 Google TTS with SSML
    def _generate_google(self, text, voice_params, path):
        ssml_text = self.ssml_generator.generate(text, voice_params)

        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=self.config["tts"]["language"],
            name=self.config["tts"]["voice_name"],
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.google_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        with open(path, "wb") as f:
            f.write(response.audio_content)

        print("✅ Google TTS used")

    # 🔥 ElevenLabs backup
    def _generate_elevenlabs(self, text, voice_params, path):
        audio = self.eleven_client.text_to_speech.convert(
            voice_id=self.voice_id,
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=voice_params.get("stability", 0.5),
                similarity_boost=voice_params.get("similarity_boost", 0.75),
                style=voice_params.get("style", 0.5),
                use_speaker_boost=True,
                speed=float(voice_params.get("rate", 1.0)),
            ),
        )
        with open(path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        print("✅ ElevenLabs used")
    # 🔁 gTTS fallback
    def _generate_gtts(self, text, path):
        tts = gTTS(text=text, lang="en")
        tts.save(path)
        print("✅ gTTS fallback used")