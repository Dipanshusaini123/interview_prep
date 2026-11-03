
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq


# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

load_dotenv()

st.title("🧠 Interview Preparation")

st.write(
    "Generate personalized interview questions based on "
    "your resume, job description and target role."
)

st.divider()


# --------------------------------
# CHECK PREVIOUS ANALYSIS
# --------------------------------

resume_text = st.session_state.get("resume_text", "")
jd_text = st.session_state.get("jd_text", "")
analysis = st.session_state.get("resume_analysis")


if not resume_text or not jd_text or analysis is None:

    st.warning(
        "Please complete Resume & JD Analysis before "
        "generating interview questions."
    )

    st.info("Navigate to the Resume Analysis page first.")
    st.stop()


# --------------------------------
# INTERVIEW SETTINGS
# --------------------------------

st.header("Customize Your Interview")

col1, col2 = st.columns(2)

with col1:

    question_type = st.selectbox(
        "Question Category",
        [
            "Mixed Questions",
            "Technical Questions",
            "HR Questions",
            "Behavioral Questions",
            "Role-Specific Questions",
            "Situational Questions"
        ]
    )

with col2:

    difficulty = st.selectbox(
        "Difficulty Level",
        ["Beginner", "Intermediate", "Advanced", "Mixed"]
    )


number_of_questions = st.slider(
    "Number of Questions",
    min_value=5,
    max_value=20,
    value=10
)


# --------------------------------
# GENERATE QUESTIONS
# --------------------------------

if st.button("Generate Interview Questions", type="primary"):

    try:

        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.4
        )

        prompt = f"""
You are an experienced professional interviewer.

Generate interview questions for a candidate based on
their resume and job description.

The questions must be relevant to the actual job role.
Support both technical and non-technical professions.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

RESUME ANALYSIS:
{analysis}

QUESTION CATEGORY: {question_type}

DIFFICULTY: {difficulty}

NUMBER OF QUESTIONS: {number_of_questions}

Instructions:
1. Generate exactly {number_of_questions} questions.
2. Make questions relevant to the job role.
3. Include questions based on the candidate's actual resume.
4. Avoid generic questions wherever possible.
5. Adapt questions to the selected category and difficulty.
6. Do not provide answers or hints.
7. Number each question.
8. Return only the questions, one per line.
"""

        with st.spinner("Generating personalized questions..."):

            response = llm.invoke(prompt)

        questions = response.content

        st.session_state.interview_questions = questions
        st.session_state.interview_question_settings = {
            "category": question_type,
            "difficulty": difficulty,
            "count": number_of_questions
        }

        st.success("Interview questions generated successfully!")

    except Exception as e:

        st.error(f"Question generation failed: {str(e)}")


# --------------------------------
# DISPLAY GENERATED QUESTIONS
# --------------------------------

questions = st.session_state.get("interview_questions")

if questions:

    st.divider()

    st.header("Your Personalized Interview Questions")

    st.markdown(questions)

    st.download_button(
        label="Download Questions",
        data=questions,
        file_name="interview_questions.txt",
        mime="text/plain"
    )
