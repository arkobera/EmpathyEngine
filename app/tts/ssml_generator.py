class SSMLGenerator:
    def generate(self, text, voice_params):
        pitch = voice_params.get("pitch", "0st")
        rate = voice_params.get("rate", "1.0")

        ssml = f"""
        <speak>
            <prosody pitch="{pitch}" rate="{rate}">
                {text}
            </prosody>
        </speak>
        """

        return ssml.strip()