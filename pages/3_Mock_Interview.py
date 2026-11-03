
import streamlit as st
import re


# --------------------------------
# PAGE HEADER
# --------------------------------

st.title("🎤 Mock Interview")

st.write(
    "Practice answering personalized interview questions "
    "and save your responses for performance evaluation."
)

st.divider()


# --------------------------------
# CHECK GENERATED QUESTIONS
# --------------------------------

questions_text = st.session_state.get("interview_questions")

if not questions_text:

    st.warning(
        "No interview questions found. Please generate "
        "questions in the Interview Preparation page first."
    )

    st.stop()


# --------------------------------
# EXTRACT QUESTIONS
# --------------------------------

questions = []

for line in questions_text.splitlines():

    line = line.strip()

    # Accept numbered questions such as 1. or 1)
    if re.match(r"^\d+[\.\)]\s*", line):

        question = re.sub(
            r"^\d+[\.\)]\s*",
            "",
            line
        ).strip()

        if question:
            questions.append(question)


if not questions:

    st.error(
        "Could not identify questions. Please generate "
        "the questions again."
    )

    st.stop()


# --------------------------------
# INITIALIZE ANSWERS
# --------------------------------

if "mock_answers" not in st.session_state:
    st.session_state.mock_answers = {}


# --------------------------------
# INTERVIEW PROGRESS
# --------------------------------

answered_count = len(st.session_state.mock_answers)

total_questions = len(questions)

st.subheader("Interview Progress")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Questions", total_questions)

with col2:
    st.metric("Answered Questions", answered_count)

st.progress(answered_count / total_questions)

st.divider()


# --------------------------------
# SELECT QUESTION
# --------------------------------

question_number = st.selectbox(
    "Select Interview Question",
    options=list(range(1, total_questions + 1)),
    format_func=lambda x: f"Question {x}"
)

current_question = questions[question_number - 1]

st.subheader(f"Question {question_number}")

st.info(current_question)


# --------------------------------
# ANSWER INPUT
# --------------------------------

existing_answer = st.session_state.mock_answers.get(
    question_number,
    ""
)

answer = st.text_area(
    "Your Answer",
    value=existing_answer,
    height=200,
    placeholder="Write your answer here..."
)


# --------------------------------
# SAVE ANSWER
# --------------------------------

if st.button("Save Answer", type="primary"):

    if not answer.strip():

        st.warning("Please enter your answer first.")

    else:

        st.session_state.mock_answers[question_number] = answer.strip()

        st.success("Your answer has been saved!")


# --------------------------------
# VIEW ALL RESPONSES
# --------------------------------

st.divider()

with st.expander("View All Saved Answers"):

    if st.session_state.mock_answers:

        for number, saved_answer in sorted(
            st.session_state.mock_answers.items()
        ):

            st.markdown(f"**Question {number}:**")
            st.write(questions[number - 1])

            st.markdown("**Your Answer:**")
            st.write(saved_answer)

            st.divider()

    else:

        st.info("You haven't saved any answers yet.")
