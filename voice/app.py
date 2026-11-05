

import asyncio
import base64
import os
import tempfile
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import edge_tts
from dotenv import load_dotenv
from groq import Groq


VOICE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = VOICE_DIR.parent

# Load local environment variables.
load_dotenv(PROJECT_DIR / ".env")


def get_api_key():
    """Read Groq API key from Streamlit Secrets or local .env."""

    # First try Streamlit Cloud Secrets.
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
        if api_key:
            return api_key
    except Exception:
        pass

    # Fall back to local .env / environment variables.
    return os.getenv("GROQ_API_KEY")


@st.cache_resource
def get_groq_client():
    """Create and cache the Groq client."""

    api_key = get_api_key()

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not found. Add it to Streamlit Cloud Secrets "
            "or your project's root .env file."
        )

    return Groq(api_key=api_key)


# Register the existing HTML component.
voice_recorder = components.declare_component(
    "edxso_voice_recorder",
    path=str(VOICE_DIR)
)


def generate_speech(text):
    """Convert text to MP3 bytes using Edge TTS."""

    text = str(text or "").strip()

    if not text:
        return b""

    async def create_audio(output_path):
        communicator = edge_tts.Communicate(
            text,
            voice="en-US-AriaNeural"
        )
        await communicator.save(output_path)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as temp_file:
            temp_path = temp_file.name

        asyncio.run(create_audio(temp_path))

        return Path(temp_path).read_bytes()

    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


def transcribe_audio(audio_bytes, mime_type="audio/webm"):
    """Transcribe a browser recording with Groq Whisper."""

    if not audio_bytes:
        return ""

    client = get_groq_client()

    mime_type = (mime_type or "audio/webm").lower()

    if "mp4" in mime_type or "m4a" in mime_type:
        extension = ".mp4"
    elif "ogg" in mime_type:
        extension = ".ogg"
    elif "wav" in mime_type:
        extension = ".wav"
    else:
        extension = ".webm"

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False
        ) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name

        with open(temp_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(Path(temp_path).name, audio_file.read()),
                model="whisper-large-v3-turbo",
                response_format="text"
            )

        if isinstance(transcription, str):
            return transcription.strip()

        return str(
            getattr(transcription, "text", "")
        ).strip()

    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


def encode_audio(audio_bytes):
    """Encode MP3 bytes for the HTML component."""

    if not audio_bytes:
        return ""

    return base64.b64encode(audio_bytes).decode("utf-8")
