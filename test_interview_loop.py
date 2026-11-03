
from modules.question_generator import (
    generate_greeting,
    generate_next_interaction,
    generate_closing
)


# =====================================================
# 1. CANDIDATE INFORMATION
# =====================================================

CANDIDATE_NAME = "Dipanshu Saini"
JOB_ROLE = "AI Engineer Intern"

resume_text = """
Dipanshu Saini

Education:
B.Tech Mathematics and Computing,
Delhi Technological University.

Skills:
Python, C++, JavaScript, HTML, CSS,
React, Machine Learning.

Projects:

1. Teaching Buddy
AI chatbot using LangChain, Groq and Streamlit.
Features include answering questions, explaining
concepts and maintaining conversation context.

2. Scholarship Crawler
Automated scholarship discovery, extraction,
verification and database management system.
"""


# =====================================================
# 2. JOB DESCRIPTION
# =====================================================

jd_text = """
Job Role: AI Engineer Intern

Responsibilities:
- Develop AI-powered applications.
- Work with Python and machine learning.
- Build applications using LLMs.
- Work with APIs and data processing.
- Develop and integrate AI solutions.

Requirements:
- Python programming.
- Machine Learning fundamentals.
- Understanding of LangChain and LLMs.
- Problem-solving skills.
- Knowledge of Streamlit.
- Understanding of REST APIs.
"""


# =====================================================
# 3. RESUME ANALYSIS
# =====================================================

analysis = {
    "candidate_name": CANDIDATE_NAME,

    "candidate_skills": [
        "Python",
        "C++",
        "Machine Learning",
        "LangChain",
        "Streamlit",
        "JavaScript",
        "React"
    ],

    "matching_skills": [
        "Python",
        "Machine Learning",
        "LangChain",
        "Streamlit"
    ],

    "missing_skills": []
}


# =====================================================
# 4. INTERVIEW SETTINGS
# =====================================================

DIFFICULTY = "Intermediate"
QUESTION_TYPE = "Mixed Questions"

# Emergency safeguard only.
# This is NOT the target number of questions.
EMERGENCY_LIMIT = 25

history = []


# =====================================================
# 5. GET CANDIDATE ANSWER
# =====================================================

def get_answer():

    while True:

        answer = input("\nYou: ").strip()

        if answer.lower() == "exit":
            return None

        if answer:
            return answer

        print("Please enter an answer or type 'exit'.")


# =====================================================
# 6. SAVE CONVERSATION HISTORY
# =====================================================

def save_history(stage, action, question, answer):

    history.append({
        "stage": stage,
        "action": action,
        "question": question,
        "answer": answer
    })


# =====================================================
# 7. DISPLAY INTERVIEW SUMMARY
# =====================================================

def display_interview_summary(question_count):

    print("\n" + "=" * 60)
    print("               INTERVIEW SUMMARY")
    print("=" * 60)

    print("Candidate:", CANDIDATE_NAME)
    print("Position:", JOB_ROLE)
    print("Interview questions asked:", question_count)

    for index, item in enumerate(history, start=1):

        print(f"\nInteraction {index}")
        print("Stage:", item["stage"])
        print("Interviewer:", item["question"])
        print("Candidate:", item["answer"])

    print("\n" + "=" * 60)


# =====================================================
# 8. RUN DYNAMIC INTERVIEW
# =====================================================

def run_interview():

    question_count = 0
    interview_started = False

    print("\n" + "=" * 60)
    print("              DYNAMIC AI MOCK INTERVIEW")
    print("=" * 60)

    print("\nCandidate:", CANDIDATE_NAME)
    print("Position:", JOB_ROLE)

    try:

        # -------------------------------------------------
        # GREETING
        # -------------------------------------------------

        greeting = generate_greeting(
            candidate_name=CANDIDATE_NAME,
            job_role=JOB_ROLE
        )

        print("\nInterviewer:", greeting)

        answer = get_answer()

        if answer is None:
            print("\nInterview ended by candidate.")
            return

        save_history(
            stage="Greeting",
            action="greeting",
            question=greeting,
            answer=answer
        )

        interview_started = True

        # -------------------------------------------------
        # DYNAMIC INTERVIEW LOOP
        # -------------------------------------------------

        while True:

            print("\n" + "-" * 60)
            print("AI IS ANALYSING THE CONVERSATION...")
            print("-" * 60)

            result = generate_next_interaction(
                resume_text=resume_text,
                jd_text=jd_text,
                analysis=analysis,
                history=history,
                question_count=question_count,
                emergency_limit=EMERGENCY_LIMIT,
                difficulty=DIFFICULTY,
                question_type=QUESTION_TYPE
            )

            action = result["action"]

            # ---------------------------------------------
            # AI DECIDES TO FINISH
            # ---------------------------------------------

            if action == "finish":

                if question_count >= EMERGENCY_LIMIT:
                    print("\nEmergency question limit reached.")
                else:
                    print("\nAI Decision: Interview is complete.")

                break

            # ---------------------------------------------
            # DISPLAY NEXT QUESTION
            # ---------------------------------------------

            question = result["question"]
            stage = result["stage"]

            question_count += 1

            print(f"\nQuestion Number: {question_count}")
            print(f"AI Decision: {action.upper()}")
            print(f"Topic: {stage}")

            print("\nInterviewer:", question)

            # ---------------------------------------------
            # GET CANDIDATE ANSWER
            # ---------------------------------------------

            answer = get_answer()

            if answer is None:

                print("\nCandidate ended the interview.")
                break

            # ---------------------------------------------
            # SAVE HISTORY
            # ---------------------------------------------

            save_history(
                stage=stage,
                action=action,
                question=question,
                answer=answer
            )

            print("\nInterviewer: Thank you for your response.")

        # -------------------------------------------------
        # CLOSING
        # -------------------------------------------------

        print("\n" + "-" * 60)
        print("INTERVIEW CLOSING")
        print("-" * 60)

        closing = generate_closing(
            candidate_name=CANDIDATE_NAME,
            job_role=JOB_ROLE,
            history=history
        )

        print("\nInterviewer:", closing)

    except Exception as error:

        print("\nAn error occurred during the interview:")
        print(error)

    finally:

        if interview_started:
            display_interview_summary(question_count)


# =====================================================
# 9. MAIN
# =====================================================

if __name__ == "__main__":

    try:
        run_interview()

    except KeyboardInterrupt:
        print("\n\nInterview interrupted by user.")
