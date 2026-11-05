
import os
import wave
import tempfile

from faster_whisper import WhisperModel


# Load model only once
_model = None


def get_model():
    global _model

    if _model is None:
        print("Loading Faster-Whisper model...")

        _model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )

        print("Faster-Whisper loaded successfully.")

    return _model


def transcribe_audio(audio_bytes):
    """
    Convert raw PCM audio into WAV and transcribe it.

    Expected input:
        16 kHz, mono, int16 PCM bytes.

    Returns:
        Transcribed text.
    """

    if not audio_bytes:
        return ""

    audio_path = None

    try:
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_audio:

            audio_path = temp_audio.name

        # Add WAV header to raw PCM audio
        with wave.open(audio_path, "wb") as wav_file:

            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)

            wav_file.writeframes(audio_bytes)

        # Load transcription model
        model = get_model()

        # Transcribe audio
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True
        )

        transcript = " ".join(
            segment.text.strip()
            for segment in segments
        )

        transcript = transcript.strip()

        print("Transcription completed:", transcript)

        return transcript

    except Exception as e:

        print(f"Transcription error: {e}")

        raise RuntimeError(
            f"Speech transcription failed: {e}"
        ) from e

    finally:

        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
