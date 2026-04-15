import yaml
import os
from dotenv import load_dotenv


def load_config(config_path: str) -> dict:
    """
    Load YAML configuration file and inject environment variables.

    Args:
        config_path (str): Path to YAML config file

    Returns:
        dict: Parsed configuration dictionary
    """

    # Load environment variables from .env
    load_dotenv()

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # # Optional: Inject env variables into config (if needed)
    # config["env"] = {
    #     "ELEVEN_LABS": os.getenv("ELEVEN_LABS")
    # }

    # Basic validation (important for robustness)
    validate_config(config)

    return config


def validate_config(config: dict):
    """
    Basic validation to ensure required keys exist
    """

    required_keys = ["app", "emotion", "tts", "voice_mapping"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config section: {key}")

    # Check output directory
    if "output_dir" not in config["app"]:
        raise ValueError("Missing 'output_dir' in app config")

    provider = config["tts"].get("provider")
    supported_providers = ["google", "elevenlabs", "gtts"]
    if provider not in supported_providers:
        raise ValueError(
            f"Unsupported TTS provider: {provider}. Supported: {supported_providers}"
            )

    # Check voice mapping
    if "neutral" not in config["voice_mapping"]:
        raise ValueError("voice_mapping must contain 'neutral' config")