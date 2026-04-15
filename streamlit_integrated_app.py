"""
Example: Using Empathy Engine Flask API from Streamlit

This example shows how to use the Flask API backend from the Streamlit frontend.
This is useful when you want to have the API running separately (for scalability)
and the Streamlit UI connecting to it remotely.

To use this:
1. Start the Flask API in one terminal:
   uv run flask run --app flask_app/app.py --port 5000

2. Start the Streamlit app in another terminal:
   uv run streamlit run streamlit_integrated_app.py

3. The Streamlit app will communicate with the Flask API
"""

import streamlit as st
import requests
import os
from datetime import datetime
import base64

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = os.getenv("EMPATHY_API_URL", "http://localhost:5001")
API_TIMEOUT = 60  # seconds


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Empathy Engine (API)",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🎙️ Empathy Engine (Flask API)")
st.write("Transform text into emotionally expressive speech with our REST API backend")


# ============================================================================
# Sidebar Configuration
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_url = st.text_input(
        "API URL",
        value=API_BASE_URL,
        help="The base URL of the Flask API"
    )
    
    st.markdown("---")
    st.markdown("### 📚 Documentation")
    st.markdown("""
    - **API Docs:** [FLASK_API.md](../FLASK_API.md)
    - **Base URL:** Use `/api/synthesize` for speech synthesis
    - **Endpoint:** Use `/api/emotion` for emotion detection
    """)
    
    st.markdown("---")
    st.markdown("### 🚀 Running the API")
    st.code("""
uv run flask run --app flask_app/app.py
    """, language="bash")


# ============================================================================
# Helper Functions
# ============================================================================

@st.cache_resource
def check_api_health(url: str) -> bool:
    """Check if the API is healthy"""
    try:
        response = requests.get(
            f"{url}/api/health",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False


def synthesize_speech(text: str, url: str) -> dict:
    try:
        response = requests.post(
            f"{url}/api/synthesize",
            json={"text": text},  # no return_audio needed now
            timeout=API_TIMEOUT
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error {response.status_code}"}

    except Exception as e:
        return {"error": str(e)}


def detect_emotion(text: str, url: str) -> dict:
    """Detect emotion using the API"""
    try:
        response = requests.post(
            f"{url}/api/emotion",
            json={"text": text},
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"error": f"Could not connect to API at {url}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}


def download_audio(filename: str, url: str):
    """Download audio from the API"""
    try:
        response = requests.get(
            f"{url}/api/audio/{filename}",
            timeout=API_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.content
        else:
            return None
    except:
        return None


# ============================================================================
# Main App
# ============================================================================

# Check API connection
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("**API Status:**")

with col2:
    if check_api_health(api_url):
        st.success("🟢 Connected", icon="✅")
    else:
        st.error("🔴 Disconnected", icon="❌")
        st.warning(f"""
        Cannot connect to API at `{api_url}`
        
        Make sure the Flask app is running:
        ```bash
        uv run flask run --app flask_app/app.py
        ```
        """)

st.markdown("---")

# Input section
st.subheader("📝 Input")
text_input = st.text_area(
    "Enter your text:",
    height=150,
    placeholder="Type something here..."
)

# Mode selection
st.markdown("---")
mode = st.radio(
    "Choose mode:",
    options=["🎙️ Generate Speech", "🧠 Detect Emotion Only"],
    horizontal=True
)

# Generate button
col1, col2 = st.columns([3, 1])

with col1:
    generate_button = st.button(
        "Generate",
        use_container_width=True,
        type="primary"
    )

with col2:
    help_button = st.button(
        "?",
        help="Click to show API information"
    )

if help_button:
    st.info("""
    ### Usage
    
    **1. Generate Speech:**
    - Enter text
    - Click "Generate"
    - System detects emotion and generates speech
    - Download the audio file
    
    **2. Detect Emotion:**
    - Enter text
    - Select "Detect Emotion Only"
    - System returns the detected emotion
    
    ### Emotions
    - **Positive** 😊 - Happy, excited, enthusiastic
    - **Negative** 😠 - Sad, angry, frustrated
    - **Neutral** 😐 - Calm, informative, objective
    """)

st.markdown("---")

# Process request
if generate_button:
    if text_input.strip() == "":
        st.warning("⚠️ Please enter some text")
    else:
        if mode == "🎙️ Generate Speech":
            # Synthesize speech
            with st.spinner("🎤 Synthesizing speech..."):
                result = synthesize_speech(text_input, api_url)
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"✅ Emotion: **{result['emotion']}**")
                    with col2:
                        st.info(f"🔊 Provider: **{result['provider']}**")

                audio_bytes = base64.b64decode(result["audio"])
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="📥 Download Audio",
                    data=audio_bytes,
                    file_name=f"speech_{datetime.now().timestamp()}.mp3",
                    mime="audio/mp3"
)
        
        else:
            # Detect emotion only
            with st.spinner("🧠 Detecting emotion..."):
                result = detect_emotion(text_input, api_url)
            
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                emotion = result['emotion']
                
                # Display emotion with emoji
                emoji_map = {
                    "positive": "😊",
                    "negative": "😠",
                    "neutral": "😐"
                }
                emoji = emoji_map.get(emotion, "🤔")
                
                st.success(f"# Detected Emotion: {emoji} **{emotion.upper()}**")
                
                # Additional info
                with st.expander("📊 Emotion Details"):
                    st.write(f"""
                    - **Text:** {result['text']}
                    - **Emotion:** {result['emotion']}
                    - **Timestamp:** {result['timestamp']}
                    """)

# ============================================================================
# Footer
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🎙️ Empathy Engine**")
    st.markdown("""
    Emotion-Aware Text-to-Speech System
    """)

with col2:
    st.markdown("**📚 Resources**")
    st.markdown("""
    - [Flask API Docs](../FLASK_API.md)
    - [API Client](../client.py)
    """)

with col3:
    st.markdown("**🔧 Tech Stack**")
    st.markdown("""
    - Flask (API)
    - Streamlit (UI)
    - Transformers (NLP)
    - Google TTS / ElevenLabs
    """)
