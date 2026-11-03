
import streamlit as st


# --------------------------------
# PAGE HEADER
# --------------------------------

st.title("📊 Performance Report")

st.write(
    "Review your mock interview progress, submitted answers "
    "and interview preparation status."
)

st.divider()


# --------------------------------
# GET SESSION DATA
# --------------------------------

questions_text = st.session_state.get("interview_questions", "")

answers = st.session_state.get("mock_answers", {})

analysis = st.session_state.get("resume_analysis")


# --------------------------------
# CHECK INTERVIEW DATA
# --------------------------------

if not questions_text:

    st.warning(
        "No interview data available. Complete Resume Analysis "
        "and Interview Preparation first."
    )

    st.stop()


# --------------------------------
# COUNT QUESTIONS
# --------------------------------

import re

questions = []

for line in questions_text.splitlines():

    line = line.strip()

    if re.match(r"^\d+[\.\)]\s*", line):

        question = re.sub(
            r"^\d+[\.\)]\s*",
            "",
            line
        ).strip()

        if question:
            questions.append(question)


total_questions = len(questions)

answered_questions = len(answers)

unanswered_questions = max(
    0,
    total_questions - answered_questions
)

completion_percentage = (
    (answered_questions / total_questions) * 100
    if total_questions > 0 else 0
)


# --------------------------------
# INTERVIEW OVERVIEW
# --------------------------------

st.header("Interview Overview")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Questions",
        total_questions
    )

with col2:

    st.metric(
        "Answered",
        answered_questions
    )

with col3:

    st.metric(
        "Remaining",
        unanswered_questions
    )


st.subheader("Interview Completion")

st.progress(completion_percentage / 100)

st.write(f"Completion: {completion_percentage:.1f}%")


# --------------------------------
# RESUME ANALYSIS SUMMARY
# --------------------------------

if analysis:

    st.divider()

    st.header("Resume Analysis Summary")

    score = analysis.get("match_score", 0)

    try:
        score = float(score)
    except (ValueError, TypeError):
        score = 0

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Resume-JD Match Score",
            f"{score:g}/100"
        )

    with col2:

        st.metric(
            "Candidate",
            analysis.get("candidate_name") or "Not available"
        )


# --------------------------------
# ANSWER REVIEW
# --------------------------------

st.divider()

st.header("Mock Interview Responses")

if answers:

    for number, answer in sorted(answers.items()):

        with st.expander(f"Question {number}"):

            if 1 <= number <= total_questions:

                st.markdown(
                    f"**{questions[number - 1]}**"
                )

            st.write(answer)

else:

    st.info(
        "No interview answers have been submitted yet. "
        "Visit the Mock Interview page to answer questions."
    )


# --------------------------------
# EVALUATION STATUS
# --------------------------------

st.divider()

st.header("AI Performance Evaluation")

st.info(
    "Detailed answer evaluation is not connected yet. "
    "The next development step will add AI-based scoring, "
    "answer relevance, communication feedback and "
    "improvement recommendations."
)
