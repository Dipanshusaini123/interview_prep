import os
import time
import threading
import streamlit as st

from io import BytesIO
from mutagen.mp3 import MP3
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

from modules.voice_activity import VoiceActivityDetector
from modules.speech_to_text import transcribe_audio
from modules.text_to_speech import generate_speech


st.set_page_config(page_title="Voice Call Chatbot", page_icon="📞", layout="centered")


# -------------------- AUDIO PIPELINE --------------------

class CallAudioController:
    def __init__(self):
        self.detector = VoiceActivityDetector(
            silence_duration=1.5,
            max_recording_duration=45,
            vad_aggressiveness=2,
        )
        self.listening = threading.Event()
        self.lock = threading.Lock()
        self.completed_audio = None

    def begin_listening(self):
        with self.lock:
            self.completed_audio = None
            self.detector.reset()
            self.listening.set()
        print("CALL: microphone listening started")

    def stop_listening(self):
        self.listening.clear()

    def on_frame(self, frame):
        if not self.listening.is_set():
            return

        with self.lock:
            if not self.listening.is_set():
                return
            audio = self.detector.process_frame(frame)
            if audio:
                self.completed_audio = audio
                self.listening.clear()
                print("CALL: silence detected; recording complete")

    def take_audio(self):
        with self.lock:
            result = self.completed_audio
            self.completed_audio = None
            return result


class CallAudioProcessor(AudioProcessorBase):
    def __init__(self, controller):
        self.controller = controller
        self.logged = False

    async def recv_queued(self, frames):
        if not self.logged:
            print(f"CALL: WebRTC connected ({len(frames)} initial frames)")
            self.logged = True
        for frame in frames:
            self.controller.on_frame(frame)
        return frames


def create_tts(text):
    path = generate_speech(text)
    try:
        with open(path, "rb") as f:
            audio_bytes = f.read()
        duration = MP3(BytesIO(audio_bytes)).info.length
        return audio_bytes, duration
    finally:
        if path and os.path.exists(path):
            os.remove(path)


def simple_reply(text):
    """Temporary local response logic. Groq will replace this in the next stage."""
    cleaned = text.strip()
    if not cleaned:
        return "Sorry, I didn't catch that. Could you say it again?"
    low = cleaned.lower()
    if any(word in low for word in ("bye", "goodbye", "end the call", "hang up")):
        return "It was nice talking with you. Goodbye!"
    return f"I heard you say: {cleaned}. What would you like to talk about next?"


def set_ai_speaking(text):
    controller = st.session_state.call_controller
    controller.stop_listening()
    audio, duration = create_tts(text)
    st.session_state.call_audio = audio
    st.session_state.call_audio_duration = duration
    st.session_state.call_audio_started = time.monotonic()
    st.session_state.call_status = "speaking"
    st.session_state.call_turn_id += 1


# -------------------- SESSION --------------------

if "call_controller" not in st.session_state:
    st.session_state.call_controller = CallAudioController()

defaults = {
    "call_status": "ready",
    "call_audio": None,
    "call_audio_duration": 0.0,
    "call_audio_started": 0.0,
    "call_turn_id": 0,
    "call_pending_audio": None,
    "call_last_transcript": "",
    "call_error": None,
    "call_connected_once": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- CALL UI --------------------

st.title("📞 Voice Call Chatbot")
st.caption("A simple one-to-one voice conversation. No typing or submit button.")

status = st.session_state.call_status
status_labels = {
    "ready": "Ready to call",
    "speaking": "AI is speaking",
    "listening": "Listening to you",
    "processing": "Thinking",
    "ended": "Call ended",
}
status_label = status_labels.get(status, status.title())

orb_color = {
    "ready": "#64748b",
    "speaking": "#2563eb",
    "listening": "#16a34a",
    "processing": "#d97706",
    "ended": "#64748b",
}.get(status, "#64748b")

st.markdown(
    f"""
    <div style="display:flex; flex-direction:column; align-items:center;
                justify-content:center; padding:28px 12px 18px;">
      <div style="width:116px;height:116px;border-radius:50%;
                  background:{orb_color};display:flex;align-items:center;
                  justify-content:center;color:white;font-size:48px;
                  box-shadow:0 0 0 12px {orb_color}22;">
        {"🔊" if status == "speaking" else "🎙️" if status == "listening" else "🤖"}
      </div>
      <div style="font-size:22px;font-weight:650;margin-top:22px;">AI Voice Assistant</div>
      <div style="color:#888;margin-top:7px;">{status_label}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

controller = st.session_state.call_controller

# WebRTC runs continuously; the controller accepts frames only during the
# listening turn, so candidate audio is ignored while the AI is speaking.
webrtc_ctx = webrtc_streamer(
    key="simple_voice_call",
    mode=WebRtcMode.SENDONLY,
    audio_processor_factory=lambda: CallAudioProcessor(controller),
    media_stream_constraints={"video": False, "audio": True},
    desired_playing_state=True,
    async_processing=True,
)

if st.session_state.call_status == "ready":
    st.info("Press Start Call. Allow microphone access when your browser asks.")
    if st.button("Start Call", type="primary", use_container_width=True):
        try:
            set_ai_speaking("Hello! I'm your voice assistant. How are you doing today?")
            st.rerun()
        except Exception as exc:
            st.session_state.call_error = str(exc)
            st.error(f"Could not start the call: {exc}")

elif st.session_state.call_status == "speaking":
    # Playback is rendered in the main app, not in the polling fragment.
    st.audio(
        st.session_state.call_audio,
        format="audio/mp3",
        autoplay=True,
    )

elif st.session_state.call_status == "listening":
    st.caption("Speak naturally. The recording should finish after 1.5 seconds of silence.")

elif st.session_state.call_status == "processing":
    st.caption("Processing your response…")

elif st.session_state.call_status == "ended":
    st.success("The call has ended.")
    if st.button("Start a new call", use_container_width=True):
        controller.stop_listening()
        st.session_state.call_status = "ready"
        st.session_state.call_audio = None
        st.session_state.call_pending_audio = None
        st.session_state.call_last_transcript = ""
        st.rerun()

if st.session_state.call_error:
    st.error(st.session_state.call_error)


# -------------------- TURN MANAGER --------------------
# This fragment only polls state. It does not call st.rerun() from inside
# the fragment; state transitions are reflected on its next refresh.

@st.fragment(run_every="300ms")
def call_turn_manager():
    status_now = st.session_state.call_status
    ctrl = st.session_state.call_controller

    if status_now == "speaking":
        elapsed = time.monotonic() - st.session_state.call_audio_started
        if elapsed >= st.session_state.call_audio_duration + 1.0:
            if st.session_state.call_turn_id == 1 and st.session_state.get("call_first_greeting", True):
                st.session_state.call_first_greeting = False
            ctrl.begin_listening()
            st.session_state.call_status = "listening"

    elif status_now == "listening":
        completed = ctrl.take_audio()
        if completed:
            ctrl.stop_listening()
            st.session_state.call_status = "processing"
            st.session_state.call_pending_audio = completed

    elif status_now == "processing":
        pending = st.session_state.call_pending_audio
        if pending:
            st.session_state.call_pending_audio = None
            try:
                transcript = transcribe_audio(pending)
                st.session_state.call_last_transcript = transcript or ""
                print("CALL: transcript:", transcript)

                if transcript and any(
                    phrase in transcript.lower()
                    for phrase in ("bye", "goodbye", "end the call", "hang up")
                ):
                    reply = "It was nice talking with you. Goodbye!"
                    audio, duration = create_tts(reply)
                    st.session_state.call_audio = audio
                    st.session_state.call_audio_duration = duration
                    st.session_state.call_audio_started = time.monotonic()
                    st.session_state.call_status = "speaking"
                    st.session_state.call_turn_id += 1
                    st.session_state.call_end_after_speech = True
                else:
                    reply = simple_reply(transcript)
                    audio, duration = create_tts(reply)
                    st.session_state.call_audio = audio
                    st.session_state.call_audio_duration = duration
                    st.session_state.call_audio_started = time.monotonic()
                    st.session_state.call_status = "speaking"
                    st.session_state.call_turn_id += 1
                    st.session_state.call_end_after_speech = False

            except Exception as exc:
                ctrl.stop_listening()
                st.session_state.call_error = str(exc)
                st.session_state.call_status = "ended"

    # End the call only after the goodbye audio has had time to play.
    if (
        st.session_state.call_status == "speaking"
        and st.session_state.get("call_end_after_speech", False)
        and time.monotonic() - st.session_state.call_audio_started
            >= st.session_state.call_audio_duration + 1.0
    ):
        ctrl.stop_listening()
        st.session_state.call_status = "ended"


call_turn_manager()
