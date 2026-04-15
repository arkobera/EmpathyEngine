from transformers import pipeline
from app.emotion.labels import LABEL_MAP
from dotenv import load_dotenv
import os



class EmotionDetector:
    def __init__(self, config):
        # Load environment variables
        load_dotenv()

        hf_token = os.getenv("HF_TOKEN")

        model_name = config["emotion"]["model_name"]

        self.classifier = pipeline(
            "text-classification",
            model=model_name,
            token=hf_token
        )

    def predict(self, text):
        result = self.classifier(text)[0]
        raw_label = result["label"].lower()

        # Map to standardized label
        return LABEL_MAP.get(raw_label, "neutral")
    