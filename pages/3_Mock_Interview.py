import uuid

import streamlit as st

from modules.question_generator import (
    create_empty_memory,
    generate_greeting,
    generate_next_interaction,
    generate_closing
)

from voice.app import (
    encode_audio,
    generate_speech,
    transcribe_audio,
    voice_recorder
)


# =====================================================
# 1. PAGE
# =====================================================

st.title("🎙️ AI Mock Interview")
st.caption(
    "Have a one-to-one voice interview based on your resume and the job description."
)


# =====================================================
# 2. SESSION STATE
# =====================================================

DEFAULTS = {
    "mock_history": [],
    "mock_memory": create_empty_memory(),
    "mock_question_count": 0,
    "mock_status": "not_started",
    "mock_current_question": "",
    "mock_spoken_response": "",
    "mock_current_stage": "",
    "mock_current_action": "",
    "mock_closing": "",
    "mock_candidate_name": "",
    "mock_job_role": "",
    "mock_difficulty": "Intermediate",
    "mock_question_type": "Mixed Questions",
    "mock_error": "",
    "mock_audio_bytes": None,
    "mock_question_id": "",
    "mock_last_recording_id": "",
    "mock_last_transcript": ""
}

for key, default_value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# =====================================================
# 3. RESUME AND JOB DESCRIPTION CONTEXT
# =====================================================

resume_text = st.session_state.get("resume_text", "")
jd_text = st.session_state.get("jd_text", "")
analysis = st.session_state.get("resume_analysis", {})

if not resume_text or not jd_text or not analysis:
    st.warning(
        "Please complete Resume & JD Analysis before starting the mock interview."
    )
    st.page_link(
        "pages/1_Resume_Analysis.py",
        label="Go to Resume Analysis",
        icon="📄"
    )
    st.stop()

candidate_name = (
    analysis.get("candidate_name", "Candidate")
    if isinstance(analysis, dict)
    else "Candidate"
) or "Candidate"


# =====================================================
# 4. HELPER FUNCTIONS
# =====================================================

def reset_interview():
    """Reset all state belonging to the current mock interview."""
    reset_values = {
        "mock_history": [],
        "mock_memory": create_empty_memory(),
        "mock_question_count": 0,
        "mock_status": "not_started",
        "mock_current_question": "",
        "mock_spoken_response": "",
        "mock_current_stage": "",
        "mock_current_action": "",
        "mock_closing": "",
        "mock_candidate_name": "",
        "mock_job_role": "",
        "mock_difficulty": "Intermediate",
        "mock_question_type": "Mixed Questions",
        "mock_error": "",
        "mock_audio_bytes": None,
        "mock_question_id": "",
        "mock_last_recording_id": "",
        "mock_last_transcript": ""
    }

    for key, value in reset_values.items():
        st.session_state[key] = value


def prepare_audio(text):
    """Generate speech for the current interviewer turn."""
    try:
        st.session_state.mock_audio_bytes = generate_speech(text)
    except Exception as error:
        st.session_state.mock_audio_bytes = None
        st.session_state.mock_error = (
            f"Voice generation failed: {error}"
        )


def set_interviewer_turn(question, spoken_response=None, stage="", action=""):
    """Set the next interviewer turn and create a fresh component question ID."""
    st.session_state.mock_current_question = question
    st.session_state.mock_spoken_response = (
        spoken_response or question
    )
    st.session_state.mock_current_stage = stage
    st.session_state.mock_current_action = action
    st.session_state.mock_question_id = str(uuid.uuid4())
    st.session_state.mock_last_recording_id = ""
    prepare_audio(st.session_state.mock_spoken_response)


def finish_interview():
    """Generate the closing message and mark the interview completed."""
    st.session_state.mock_closing = generate_closing(
        candidate_name=st.session_state.mock_candidate_name,
        job_role=st.session_state.mock_job_role,
        history=st.session_state.mock_history
    )
    st.session_state.mock_status = "completed"
    st.session_state.mock_current_question = ""
    st.session_state.mock_spoken_response = ""
    st.session_state.mock_audio_bytes = None
    st.session_state.mock_error = ""


def process_candidate_answer(transcript):
    """Save an answer, update memory, and prepare the next interviewer turn."""
    transcript = (transcript or "").strip()

    if not transcript:
        st.warning("I couldn't detect speech. Please try answering again.")
        return

    # Save the answer against the question that was just asked.
    if not st.session_state.mock_history:
        st.session_state.mock_history.append({
            "stage": st.session_state.mock_current_stage,
            "action": st.session_state.mock_current_action,
            "question": st.session_state.mock_current_question,
            "answer": transcript
        })
    else:
        st.session_state.mock_history[-1]["answer"] = transcript

    # The greeting is not counted as an interview question.
    if st.session_state.mock_current_action != "greeting":
        st.session_state.mock_question_count += 1

    st.session_state.mock_last_transcript = transcript

    with st.spinner("The interviewer is considering your answer..."):
        result = generate_next_interaction(
            resume_text=resume_text,
            jd_text=jd_text,
            analysis=analysis,
            history=st.session_state.mock_history,
            question_count=st.session_state.mock_question_count,
            emergency_limit=25,
            difficulty=st.session_state.mock_difficulty,
            question_type=st.session_state.mock_question_type,
            interview_memory=st.session_state.mock_memory
        )

    st.session_state.mock_memory = result.get(
        "memory",
        st.session_state.mock_memory
    )

    if result.get("action") == "finish":
        finish_interview()
        return

    next_question = (result.get("question") or "").strip()
    spoken_response = (
        result.get("spoken_response") or next_question
    ).strip()

    if not next_question:
        raise ValueError("The interview engine returned an empty question.")

    # Add the next question now, so the following answer is attached
    # to the correct history item.
    next_stage = result.get("stage", "General Discussion")
    next_action = result.get("action", "new_topic")

    st.session_state.mock_history.append({
        "stage": next_stage,
        "action": next_action,
        "question": next_question,
        "acknowledgement": result.get("acknowledgement", ""),
        "answer": ""
    })

    set_interviewer_turn(
        question=next_question,
        spoken_response=spoken_response,
        stage=next_stage,
        action=next_action
    )


# =====================================================
# 5. INTERVIEW SETUP
# =====================================================

if st.session_state.mock_status == "not_started":

    st.subheader("Interview Setup")

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
        "The interviewer uses your resume, job description, previous answers, "
        "and interview memory to choose relevant follow-up questions."
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
                with st.spinner("Preparing your interviewer..."):
                    greeting = generate_greeting(
                        candidate_name=candidate_name,
                        job_role=job_role.strip()
                    )

                    st.session_state.mock_candidate_name = candidate_name
                    st.session_state.mock_job_role = job_role.strip()
                    st.session_state.mock_difficulty = difficulty
                    st.session_state.mock_question_type = question_type
                    st.session_state.mock_history = [{
                        "stage": "greeting",
                        "action": "greeting",
                        "question": greeting,
                        "answer": ""
                    }]
                    st.session_state.mock_memory = create_empty_memory()
                    st.session_state.mock_question_count = 0
                    st.session_state.mock_status = "active"
                    st.session_state.mock_error = ""
                    st.session_state.mock_last_transcript = ""

                    set_interviewer_turn(
                        question=greeting,
                        spoken_response=greeting,
                        stage="greeting",
                        action="greeting"
                    )

                st.rerun()

            except Exception as error:
                st.error(f"Could not start the interview: {error}")


# =====================================================
# 6. ACTIVE VOICE INTERVIEW
# =====================================================

elif st.session_state.mock_status == "active":

    st.subheader("Interview in Progress")

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Questions Answered",
            st.session_state.mock_question_count
        )
    with col2:
        st.metric("Emergency Limit", 25)

    if st.session_state.mock_current_stage:
        st.caption(
            f"Current topic: {st.session_state.mock_current_stage}"
        )

    st.markdown("### 🤖 AI Interviewer")
    st.info(st.session_state.mock_current_question)

    if st.session_state.mock_error:
        st.error(st.session_state.mock_error)

    audio_b64 = encode_audio(
        st.session_state.mock_audio_bytes
    )

    st.markdown("### 🎤 Voice Conversation")
    st.write(
        "Enable your microphone once. The interviewer will speak first, "
        "then recording will start automatically. Your answer is submitted "
        "after you stop speaking."
    )

    voice_result = voice_recorder(
        question=st.session_state.mock_spoken_response,
        audio_b64=audio_b64,
        question_id=st.session_state.mock_question_id,
        silence_seconds=2,
        active=True,
        key="mock_voice_recorder"
    )

    if isinstance(voice_result, dict):
        recording_type = voice_result.get("type")
        recording_id = voice_result.get("recording_id")
        recording_question_id = voice_result.get("question_id")

        if (
            recording_type == "VOICE_RECORDING"
            and recording_id
            and recording_id != st.session_state.mock_last_recording_id
            and recording_question_id == st.session_state.mock_question_id
        ):
            # Record the ID before processing so reruns cannot process it twice.
            st.session_state.mock_last_recording_id = recording_id

            try:
                encoded_audio = voice_result.get("audio_base64", "")
                audio_bytes = __import__("base64").b64decode(encoded_audio)

                with st.spinner("Transcribing your answer..."):
                    transcript = transcribe_audio(
                        audio_bytes,
                        voice_result.get("mime_type", "audio/webm")
                    )

                if transcript:
                    st.success("Your answer was transcribed.")
                    st.write(transcript)
                    process_candidate_answer(transcript)
                    st.rerun()
                else:
                    st.warning(
                        "No speech was detected. Please try recording again."
                    )

            except Exception as error:
                st.session_state.mock_error = str(error)
                st.error(f"Could not process your answer: {error}")

        elif recording_type == "VOICE_ERROR":
            st.error(
                voice_result.get(
                    "message",
                    "There was a problem with the microphone or audio playback."
                )
            )

    if st.session_state.mock_last_transcript:
        with st.expander("Your latest transcribed answer"):
            st.write(st.session_state.mock_last_transcript)

    with st.expander("Interview Transcript"):
        for index, item in enumerate(st.session_state.mock_history, start=1):
            if item.get("action") == "greeting":
                st.markdown("**AI Interviewer – Greeting**")
            else:
                st.markdown(f"**Interviewer – Turn {index - 1}**")

            if item.get("acknowledgement"):
                st.caption(item["acknowledgement"])

            st.write(item.get("question", ""))

            if item.get("answer"):
                st.markdown("**Candidate:**")
                st.write(item["answer"])

            st.divider()

    with st.expander("Interview Memory"):
        st.json(st.session_state.mock_memory)

    st.divider()

    if st.button(
        "End Interview",
        type="secondary",
        use_container_width=True
    ):
        try:
            with st.spinner("Preparing the interview conclusion..."):
                finish_interview()
            st.rerun()
        except Exception as error:
            st.error(f"Could not generate closing: {error}")


# =====================================================
# 7. COMPLETED INTERVIEW
# =====================================================

elif st.session_state.mock_status == "completed":

    st.success("🎉 Interview Completed!")

    st.subheader("AI Interviewer Closing")
    if st.session_state.mock_closing:
        st.info(st.session_state.mock_closing)

        if st.button("🔊 Play Closing Message"):
            try:
                closing_audio = generate_speech(
                    st.session_state.mock_closing
                )
                st.audio(closing_audio, format="audio/mp3")
            except Exception as error:
                st.error(f"Closing audio failed: {error}")

    st.metric(
        "Total Questions Answered",
        st.session_state.mock_question_count
    )

    st.subheader("Interview Transcript")
    for index, item in enumerate(st.session_state.mock_history, start=1):
        if item.get("action") == "greeting":
            st.markdown("**AI Interviewer – Greeting**")
        else:
            st.markdown(f"**Question {index - 1}:**")

        if item.get("acknowledgement"):
            st.caption(item["acknowledgement"])

        st.write(item.get("question", ""))

        if item.get("answer"):
            st.markdown("**Your Answer:**")
            st.write(item["answer"])
        else:
            st.caption("No answer recorded.")

        st.divider()

    st.subheader("What the Interviewer Remembered")
    st.json(st.session_state.mock_memory)

    if st.button(
        "🔄 Start New Interview",
        type="primary",
        use_container_width=True
    ):
        reset_interview()
        st.rerun()
