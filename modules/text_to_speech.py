
import edge_tts
import asyncio
import tempfile
import os


async def generate_speech_async(text, output_path):
    """Generate speech from text using Edge TTS."""

    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-AriaNeural",
        rate="+0%",
        pitch="+0Hz"
    )

    await communicate.save(output_path)


def generate_speech(text):
    """
    Convert text into speech and return the audio file path.
    """

    if not text or not text.strip():
        return None

    audio_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as temp_audio:

            audio_path = temp_audio.name

        asyncio.run(
            generate_speech_async(text, audio_path)
        )

        return audio_path

    except Exception as e:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

        raise RuntimeError(f"Speech generation failed: {e}")


if __name__ == "__main__":

    sample_text = (
        "Hello Dipanshu. Welcome to your AI mock interview. "
        "Could you please introduce yourself?"
    )

    try:
        audio_file = generate_speech(sample_text)
        print("Speech generated successfully:", audio_file)

    except Exception as e:
        print(e)
