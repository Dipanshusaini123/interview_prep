import json
import re
import streamlit as st

from modules.question_generator import get_llm


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Interview Preparation",
    page_icon="🧠",
    layout="wide"
)


# ==========================================
# QUESTION CATEGORIES
# ==========================================

CATEGORY_DETAILS = {
    "Category 1 – General Interview Questions": {
        "description": (
            "Common questions based on the selected job role, "
            "including technical fundamentals, concepts and "
            "behavioural questions."
        )
    },

    "Category 2 – Resume-Specific Questions": {
        "description": (
            "Questions based on your actual resume, projects, "
            "skills, internships and experience."
        )
    },

    "Category 3 – Deep-Dive Resume Questions": {
        "description": (
            "Advanced questions that deeply test your understanding "
            "of projects, implementation, technical decisions, "
            "trade-offs and problem-solving."
        )
    }
}


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_text(value):
    if value is None:
        return ""

    if isinstance(value, str):
        return value

    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        default=str
    )


def clean_json_response(content):

    if isinstance(content, list):
        content = "".join(
            item.get("text", "")
            if isinstance(item, dict)
            else str(item)
            for item in content
        )

    content = str(content).strip()

    content = re.sub(
        r"^```(?:json)?\s*",
        "",
        content,
        flags=re.IGNORECASE
    )

    content = re.sub(r"\s*```$", "", content)

    try:
        return json.loads(content)

    except json.JSONDecodeError:
        match = re.search(
            r"\{.*\}",
            content,
            flags=re.DOTALL
        )

        if not match:
            raise ValueError(
                "AI did not return valid JSON."
            )

        return json.loads(match.group(0))


# ==========================================
# GENERATE INTERVIEW QUESTIONS
# ==========================================

def generate_questions(
    category,
    number_of_questions,
    job_role,
    resume_text,
    jd_text,
    resume_analysis
):

    category_description = CATEGORY_DETAILS[category]["description"]

    prompt = f"""
You are an experienced technical interviewer.

Generate exactly {number_of_questions} unique interview questions.

SELECTED CATEGORY:
{category}

CATEGORY DESCRIPTION:
{category_description}

TARGET JOB ROLE:
{job_role or "Infer from the job description."}

JOB DESCRIPTION:
{jd_text or "Not provided."}

CANDIDATE RESUME:
{resume_text or "Not provided."}

RESUME ANALYSIS:
{resume_analysis or "Not provided."}

INSTRUCTIONS:

1. Generate exactly {number_of_questions} questions.
2. Avoid duplicate questions.
3. Questions must match the selected category.
4. Category 1: Focus on general role-related knowledge.
5. Category 2: Focus on actual resume details.
6. Category 3: Ask challenging questions about project
   architecture, implementation, decisions and limitations.
7. Never invent candidate experience or projects.
8. Give every question a topic and difficulty level.
9. Do not generate answers.

Return ONLY valid JSON:

{{
    "questions": [
        {{
            "number": 1,
            "topic": "Python",
            "difficulty": "Intermediate",
            "question": "Your question here"
        }}
    ]
}}
"""

    response = get_llm().invoke(prompt)

    content = getattr(response, "content", response)

    result = clean_json_response(content)

    questions = result.get("questions", [])

    if not isinstance(questions, list):
        raise ValueError("Invalid questions returned by AI.")

    cleaned_questions = []

    for index, item in enumerate(
        questions[:number_of_questions],
        start=1
    ):

        if isinstance(item, str):

            cleaned_questions.append({
                "number": index,
                "topic": "General",
                "difficulty": "Not specified",
                "question": item.strip()
            })

        elif isinstance(item, dict) and item.get("question"):

            cleaned_questions.append({
                "number": index,
                "topic": item.get("topic", "General"),
                "difficulty": item.get(
                    "difficulty",
                    "Not specified"
                ),
                "question": item["question"].strip()
            })

    if len(cleaned_questions) != number_of_questions:
        raise ValueError(
            f"Expected {number_of_questions} questions, "
            f"but received {len(cleaned_questions)} valid questions."
        )

    return cleaned_questions


# ==========================================
# GENERATE ANSWER FOR INDIVIDUAL QUESTION
# ==========================================

def generate_answer(
    question,
    job_role,
    resume_text,
    jd_text,
    resume_analysis
):

    prompt = f"""
You are an expert interview coach.

Generate a strong, detailed and natural sample answer
for the following interview question.

INTERVIEW QUESTION:
{question}

TARGET JOB ROLE:
{job_role or "Not specified"}

CANDIDATE RESUME:
{resume_text or "Not provided"}

JOB DESCRIPTION:
{jd_text or "Not provided"}

RESUME ANALYSIS:
{resume_analysis or "Not provided"}

INSTRUCTIONS:

1. Tailor the answer to the target job role.
2. Consider the job description.
3. Personalize the answer using relevant projects,
   skills and experience from the candidate's resume.
4. Never invent achievements, metrics, projects,
   tools or professional experience.
5. For behavioural questions, use STAR format:
   Situation, Task, Action and Result.
6. For technical questions, explain the concept clearly
   and include relevant examples.
7. Connect the answer to the candidate's resume
   wherever relevant.
8. If the resume does not contain enough information,
   provide an adaptable sample answer and mention
   what the candidate should customize.
9. Make the answer interview-ready and conversational.
10. Do not simply repeat the question.

Return the answer in readable Markdown.

Include a short Personalization Note if necessary.
"""

    response = get_llm().invoke(prompt)

    return str(
        getattr(response, "content", response)
    ).strip()


# ==========================================
# PAGE CONTENT
# ==========================================

st.title("🧠 Interview Preparation")

st.caption(
    "Generate personalized interview questions "
    "and prepare answers using AI."
)


# ==========================================
# GET SESSION DATA
# ==========================================

resume_text = st.session_state.get(
    "resume_text",
    ""
)

jd_text = st.session_state.get(
    "jd_text",
    ""
)

resume_analysis = st.session_state.get(
    "resume_analysis",
    ""
)


# ==========================================
# RESUME AND JD STATUS
# ==========================================

with st.container(border=True):

    st.subheader("Your Preparation Context")

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            "📄 **Resume:** "
            + ("Loaded" if resume_text else "Not uploaded")
        )

    with col2:

        st.write(
            "💼 **Job Description:** "
            + ("Loaded" if jd_text else "Not provided")
        )

    if not resume_text:

        st.info(
            "Upload your resume in Resume Analysis "
            "to generate resume-specific questions."
        )

    if not jd_text:

        st.info(
            "Add a job description for more relevant "
            "general interview questions."
        )


# ==========================================
# DEFAULT JOB ROLE
# ==========================================

default_role = st.session_state.get(
    "target_role",
    ""
)

if not default_role and isinstance(resume_analysis, dict):

    default_role = (
        resume_analysis.get("target_role")
        or resume_analysis.get("job_role")
        or ""
    )


# ==========================================
# QUESTION GENERATION FORM
# ==========================================

with st.form("question_generation_form"):

    st.subheader("Configure Question Generation")

    category = st.selectbox(
        "Select Question Category",
        options=list(CATEGORY_DETAILS.keys())
    )

    st.caption(
        CATEGORY_DETAILS[category]["description"]
    )

    job_role = st.text_input(
        "Target Job Role",
        value=str(default_role),
        placeholder="e.g. Python Developer, AI Engineer"
    )

    number_of_questions = st.number_input(
        "Number of Questions",
        min_value=1,
        max_value=30,
        value=10,
        step=1
    )

    generate_clicked = st.form_submit_button(
        "✨ Generate Questions",
        type="primary",
        use_container_width=True
    )


# ==========================================
# GENERATE QUESTIONS
# ==========================================

if generate_clicked:

    if category in (
        "Category 2 – Resume-Specific Questions",
        "Category 3 – Deep-Dive Resume Questions"
    ) and not resume_text:

        st.error(
            "Please upload your resume first."
        )

    elif category == "Category 1 – General Interview Questions" and not (
        jd_text or job_role.strip()
    ):

        st.error(
            "Please provide a job description or target job role."
        )

    else:

        with st.spinner("Generating questions using AI..."):

            try:

                questions = generate_questions(
                    category=category,
                    number_of_questions=int(number_of_questions),
                    job_role=job_role.strip(),
                    resume_text=resume_text,
                    jd_text=jd_text,
                    resume_analysis=get_text(resume_analysis)
                )

                st.session_state["generated_question_set"] = {
                    "category": category,
                    "questions": questions
                }

                st.session_state["interview_questions"] = questions

                st.session_state["interview_question_settings"] = {
                    "category": category,
                    "job_role": job_role.strip(),
                    "number_of_questions": int(number_of_questions)
                }

                # Clear previous answers for the new question set.
                st.session_state["generated_question_answers"] = {}

                st.success(
                    f"Successfully generated {len(questions)} questions!"
                )

            except Exception as error:

                st.error(
                    f"Question generation failed: {error}"
                )


# ==========================================
# DISPLAY GENERATED QUESTIONS
# ==========================================

generated_set = st.session_state.get(
    "generated_question_set"
)


if generated_set and generated_set.get("questions"):

    st.divider()

    st.subheader("Your Generated Questions")

    settings = st.session_state.get(
        "interview_question_settings",
        {}
    )

    st.caption(
        f"{settings.get('category', '')} "
        f"· {len(generated_set['questions'])} Questions"
    )

    # Store generated answers.
    if "generated_question_answers" not in st.session_state:

        st.session_state["generated_question_answers"] = {}

    answer_store = st.session_state[
        "generated_question_answers"
    ]

    # ======================================
    # DISPLAY EACH QUESTION
    # ======================================

    for index, question in enumerate(
        generated_set["questions"],
        start=1
    ):

        answer_key = f"answer_{index}"

        with st.container(border=True):

            col1, col2 = st.columns([5, 1])

            with col1:

                st.markdown(
                    f"**Q{question['number']}. {question['topic']}**"
                )

            with col2:

                st.caption(
                    question["difficulty"]
                )

            st.write(
                question["question"]
            )

            # ANSWER BUTTON
            answer_clicked = st.button(
                "💡 Generate Answer",
                key=f"generate_answer_{index}",
                type="secondary"
            )

            if answer_clicked:

                with st.spinner(
                    "Generating personalized answer..."
                ):

                    try:

                        answer = generate_answer(
                            question=question["question"],
                            job_role=settings.get(
                                "job_role",
                                ""
                            ),
                            resume_text=resume_text,
                            jd_text=jd_text,
                            resume_analysis=get_text(resume_analysis)
                        )

                        answer_store[answer_key] = answer

                    except Exception as error:

                        st.error(
                            f"Answer generation failed: {error}"
                        )

            # DISPLAY GENERATED ANSWER
            if answer_key in answer_store:

                with st.expander(
                    "📝 View Sample Answer",
                    expanded=True
                ):

                    st.markdown(
                        answer_store[answer_key]
                    )


    # ======================================
    # DOWNLOAD QUESTIONS
    # ======================================

    export_text = "\n\n".join(
        f"Q{q['number']}. {q['question']}"
        for q in generated_set["questions"]
    )

    st.download_button(
        "⬇️ Download Questions",
        data=export_text,
        file_name="interview_questions.txt",
        mime="text/plain",
        use_container_width=True
    )