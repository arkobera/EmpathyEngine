#!/usr/bin/env python3
"""
Empathy Engine Flask API Client

A simple client script to interact with the Flask API.
Run this script to test the API endpoints.

Usage:
    python client.py
    uv run client.py
"""

import requests
import json
import sys
from pathlib import Path
from typing import Optional
import argparse


class EmpathyEngineClient:
    """Client for interacting with Empathy Engine Flask API"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def health_check(self) -> bool:
        """Check if the API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print("✅ API is healthy!")
                return True
            print("❌ API health check failed")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to API at {self.base_url}")
            print("   Make sure the Flask app is running:")
            print("   uv run flask run --app flask_app/app.py")
            return False

    def synthesize(self, text: str, return_audio: bool = False) -> Optional[dict]:
        """
        Synthesize speech from text with emotion detection
        
        Args:
            text: Text to synthesize
            return_audio: Whether to return audio file URL
            
        Returns:
            Response dictionary or None if failed
        """
        if not text.strip():
            print("❌ Text cannot be empty")
            return None

        try:
            print(f"\n🎤 Synthesizing: '{text}'")
            print("⏳ Processing...")

            response = self.session.post(
                f"{self.base_url}/api/synthesize",
                json={"text": text, "return_audio": return_audio},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print("\n✅ Synthesis successful!")
                print(f"   Emotion: {result['emotion']}")
                print(f"   Provider: {result['provider']}")
                print(f"   Audio: {result['audio_path']}")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.json())
                return None

        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    def detect_emotion(self, text: str) -> Optional[str]:
        """
        Detect emotion from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected emotion or None if failed
        """
        if not text.strip():
            print("❌ Text cannot be empty")
            return None

        try:
            print(f"\n🧠 Analyzing: '{text}'")
            print("⏳ Processing...")

            response = self.session.post(
                f"{self.base_url}/api/emotion",
                json={"text": text},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Emotion detected: {result['emotion']}")
                return result['emotion']
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.json())
                return None

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    def download_audio(self, filename: str, save_path: str = "./downloaded_audio.mp3") -> bool:
        """
        Download an audio file
        
        Args:
            filename: Audio filename to download
            save_path: Where to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"\n📥 Downloading: {filename}")
            response = self.session.get(
                f"{self.base_url}/api/audio/{filename}",
                timeout=30
            )

            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                print(f"✅ Downloaded to: {save_path}")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

    def get_docs(self) -> Optional[dict]:
        """Get API documentation"""
        try:
            response = self.session.get(f"{self.base_url}/api/docs")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None


def interactive_mode(client: EmpathyEngineClient):
    """Interactive mode for testing the API"""
    print("\n" + "=" * 70)
    print("🎙️  Empathy Engine Flask API - Interactive Client")
    print("=" * 70)

    while True:
        print("\nOptions:")
        print("  1. Synthesize speech (text → emotion + audio)")
        print("  2. Detect emotion only (text → emotion)")
        print("  3. Get API documentation")
        print("  4. Show example usage")
        print("  5. Exit")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            text = input("Enter text to synthesize: ").strip()
            if text:
                client.synthesize(text)

        elif choice == "2":
            text = input("Enter text to analyze: ").strip()
            if text:
                client.detect_emotion(text)

        elif choice == "3":
            docs = client.get_docs()
            if docs:
                print("\n📚 API Documentation:")
                print(json.dumps(docs, indent=2))

        elif choice == "4":
            show_examples()

        elif choice == "5":
            print("\n👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice")


def show_examples():
    """Show example usage"""
    print("\n" + "=" * 70)
    print("📖 Example Usage")
    print("=" * 70)

    examples = {
        "Positive emotion": "I am absolutely thrilled about this amazing opportunity!",
        "Negative emotion": "This is terrible and I hate it",
        "Neutral emotion": "The weather is cloudy today",
        "With exclamation": "I can't believe how incredible this is!!!",
        "With capitals": "THIS IS AWESOME",
    }

    for label, text in examples.items():
        print(f"\n{label}:")
        print(f'  Text: "{text}"')
        print(f'  Command: curl -X POST http://localhost:5000/api/emotion \\')
        print(f'    -H "Content-Type: application/json" \\')
        print(f'    -d \'{{\"text": "{text}"}}\'')


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Empathy Engine Flask API Client"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:5000",
        help="API base URL (default: http://localhost:5000)"
    )
    parser.add_argument(
        "--synthesize",
        help="Synthesize text (non-interactive mode)"
    )
    parser.add_argument(
        "--emotion",
        help="Detect emotion from text (non-interactive mode)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check API health"
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Show example usage"
    )

    args = parser.parse_args()

    # Create client
    client = EmpathyEngineClient(args.url)

    # Check health first
    print(f"Connecting to {args.url}...")
    if not client.health_check():
        sys.exit(1)

    # Handle different modes
    if args.check:
        return

    elif args.synthesize:
        client.synthesize(args.synthesize)

    elif args.emotion:
        client.detect_emotion(args.emotion)

    elif args.examples:
        show_examples()

    else:
        # Interactive mode
        interactive_mode(client)


if __name__ == "__main__":
    main()
