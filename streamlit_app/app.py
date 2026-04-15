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

# ✅ Cache pipeline
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
                # 🔥 UPDATED RETURN
                emotion, audio_path, provider = pipeline.run(text_input)

                # 🎯 Emotion Output
                st.success(f"Detected Emotion: **{emotion}**")

                # 🧠 Provider Info (NEW)
                st.info(f"🔊 Generated using: **{provider}**")

                # 🔊 Play audio
                with open(audio_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")

                # 📂 Download button
                with open(audio_path, "rb") as f:
                    st.download_button(
                        label="Download Audio",
                        data=f.read(),
                        file_name=os.path.basename(audio_path),
                        mime="audio/mp3"
                    )

                # 🧠 Smart message based on provider
                if provider == "Google TTS":
                    st.success("✨ High-quality SSML-based expressive voice")
                elif provider == "ElevenLabs":
                    st.warning("⚠️ Using ElevenLabs (may be rate-limited)")
                else:
                    st.info("ElevenLabs API - Rate Limit")
                    st.info("ℹ️ Fallback mode (gTTS - basic voice)")

            except Exception as e:
                st.error("❌ Something went wrong during processing")
                st.exception(e)