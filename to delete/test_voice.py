
import os
import time
import threading
import streamlit as st

from io import BytesIO
from mutagen.mp3 import MP3

from streamlit_webrtc import (
    webrtc_streamer,
    AudioProcessorBase,
    WebRtcMode,
)

from modules.voice_activity import VoiceActivityDetector
from modules.speech_to_text import transcribe_audio
from modules.text_to_speech import generate_speech

from modules.question_generator import (
    generate_greeting,
    generate_next_interaction,
    generate_closing,
)

from modules.voice_ui import render_voice_ui


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Voice Interview",
    page_icon="🎙️",
    layout="centered",
)


# --------------------------------------------------
# AUDIO CONTROLLER
# --------------------------------------------------

class AudioController:
    """
    Per-session controller shared between Streamlit
    and the WebRTC audio processing thread.
    """

    def __init__(self):

        self.detector = VoiceActivityDetector()

        self.listening_gate = threading.Event()

        self.lock = threading.Lock()

        self.completed_audio = None

    def start_listening(self):

        with self.lock:

            self.completed_audio = None
            self.detector.reset()

            self.listening_gate.set()

    def stop_listening(self):

        self.listening_gate.clear()

    def process_frame(self, frame):

        if not self.listening_gate.is_set():
            return

        with self.lock:

            if not self.listening_gate.is_set():
                return

            result = self.detector.process_frame(frame)

            if result:

                self.completed_audio = result

                self.listening_gate.clear()

    def get_completed_audio(self):

        with self.lock:

            audio = self.completed_audio

            self.completed_audio = None

            return audio


# --------------------------------------------------
# WEBRTC AUDIO PROCESSOR
# --------------------------------------------------


class InterviewAudioProcessor(AudioProcessorBase):

    def __init__(self, controller):
        self.controller = controller
        self._logged_first_batch = False

    async def recv_queued(self, frames):
        if not self._logged_first_batch:
            print(
                f"WebRTC audio connected: received first batch "
                f"({len(frames)} frame(s))."
            )
            self._logged_first_batch = True

        for frame in frames:
            self.controller.process_frame(frame)

        return frames



# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

def initialize_session():

    defaults = {

        "call_started": False,
        "call_status": "waiting",

        "call_history": [],

        "call_question_count": 0,

        "call_current_question": "",

        "call_audio": None,

        "call_audio_duration": 0,

        "call_audio_started": 0,

        "call_closing": False,

        "call_error": None,

        "call_candidate_name": "Candidate",

        "call_job_role": "Software Engineer",

        "call_resume_text": "",

        "call_jd_text": "",

        "call_resume_analysis": {},
        "call_pending_audio": None,

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


initialize_session()

# Create the audio controller only once per Streamlit session.
if "call_controller" not in st.session_state:
    st.session_state.call_controller = AudioController()


# --------------------------------------------------
# TEXT TO SPEECH
# --------------------------------------------------

def create_ai_audio(text):

    if not text or not text.strip():

        raise ValueError("Cannot generate speech from empty text.")

    audio_path = None

    try:

        audio_path = generate_speech(text)

        if not audio_path or not os.path.exists(audio_path):

            raise RuntimeError("TTS did not generate an audio file.")

        with open(audio_path, "rb") as audio_file:

            audio_bytes = audio_file.read()

        duration = MP3(
            BytesIO(audio_bytes)
        ).info.length

        return audio_bytes, duration

    finally:

        if audio_path and os.path.exists(audio_path):

            os.remove(audio_path)


# --------------------------------------------------
# AI SPEAKING
# --------------------------------------------------

def make_ai_speak(text):

    controller = st.session_state.call_controller

    # Never listen while AI is speaking.
    controller.stop_listening()

    audio_bytes, duration = create_ai_audio(text)

    st.session_state.call_audio = audio_bytes

    st.session_state.call_audio_duration = duration

    # Timer starts after audio generation.
    st.session_state.call_audio_started = time.monotonic()

    st.session_state.call_status = "speaking"


# --------------------------------------------------
# INTERVIEW START
# --------------------------------------------------

def start_interview():

    candidate_name = st.session_state.call_candidate_name

    job_role = st.session_state.call_job_role

    greeting = generate_greeting(
        candidate_name,
        job_role
    )

    if not greeting:

        raise RuntimeError("AI greeting generation returned empty text.")

    st.session_state.call_history = []

    st.session_state.call_question_count = 0

    st.session_state.call_current_question = greeting

    st.session_state.call_closing = False

    st.session_state.call_started = True

    make_ai_speak(greeting)


# --------------------------------------------------
# NEXT AI INTERACTION
# --------------------------------------------------

def ask_next_question():

    result = generate_next_interaction(

        resume_text=st.session_state.call_resume_text,

        jd_text=st.session_state.call_jd_text,

        analysis=st.session_state.call_resume_analysis,

        history=st.session_state.call_history,

        question_count=st.session_state.call_question_count,

        emergency_limit=25,

        difficulty="Intermediate",

        question_type="Mixed Questions",
    )

    if not isinstance(result, dict):

        raise RuntimeError("Invalid response from question generator.")

    action = result.get("action")

    # AI decides to finish.
    if action == "finish":

        closing = generate_closing(

            st.session_state.call_candidate_name,

            st.session_state.call_job_role,

            st.session_state.call_history,
        )

        st.session_state.call_closing = True

        make_ai_speak(closing)

        return

    if action not in ("follow_up", "new_topic"):

        raise RuntimeError(f"Unknown AI action: {action}")

    question = result.get("question", "").strip()

    if not question:

        raise RuntimeError("AI generated an empty question.")

    st.session_state.call_current_question = question

    st.session_state.call_question_count += 1

    make_ai_speak(question)


# --------------------------------------------------
# PROCESS CANDIDATE ANSWER
# --------------------------------------------------

def process_candidate_answer(audio_bytes):

    st.session_state.call_status = "processing"

    transcript = transcribe_audio(audio_bytes)

    print("\nCandidate answer:", transcript)

    if not transcript:

        make_ai_speak(
            "I could not hear your answer clearly. "
            "Could you please repeat that?"
        )

        return

    # Save the answer against the question asked.
    st.session_state.call_history.append({

        "stage": "Interview",

        "action": "question_answer",

        "question": st.session_state.call_current_question,

        "answer": transcript,

    })

    print("Interview history updated.")

    # Generate the next question.
    ask_next_question()


# --------------------------------------------------
# INTERVIEW HEADER
# --------------------------------------------------

st.title("🎙️ AI Mock Interview")

st.caption(
    "A voice-based interview with your AI interviewer."
)


# --------------------------------------------------
# TEST CONFIGURATION
# --------------------------------------------------

if not st.session_state.call_started:

    st.info(
        "Enter your interview details before starting."
    )

    with st.expander("Interview configuration", expanded=True):

        st.text_input(
            "Candidate name",
            key="call_candidate_name"
        )

        st.text_input(
            "Job role",
            key="call_job_role"
        )

        st.text_area(
            "Resume text",
            key="call_resume_text",
            height=130,
            placeholder="Paste your resume text here..."
        )

        st.text_area(
            "Job description",
            key="call_jd_text",
            height=130,
            placeholder="Paste the job description here..."
        )

        # Optional existing resume analysis.
        st.caption(
            "Resume analysis is optional for this initial test."
        )

    if st.button(
        "Start Interview",
        type="primary",
        use_container_width=True
    ):

        if not st.session_state.call_resume_text.strip():

            st.error("Please enter your resume text.")

        elif not st.session_state.call_jd_text.strip():

            st.error("Please enter the job description.")

        else:

            try:

                with st.spinner("Preparing your interview..."):

                    start_interview()

                st.rerun()

            except Exception as e:

                st.session_state.call_error = str(e)

                st.error(f"Could not start interview: {e}")

    st.stop()


# --------------------------------------------------
# WEBRTC MICROPHONE
# --------------------------------------------------

controller = st.session_state.call_controller

webrtc_ctx = webrtc_streamer(

    key="ai_voice_interview",

    mode=WebRtcMode.SENDONLY,

    audio_processor_factory=lambda: InterviewAudioProcessor(
        controller
    ),

    media_stream_constraints={
        "video": False,
        "audio": True,
    },

    desired_playing_state=True,

    async_processing=True,

)


# --------------------------------------------------
# AI AUDIO PLAYER
# --------------------------------------------------

if st.session_state.call_status == "speaking":

    st.audio(

        st.session_state.call_audio,

        format="audio/mp3",

        autoplay=True,

    )


# --------------------------------------------------
# AUTOMATIC INTERVIEW LOOP
# --------------------------------------------------

@st.fragment(run_every="300ms")
def interview_loop():

    status = st.session_state.call_status

    render_voice_ui(status)

    controller = st.session_state.call_controller

    # ----------------------------------------------
    # AI SPEAKING
    # ----------------------------------------------

    if status == "speaking":

        elapsed = (
            time.monotonic()
            - st.session_state.call_audio_started
        )

        duration = st.session_state.call_audio_duration

        # Small additional buffer for browser playback.
        if elapsed >= duration + 1.2:

            if st.session_state.call_closing:

                controller.stop_listening()

                st.session_state.call_status = "ended"

            else:

                controller.start_listening()

                st.session_state.call_status = "listening"

            # The fragment refreshes again automatically after 300 ms.

    # ----------------------------------------------
    # CANDIDATE LISTENING
    # ----------------------------------------------

    elif status == "listening":

        if not webrtc_ctx.state.playing:

            st.warning(
                "Microphone is not connected. "
                "Please allow microphone access."
            )

        audio = controller.get_completed_audio()

        if audio:

            controller.stop_listening()

            st.session_state.call_status = "processing"

            st.session_state.call_pending_audio = audio

            # The next fragment tick will process the pending audio.

    # ----------------------------------------------
    # PROCESSING
    # ----------------------------------------------

    elif status == "processing":

        pending_audio = st.session_state.get(
            "call_pending_audio"
        )

        if pending_audio:

            st.session_state.call_pending_audio = None

            try:

                process_candidate_answer(pending_audio)
                # The next fragment tick will render the updated status.

            except Exception as e:

                controller.stop_listening()

                st.session_state.call_error = str(e)

                st.session_state.call_status = "ended"

                st.error(f"Interview error: {e}")

    # ----------------------------------------------
    # ENDED
    # ----------------------------------------------

    elif status == "ended":

        controller.stop_listening()

        st.success("Your interview has been completed.")

        st.write(
            f"Questions generated: "
            f"{st.session_state.call_question_count}"
        )

        st.write(
            f"Responses recorded: "
            f"{len(st.session_state.call_history)}"
        )


interview_loop()
