import streamlit as st
from app.pipeline.empathy_pipeline import EmpathyPipeline

st.set_page_config(page_title="Empathy Engine", layout="centered")

st.title("🎙️ Empathy Engine")
st.write("Give AI a human voice")
text_input = st.text_area("Enter your text:")
if st.button("Generate Voice"):
    if text_input.strip() == "":
        st.warning("Please enter some text")
    else:
        pipeline = EmpathyPipeline("configs/config.yaml")
        emotion, audio_path = pipeline.run(text_input)
        st.success(f"Detected Emotion: **{emotion}**")
        audio_file = open(audio_path, "rb")
        st.audio(audio_file.read(), format="audio/mp3")