class VoiceMapper:
    def __init__(self, config):
        self.mapping = config["voice_mapping"]
        self.intensity_cfg = config["intensity"]

    def map(self, emotion, text):
        params = self.mapping.get(emotion, self.mapping["neutral"]).copy()

        if self.intensity_cfg["enable"]:
            boost = 0

            if "!" in text:
                boost += self.intensity_cfg["exclamation_boost"]

            if text.isupper():
                boost += self.intensity_cfg["caps_boost"]

            # Apply intensity
            params["style"] = min(1.0, params["style"] + boost)
            params["speed"] += boost

        return params