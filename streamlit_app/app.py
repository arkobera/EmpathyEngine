import sys
import os

# ✅ Fix import path issue
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from app.pipeline.empathy_pipeline import EmpathyPipeline


# ✅ Page config
st.set_page_config(page_title="Empathy Engine", layout="centered")

st.title("🎙️ Empathy Engine")
st.write("Give AI a human voice with emotional intelligence")

# ✅ Cache pipeline (VERY IMPORTANT)
@st.cache_resource
def load_pipeline():
    return EmpathyPipeline("configs/config.yaml")


pipeline = load_pipeline()

# ✅ Input
text_input = st.text_area("Enter your text:", height=150)

# ✅ Generate button
if st.button("Generate Voice"):
    if text_input.strip() == "":
        st.warning("Please enter some text")
    else:
        with st.spinner("Analyzing emotion and generating voice..."):
            try:
                emotion, audio_path = pipeline.run(text_input)

                # 🎯 Output
                st.success(f"Detected Emotion: **{emotion}**")

                # 🔊 Play audio
                with open(audio_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")

                # 📂 Optional: download button
                with open(audio_path, "rb") as f:
                    st.download_button(
                        label="Download Audio",
                        data=f,
                        file_name=os.path.basename(audio_path),
                        mime="audio/mp3"
                    )

                st.info("ℹ️ If ElevenLabs fails, system automatically falls back to gTTS")

            except Exception as e:
                st.error("❌ Something went wrong during processing")
                st.exception(e)