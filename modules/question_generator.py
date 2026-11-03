
import json
import re
from functools import lru_cache

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# =====================================================
# 1. INITIALIZE LLM
# =====================================================

load_dotenv()


@lru_cache(maxsize=1)
def get_llm():

    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.4
    )


# =====================================================
# 2. CLEAN GENERATED TEXT
# =====================================================

def clean_text(text):

    text = str(text).strip()

    # Remove accidental Markdown formatting
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # Remove unnecessary line breaks and extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =====================================================
# 3. FORMAT CONVERSATION HISTORY
# =====================================================

def format_conversation_history(history):

    if not history:
        return "No previous conversation."

    conversation = []

    for index, item in enumerate(history, start=1):

        conversation.append(
            f"""
            Interaction {index}

            Stage: {item.get("stage", "")}
            Action: {item.get("action", "")}

            Interviewer:
            {item.get("question", "")}

            Candidate:
            {item.get("answer", "")}
            """
        )

    return "\n".join(conversation)


# =====================================================
# 4. PARSE AI JSON RESPONSE
# =====================================================

def parse_json_response(response_text):

    text = str(response_text).strip()

    # Remove Markdown code fences
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        # Attempt to extract a JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            return json.loads(match.group())

        raise ValueError(
            f"Could not parse AI response as JSON: {text}"
        )


# =====================================================
# 5. GENERATE INTERVIEW GREETING
# =====================================================

def generate_greeting(candidate_name, job_role):

    llm = get_llm()

    prompt = f"""
    You are a friendly and professional AI interviewer.

    Candidate name: {candidate_name}
    Job position: {job_role}

    Start the interview naturally.

    Instructions:

    1. Greet the candidate by name.
    2. Introduce yourself as the AI interviewer.
    3. Mention the job position.
    4. Briefly explain the interview.
    5. Ask how the candidate is doing today.
    6. Keep the tone warm and professional.
    7. Do not ask technical questions yet.
    8. Keep the greeting concise.

    Return only the greeting message.
    """

    response = llm.invoke(prompt)

    greeting = clean_text(response.content)

    if not greeting:
        raise ValueError("The AI returned an empty greeting.")

    return greeting


# =====================================================
# 6. GENERATE DYNAMIC NEXT INTERACTION
# =====================================================

def generate_next_interaction(
    resume_text,
    jd_text,
    analysis,
    history,
    question_count,
    emergency_limit=25,
    difficulty="Intermediate",
    question_type="Mixed Questions"
):

    # Emergency safeguard, not a target question count
    if question_count >= emergency_limit:

        return {
            "action": "finish",
            "stage": "closing",
            "question": ""
        }

    llm = get_llm()

    conversation_history = format_conversation_history(history)

    if isinstance(analysis, dict):
        analysis_text = json.dumps(analysis, indent=2)
    else:
        analysis_text = str(analysis)

    prompt = f"""
    You are an intelligent, adaptive and professional AI interviewer.

    Your responsibility is to conduct a realistic interview
    that adapts continuously to the candidate's answers.

    There is NO fixed target number of interview questions.

    You must decide independently when enough relevant
    information has been gathered to conclude the interview.

    ==================================================
    CANDIDATE RESUME
    ==================================================

    {resume_text}

    ==================================================
    JOB DESCRIPTION
    ==================================================

    {jd_text}

    ==================================================
    RESUME ANALYSIS
    ==================================================

    {analysis_text}

    ==================================================
    INTERVIEW SETTINGS
    ==================================================

    Difficulty: {difficulty}
    Question category: {question_type}

    Questions already asked: {question_count}

    ==================================================
    COMPLETE CONVERSATION HISTORY
    ==================================================

    {conversation_history}

    ==================================================
    YOUR DECISION-MAKING RESPONSIBILITY
    ==================================================

    After analysing the complete conversation, choose
    exactly ONE of the following actions:

    1. follow_up
       Ask a relevant follow-up based on the candidate's
       latest answer.

    2. new_topic
       Explore a different relevant area of the candidate's
       resume or the job description.

    3. finish
       End the interview because sufficient relevant
       information has been gathered.

    ==================================================
    DYNAMIC INTERVIEW RULES
    ==================================================

    A. STARTING THE INTERVIEW

    - If no interview question has been asked yet,
      ask the candidate to introduce themselves.
    - Keep the opening question natural and simple.

    B. UNDERSTANDING ANSWERS

    - Carefully analyse the latest candidate answer.
    - Consider its relevance, clarity and detail.
    - Use previous answers to understand the candidate's
      actual background and knowledge.
    - Never invent experience or qualifications.

    C. FOLLOW-UP QUESTIONS

    - If an answer is interesting or needs clarification,
      ask a relevant follow-up.
    - Explore the candidate's reasoning, implementation,
      decisions, examples or challenges.
    - Do not ask repeated questions in different words.
    - Do not ask more than TWO consecutive follow-ups
      about the same topic.
    - If the candidate cannot explain something after
      clarification, move to another topic.

    D. VAGUE OR SHORT ANSWERS

    - If the answer is unclear, ask one simple
      clarification question.
    - If the candidate still cannot explain, move on.
    - Do not repeatedly question the candidate about
      the same point.

    E. IRRELEVANT ANSWERS

    - If the answer is unrelated to the question,
      ask one polite clarification.
    - If the candidate's response remains unrelated,
      move to another relevant topic.

    F. HONEST ANSWERS

    - If the candidate says they used AI tools,
      ask what they personally understood,
      implemented or learned.
    - Do not assume that every project was independently
      developed by the candidate.
    - Do not judge or embarrass the candidate.

    G. TOPIC DIVERSITY

    Explore relevant areas based on the resume and JD,
    such as:

    - Education and academic background
    - Projects and practical experience
    - Programming and technical skills
    - Machine learning and AI knowledge
    - LLMs and API integration
    - Problem-solving
    - Communication and teamwork
    - Role-specific professional knowledge

    Do not follow a fixed topic sequence.
    Avoid spending the entire interview on one project.

    H. ADAPTIVE DIFFICULTY

    - If the candidate struggles, simplify the next question.
    - If the candidate gives a strong explanation,
      ask a deeper question.
    - Match the question difficulty to the candidate's
      demonstrated understanding.

    I. INTERVIEW COMPLETION

    - There is no required minimum or target number
      of questions.
    - Do not finish simply because a particular
      number of questions has been reached.
    - Do not continue merely to increase interview length.
    - Consider whether the candidate's background,
      relevant projects, important skills and job-related
      competencies have been explored sufficiently.
    - If important areas remain unexplored, continue.
    - If enough information has been gathered,
      choose finish.
    - A weak answer alone is not a reason to finish
      the entire interview.

    J. QUESTION QUALITY

    - Ask exactly ONE focused question at a time.
    - Keep questions concise and conversational.
    - Avoid combining several unrelated questions.
    - Do not repeat previously asked questions.
    - Never provide hints, expected answers, feedback
      or scores during the interview.

    ==================================================
    OUTPUT FORMAT
    ==================================================

    Return ONLY a valid JSON object.

    For a follow-up:

    {{
        "action": "follow_up",
        "stage": "short descriptive topic name",
        "question": "Your next question"
    }}

    For a new topic:

    {{
        "action": "new_topic",
        "stage": "short descriptive topic name",
        "question": "Your next question"
    }}

    To finish:

    {{
        "action": "finish",
        "stage": "closing",
        "question": ""
    }}

    Do not include Markdown or explanations outside JSON.
    """

    response = llm.invoke(prompt)

    result = parse_json_response(response.content)

    action = result.get("action")
    stage = result.get("stage")
    question = result.get("question")

    if action not in ["follow_up", "new_topic", "finish"]:
        raise ValueError(f"Invalid AI action: {action}")

    if action == "finish":

        return {
            "action": "finish",
            "stage": "closing",
            "question": ""
        }

    if not isinstance(question, str) or not question.strip():
        raise ValueError("The AI returned an empty question.")

    if not isinstance(stage, str) or not stage.strip():
        stage = "General Discussion"

    return {
        "action": action,
        "stage": clean_text(stage),
        "question": clean_text(question)
    }


# =====================================================
# 7. GENERATE INTERVIEW CLOSING
# =====================================================

def generate_closing(candidate_name, job_role, history):

    llm = get_llm()

    conversation_history = format_conversation_history(history)

    prompt = f"""
    You are a professional AI interviewer.

    Candidate: {candidate_name}
    Position: {job_role}

    Interview conversation:
    {conversation_history}

    End the interview professionally.

    Instructions:

    1. Thank the candidate for their time.
    2. Appreciate their participation.
    3. Mention that the interview has concluded.
    4. Wish them luck with the next steps.
    5. Do not announce a hiring decision.
    6. Do not provide scores or performance feedback.
    7. Keep the message warm and concise.

    Return only the closing message.
    """

    response = llm.invoke(prompt)

    closing = clean_text(response.content)

    if not closing:
        raise ValueError("The AI returned an empty closing.")

    return closing


# =====================================================
# 8. INDEPENDENT FUNCTION TEST
# =====================================================

if __name__ == "__main__":

    sample_resume = """
    Rahul Sharma
    BBA Graduate
    Experience: Digital Marketing Intern
    Skills: SEO, Social Media Marketing, Canva.
    """

    sample_jd = """
    Job Role: Digital Marketing Executive
    Requirements: SEO, social media marketing,
    content creation and communication.
    """

    sample_analysis = {
        "candidate_name": "Rahul Sharma",
        "candidate_skills": [
            "SEO",
            "Social Media Marketing",
            "Canva"
        ]
    }

    print("\nTESTING GREETING")

    greeting = generate_greeting(
        "Rahul Sharma",
        "Digital Marketing Executive"
    )

    print("\n", greeting)

    print("\nTESTING DYNAMIC QUESTION GENERATION")

    result = generate_next_interaction(
        resume_text=sample_resume,
        jd_text=sample_jd,
        analysis=sample_analysis,
        history=[],
        question_count=0
    )

    print(json.dumps(result, indent=4))

    print("\nModule test completed.")
