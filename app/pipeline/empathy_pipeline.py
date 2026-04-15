import os
from app.config.config_loader import load_config
from app.emotion.detector import EmotionDetector
from app.tts.engine import TTSEngine
from app.tts.voice_mapper import VoiceMapper


class EmpathyPipeline:
    def __init__(self, config_path):
        self.config = load_config(config_path)
        
        self.detector = EmotionDetector(self.config)
        self.voice_mapper = VoiceMapper(self.config)
        self.tts = TTSEngine(self.config)

    def run(self, text):
        emotion = self.detector.predict(text)
        voice_params = self.voice_mapper.map(emotion, text)
        audio_path, provider = self.tts.generate(text, voice_params)
        return emotion, audio_path, provider
    