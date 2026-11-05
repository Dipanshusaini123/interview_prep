
import asyncio
import os
import tempfile
import base64
import uuid
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
import edge_tts

from dotenv import load_dotenv
from groq import Groq


# --------------------------------------------------
# PATHS AND CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
VOICE_DIR = Path(__file__).resolve().parent

# Load .env from the main project folder
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GROQ_API_KEY")


st.set_page_config(
    page_title="AI Voice Interviewer",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ AI Voice Interviewer")
st.caption("Standalone AI voice interview prototype")


if not API_KEY:
    st.error("GROQ_API_KEY not found in the main project .env file.")
    st.stop()


client = Groq(api_key=API_KEY)


# --------------------------------------------------
# REGISTER VOICE COMPONENT
# --------------------------------------------------

voice_recorder = components.declare_component(
    "voice_recorder",
    path=str(VOICE_DIR)
)


# --------------------------------------------------
# SYSTEM PROMPT
# --------------------------------------------------

SYSTEM_PROMPT = """
You are a friendly, professional interviewer.

Conduct a one-to-one interview.
Ask one question at a time.
Keep questions concise and natural.

After receiving an answer:
- Briefly acknowledge the candidate's answer.
- Ask the next relevant question.
- Maintain conversation context.

Do not provide long explanations.
"""


# --------------------------------------------------
# TEXT TO SPEECH
# --------------------------------------------------

def generate_speech(text):

    async def create_audio(path):

        communicate = edge_tts.Communicate(
            text,
            voice="en-US-AriaNeural"
        )

        await communicate.save(path)


    with tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    ) as tmp:

        path = tmp.name


    try:

        asyncio.run(create_audio(path))

        return Path(path).read_bytes()

    finally:

        Path(path).unlink(missing_ok=True)


# --------------------------------------------------
# LLM RESPONSE
# --------------------------------------------------

def ask_llm(messages):

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=messages,

        temperature=0.7,

        max_tokens=250

    )

    return response.choices[0].message.content.strip()


# --------------------------------------------------
# SPEECH TO TEXT
# --------------------------------------------------

def transcribe_audio(audio_bytes, mime_type):

    extension = (
        ".mp4" if "mp4" in mime_type else ".webm"
    )

    result = client.audio.transcriptions.create(

        file=(
            f"candidate_answer{extension}",
            audio_bytes,
            mime_type
        ),

        model="whisper-large-v3-turbo",

        response_format="text"

    )

    return (
        result
        if isinstance(result, str)
        else result.text
    )


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {

    "messages": [],

    "current_question": "",

    "question_audio": None,

    "started": False,

    "interview_id": None,

    "question_number": 1,

    "question_id": None,

    "last_recording_id": None

}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.subheader("Interview Settings")

    interview_topic = st.text_input(
        "Interview Topic",
        value="General Software Engineering"
    )

    if st.button("Reset Interview"):

        for key in defaults:
            st.session_state.pop(key, None)

        st.rerun()


# --------------------------------------------------
# START INTERVIEW
# --------------------------------------------------

def start_interview():

    interview_id = uuid.uuid4().hex

    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },

        {
            "role": "user",
            "content": (
                f"Start an interview about {interview_topic}. "
                "Introduce yourself briefly and ask the first question."
            )
        }

    ]

    question = ask_llm(messages)

    messages.append({
        "role": "assistant",
        "content": question
    })

    st.session_state.messages = messages

    st.session_state.current_question = question

    st.session_state.question_audio = generate_speech(question)

    st.session_state.started = True

    st.session_state.interview_id = interview_id

    st.session_state.question_number = 1

    st.session_state.question_id = f"{interview_id}-1"

    st.session_state.last_recording_id = None


# --------------------------------------------------
# INITIAL SCREEN
# --------------------------------------------------

if not st.session_state.started:

    st.write("Start your AI-powered voice interview.")

    if st.button(
        "▶️ Start Interview",
        type="primary",
        use_container_width=True
    ):

        with st.spinner("Preparing interviewer..."):

            try:

                start_interview()

                st.rerun()

            except Exception as e:

                st.error(f"Error: {e}")


# --------------------------------------------------
# INTERVIEW SCREEN
# --------------------------------------------------

else:

    st.subheader("🤖 AI Interviewer")

    st.info(st.session_state.current_question)

    audio_base64 = base64.b64encode(
        st.session_state.question_audio
    ).decode("utf-8")

    st.subheader("🎤 Your Answer")

    st.write(
        "Enable your microphone once. "
        "Recording will start automatically after the AI finishes speaking."
    )


    # --------------------------------------------------
    # VOICE COMPONENT
    # --------------------------------------------------

    voice_result = voice_recorder(

        question=st.session_state.current_question,

        audio_b64=audio_base64,

        question_id=st.session_state.question_id,

        silence_seconds=2,

        active=True,

        key="voice_recorder"

    )


    # --------------------------------------------------
    # PROCESS AUTOMATIC RECORDING
    # --------------------------------------------------

    if isinstance(voice_result, dict):

        recording_type = voice_result.get("type")

        recording_id = voice_result.get("recording_id")

        recording_question_id = voice_result.get("question_id")


        if (

            recording_type == "VOICE_RECORDING"

            and recording_id

            and recording_id != st.session_state.last_recording_id

            and recording_question_id == st.session_state.question_id

        ):

            # Avoid processing the same recording twice
            st.session_state.last_recording_id = recording_id

            try:

                with st.spinner("Transcribing your answer..."):

                    encoded_audio = voice_result.get(
                        "audio_base64",
                        ""
                    )

                    audio_bytes = base64.b64decode(
                        encoded_audio
                    )

                    mime_type = voice_result.get(
                        "mime_type",
                        "audio/webm"
                    )

                    transcript = transcribe_audio(
                        audio_bytes,
                        mime_type
                    )


                if not transcript.strip():

                    st.warning("No speech detected. Please try again.")
                    st.stop()


                st.success("Transcription Complete")

                st.write(transcript)


                # Send candidate answer to LLM
                st.session_state.messages.append({

                    "role": "user",

                    "content": transcript

                })


                with st.spinner("AI is thinking..."):

                    next_question = ask_llm(
                        st.session_state.messages
                    )

                    st.session_state.messages.append({

                        "role": "assistant",

                        "content": next_question

                    })

                    st.session_state.current_question = next_question

                    st.session_state.question_audio = generate_speech(
                        next_question
                    )


                    # Create new question ID
                    st.session_state.question_number += 1

                    st.session_state.question_id = (

                        f"{st.session_state.interview_id}-"
                        f"{st.session_state.question_number}"

                    )


                st.rerun()


            except Exception as e:

                st.error(f"Error processing answer: {e}")


    # --------------------------------------------------
    # CONVERSATION HISTORY
    # --------------------------------------------------

    with st.expander("Conversation Transcript"):

        for message in st.session_state.messages:

            if message["role"] == "system":
                continue

            speaker = (
                "AI Interviewer"
                if message["role"] == "assistant"
                else "Candidate"
            )

            st.markdown(
                f"**{speaker}:** {message['content']}"
            )
