"""
Flask application for the Empathy Engine API
Provides REST endpoints for emotion detection and speech synthesis
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from datetime import datetime
import base64

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.pipeline.empathy_pipeline import EmpathyPipeline


# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Initialize pipeline
pipeline = None


def init_pipeline():
    """Initialize the EmpathyPipeline"""
    global pipeline
    if pipeline is None:
        pipeline = EmpathyPipeline("configs/config.yaml")
    return pipeline


@app.before_request
def setup():
    """Initialize pipeline before first request"""
    init_pipeline()


# ============================================================================
# ROUTES
# ============================================================================

@app.route("/", methods=["GET"])
def index():
    """Home endpoint with API documentation"""
    return jsonify({
        "name": "🎙️ Empathy Engine API",
        "version": "1.0.0",
        "description": "Emotion-Aware Text-to-Speech System",
        "endpoints": {
            "POST /api/synthesize": "Generate speech from text with emotion detection",
            "POST /api/emotion": "Detect emotion from text only",
            "GET /api/health": "Check if the service is running",
            "GET /docs": "API documentation"
        }
    })


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route("/api/docs", methods=["GET"])
def docs():
    """API documentation"""
    return jsonify({
        "endpoints": {
            "POST /api/synthesize": {
                "description": "Synthesize speech from text with emotion detection",
                "request_body": {
                    "text": "string (required) - text to synthesize",
                    "return_audio": "boolean (optional, default=true) - whether to return audio file"
                },
                "response": {
                    "emotion": "detected emotion (positive, negative, neutral)",
                    "provider": "TTS provider used (Google TTS, ElevenLabs, or gTTS)",
                    "audio_path": "path to the generated audio file",
                    "timestamps": "creation timestamp",
                    "message": "success message"
                },
                "example": {
                    "curl": 'curl -X POST http://localhost:5000/api/synthesize -H "Content-Type: application/json" -d \'{"text": "I am so happy today!", "return_audio": true}\''
                }
            },
            "POST /api/emotion": {
                "description": "Detect emotion from text without generating speech",
                "request_body": {
                    "text": "string (required) - text to analyze"
                },
                "response": {
                    "emotion": "detected emotion",
                    "text": "input text",
                    "timestamp": "detection timestamp"
                }
            },
            "GET /api/health": {
                "description": "Check service health"
            }
        }
    })




@app.route("/api/synthesize", methods=["POST"])
def synthesize():
    try:
        if not request.json:
            return jsonify({"error": "JSON body required"}), 400

        text = request.json.get("text", "").strip()

        if not text:
            return jsonify({"error": "Text cannot be empty"}), 400

        # Run pipeline
        emotion, audio_path, provider = pipeline.run(text)

        # 🔥 READ AUDIO FILE
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        # 🔥 ENCODE TO BASE64
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return jsonify({
            "success": True,
            "emotion": emotion,
            "provider": provider,
            "audio": audio_base64,  # ✅ KEY CHANGE
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            "error": "Synthesis failed",
            "message": str(e)
        }), 500
  


@app.route("/api/emotion", methods=["POST"])
def detect_emotion():
    """
    Detect emotion from text only (no speech synthesis)
    
    Request JSON:
        - text (required): Text to analyze
    
    Response:
        - emotion: Detected emotion (positive, negative, neutral)
        - text: Input text
        - timestamp: Detection timestamp
    """
    try:
        if not request.json:
            return jsonify({
                "error": "Invalid request: JSON body required"
            }), 400

        text = request.json.get("text", "").strip()

        if not text:
            return jsonify({
                "error": "Invalid input",
                "message": "Text field cannot be empty"
            }), 400

        # Detect emotion
        emotion = pipeline.detector.predict(text)

        return jsonify({
            "success": True,
            "emotion": emotion,
            "text": text,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Emotion detection failed",
            "message": str(e)
        }), 500


@app.route("/api/audio/<filename>", methods=["GET"])
def get_audio(filename):
    """
    Retrieve generated audio file
    
    Args:
        filename: Name of the audio file to retrieve
    """
    try:
        # Security: only allow files from the output directory
        output_dir = Path("outputs/audio")
        file_path = output_dir / filename

        # Verify the file exists and is within the output directory
        if not file_path.exists() or not file_path.is_file():
            return jsonify({
                "error": "Audio file not found",
                "filename": filename
            }), 404

        return send_file(
            str(file_path),
            mimetype="audio/mpeg",
            as_attachment=True
        )

    except Exception as e:
        return jsonify({
            "error": "Failed to retrieve audio",
            "message": str(e)
        }), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": [
            "GET /",
            "GET /api/health",
            "GET /api/docs",
            "POST /api/synthesize",
            "POST /api/emotion"
        ]
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "error": "Method not allowed",
        "message": str(error)
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs("outputs/audio", exist_ok=True)

    # Run Flask app
    app.run(
        host="0.0.0.0",    # Listen on all interfaces
        port=5001,          # Custom Flask port
        debug=True,         # Enable debug mode
        threaded=True       # Enable threading for concurrent requests
    )
