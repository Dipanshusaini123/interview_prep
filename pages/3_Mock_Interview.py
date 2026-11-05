
import streamlit as st
import os

from modules.question_generator import (
    generate_greeting,
    generate_next_interaction,
    generate_closing
)

from modules.speech_to_text import transcribe_audio
from modules.text_to_speech import generate_speech


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.title("🎤 AI Mock Interview")

st.write(
    "Practice your interview by speaking with an AI interviewer. "
    "Listen to questions and answer using your microphone or keyboard."
)


# --------------------------------------------------
# 2. SESSION STATE
# --------------------------------------------------

DEFAULTS = {
    "mock_history": [],
    "mock_question_count": 0,
    "mock_status": "not_started",
    "mock_current_question": "",
    "mock_current_stage": "",
    "mock_current_action": "",
    "mock_is_greeting": False,
    "mock_closing": "",
    "mock_candidate_name": "",
    "mock_job_role": "",
    "mock_difficulty": "Intermediate",
    "mock_question_type": "Mixed Questions",
    "mock_error": "",
    "mock_audio_bytes": None,
    "mock_audio_text": "",
    "mock_transcribed_answer": ""
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# 3. CHECK RESUME AND JOB DESCRIPTION
# --------------------------------------------------

resume_text = st.session_state.get("resume_text", "")
jd_text = st.session_state.get("jd_text", "")
analysis = st.session_state.get("resume_analysis", {})

if not resume_text or not jd_text or not analysis:
    st.warning(
        "Please complete Resume & JD Analysis before starting "
        "the mock interview."
    )

    st.page_link(
        "pages/1_Resume_Analysis.py",
        label="Go to Resume Analysis",
        icon="📄"
    )

    st.stop()


# --------------------------------------------------
# 4. HELPER FUNCTIONS
# --------------------------------------------------

def reset_interview():

    keys_to_reset = {
        "mock_history": [],
        "mock_question_count": 0,
        "mock_status": "not_started",
        "mock_current_question": "",
        "mock_current_stage": "",
        "mock_current_action": "",
        "mock_is_greeting": False,
        "mock_closing": "",
        "mock_error": "",
        "mock_audio_bytes": None,
        "mock_audio_text": "",
        "mock_transcribed_answer": ""
    }

    for key, value in keys_to_reset.items():
        st.session_state[key] = value

    # Reset the answer widget as well
    if "mock_answer_input" in st.session_state:
        del st.session_state["mock_answer_input"]


def get_speech_audio(text):

    """Generate speech and return MP3 bytes."""

    audio_path = None

    try:
        audio_path = generate_speech(text)

        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        return audio_bytes

    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)


def prepare_question_audio():

    """Generate audio only when the question changes."""

    question = st.session_state.mock_current_question

    if not question:
        return

    if st.session_state.mock_audio_text == question:
        return

    try:
        with st.spinner("Generating interviewer voice..."):

            audio_bytes = get_speech_audio(question)

            st.session_state.mock_audio_bytes = audio_bytes
            st.session_state.mock_audio_text = question

    except Exception as e:

        st.session_state.mock_audio_bytes = None
        st.warning(f"Voice generation unavailable: {e}")


def get_next_question():

    """Ask the AI to generate the next interview interaction."""

    try:

        result = generate_next_interaction(
            resume_text=resume_text,
            jd_text=jd_text,
            analysis=analysis,
            history=st.session_state.mock_history,
            question_count=st.session_state.mock_question_count,
            emergency_limit=25,
            difficulty=st.session_state.mock_difficulty,
            question_type=st.session_state.mock_question_type
        )

        action = result.get("action", "")
        stage = result.get("stage", "")
        question = result.get("question", "")

        if action == "finish":

            st.session_state.mock_closing = generate_closing(
                candidate_name=st.session_state.mock_candidate_name,
                job_role=st.session_state.mock_job_role,
                history=st.session_state.mock_history
            )

            st.session_state.mock_status = "completed"
            st.session_state.mock_current_question = ""

            return

        if not question:
            raise ValueError("AI generated an empty question.")

        st.session_state.mock_current_action = action
        st.session_state.mock_current_stage = stage
        st.session_state.mock_current_question = question
        st.session_state.mock_is_greeting = False

        # Force audio generation for the new question
        st.session_state.mock_audio_text = ""
        st.session_state.mock_audio_bytes = None

    except Exception as e:

        st.session_state.mock_error = str(e)


# --------------------------------------------------
# 5. INTERVIEW SETUP
# --------------------------------------------------

if st.session_state.mock_status == "not_started":

    st.subheader("Interview Setup")

    candidate_name = (
        analysis.get("candidate_name") or "Candidate"
    )

    st.text_input(
        "Candidate Name",
        value=candidate_name,
        disabled=True
    )

    default_role = st.session_state.get(
        "interview_job_role",
        st.session_state.get("job_role", "AI Engineer Intern")
    )

    job_role = st.text_input(
        "Job Role",
        value=default_role,
        key="mock_job_role_input"
    )

    difficulty = st.selectbox(
        "Interview Difficulty",
        ["Beginner", "Intermediate", "Advanced"],
        index=1
    )

    question_type = st.selectbox(
        "Question Type",
        [
            "Mixed Questions",
            "Technical Questions",
            "HR Questions",
            "Project-Based Questions",
            "Resume-Based Questions"
        ]
    )

    st.info(
        "The AI interviewer dynamically decides whether to ask "
        "follow-up questions, explore new topics, or finish."
    )

    if st.button(
        "🚀 Start Voice Interview",
        type="primary",
        use_container_width=True
    ):

        if not job_role.strip():

            st.error("Please enter a job role.")

        else:

            try:

                with st.spinner("Preparing your interview..."):

                    greeting = generate_greeting(
                        candidate_name=candidate_name,
                        job_role=job_role.strip()
                    )

                    st.session_state.mock_candidate_name = candidate_name
                    st.session_state.mock_job_role = job_role.strip()
                    st.session_state.mock_difficulty = difficulty
                    st.session_state.mock_question_type = question_type

                    st.session_state.mock_history = [
                        {
                            "stage": "greeting",
                            "action": "greeting",
                            "question": greeting,
                            "answer": ""
                        }
                    ]

                    st.session_state.mock_question_count = 0
                    st.session_state.mock_current_question = greeting
                    st.session_state.mock_current_stage = "greeting"
                    st.session_state.mock_current_action = "greeting"
                    st.session_state.mock_is_greeting = True
                    st.session_state.mock_status = "active"
                    st.session_state.mock_error = ""

                    st.session_state.mock_audio_text = ""
                    st.session_state.mock_audio_bytes = None
                    st.session_state.mock_transcribed_answer = ""

                st.rerun()

            except Exception as e:

                st.error(f"Could not start interview: {e}")


# --------------------------------------------------
# 6. ACTIVE INTERVIEW
# --------------------------------------------------

elif st.session_state.mock_status == "active":

    st.subheader("🎙️ Interview in Progress")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Questions Answered",
            st.session_state.mock_question_count
        )

    with col2:
        st.metric("Emergency Limit", 25)

    st.divider()

    # Current interview stage
    stage = st.session_state.mock_current_stage

    if stage:
        st.caption(
            f"Stage: {stage.replace('_', ' ').title()}"
        )

    # ----------------------------------------------
    # AI INTERVIEWER
    # ----------------------------------------------

    st.markdown("### 🤖 AI Interviewer")

    st.info(st.session_state.mock_current_question)

    # Generate and play interviewer voice
    prepare_question_audio()

    if st.session_state.mock_audio_bytes:

        st.audio(
            st.session_state.mock_audio_bytes,
            format="audio/mp3",
            autoplay=True
        )

    # ----------------------------------------------
    # ERROR HANDLING
    # ----------------------------------------------

    if st.session_state.mock_error:

        st.error(st.session_state.mock_error)

        if st.button("Retry Generating Question"):

            st.session_state.mock_error = ""

            with st.spinner("Generating question..."):
                get_next_question()

            st.rerun()

    else:

        st.divider()

        # ------------------------------------------
        # CANDIDATE VOICE INPUT
        # ------------------------------------------

        st.markdown("### 🎤 Your Answer")

        st.write("Record your answer using your microphone.")

        recorded_audio = st.audio_input(
            "Record your response",
            key="mock_audio_input"
        )

        if st.button(
            "Transcribe Recording",
            disabled=recorded_audio is None
        ):

            try:

                with st.spinner("Transcribing your answer..."):

                    transcript = transcribe_audio(
                        recorded_audio.getvalue()
                    )

                    if transcript:

                        st.session_state.mock_transcribed_answer = transcript
                        st.session_state["mock_answer_input"] = transcript

                    else:

                        st.warning(
                            "No speech detected. Please record again."
                        )

            except Exception as e:

                st.error(f"Transcription failed: {e}")

        # ------------------------------------------
        # ANSWER EDITOR
        # ------------------------------------------

        st.markdown("#### Review your answer")

        answer = st.text_area(
            "Your transcribed answer (you can edit it)",
            value=st.session_state.mock_transcribed_answer,
            height=150,
            key="mock_answer_input",
            placeholder="Your answer will appear here after transcription. You can also type manually."
        )

        # ------------------------------------------
        # SUBMIT ANSWER
        # ------------------------------------------

        if st.button(
            "Submit Answer",
            type="primary",
            use_container_width=True
        ):

            if not answer.strip():

                st.warning(
                    "Please record or type an answer before submitting."
                )

            else:

                # Save answer in conversation history
                current_entry = st.session_state.mock_history[-1]

                current_entry["answer"] = answer.strip()

                # Do not count greeting as a question
                if not st.session_state.mock_is_greeting:

                    st.session_state.mock_question_count += 1

                st.session_state.mock_transcribed_answer = ""

                with st.spinner(
                    "AI interviewer is preparing the next question..."
                ):

                    get_next_question()

                st.rerun()

    st.divider()

    # ----------------------------------------------
    # END INTERVIEW
    # ----------------------------------------------

    if st.button(
        "End Interview",
        type="secondary",
        use_container_width=True
    ):

        try:

            with st.spinner("Preparing interview conclusion..."):

                st.session_state.mock_closing = generate_closing(
                    candidate_name=st.session_state.mock_candidate_name,
                    job_role=st.session_state.mock_job_role,
                    history=st.session_state.mock_history
                )

                st.session_state.mock_status = "completed"
                st.session_state.mock_current_question = ""
                st.session_state.mock_error = ""

        except Exception as e:

            st.error(f"Could not generate closing: {e}")

        st.rerun()


# --------------------------------------------------
# 7. COMPLETED INTERVIEW
# --------------------------------------------------

elif st.session_state.mock_status == "completed":

    st.success("🎉 Interview Completed!")

    st.subheader("AI Interviewer Closing")

    if st.session_state.mock_closing:

        st.info(st.session_state.mock_closing)

        # Speak closing message
        if st.button("🔊 Play Closing Message"):

            try:

                with st.spinner("Generating closing audio..."):

                    closing_audio = get_speech_audio(
                        st.session_state.mock_closing
                    )

                st.audio(
                    closing_audio,
                    format="audio/mp3"
                )

            except Exception as e:

                st.error(f"Closing audio failed: {e}")

    st.metric(
        "Total Questions Answered",
        st.session_state.mock_question_count
    )

    st.divider()

    st.subheader("Interview Transcript")

    for index, item in enumerate(
        st.session_state.mock_history,
        start=1
    ):

        question = item.get("question", "")
        candidate_answer = item.get("answer", "")

        if item.get("action") == "greeting":

            st.markdown("**🤖 AI Interviewer – Greeting**")
            st.write(question)

        else:

            st.markdown(f"**Question {index - 1}:**")
            st.write(question)

            if candidate_answer:

                st.markdown("**Your Answer:**")
                st.write(candidate_answer)

            else:

                st.caption("No answer submitted.")

        st.divider()

    if st.button(
        "🔄 Start New Interview",
        type="primary",
        use_container_width=True
    ):

        reset_interview()
        st.rerun()
