from app.pipeline.empathy_pipeline import EmpathyPipeline

if __name__ == "__main__":
    text = input("Enter text: ")

    pipeline = EmpathyPipeline("configs/config.yaml")
    emotion, path = pipeline.run(text)

    print(f"Emotion: {emotion}")
    print(f"Audio saved at: {path}")