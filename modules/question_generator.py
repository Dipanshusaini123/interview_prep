
import json
import re
from functools import lru_cache

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# 1. INITIALIZE llm


load_dotenv()


@lru_cache(maxsize=1)
def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.4
    )


# 2. CLEAN GENERATED TEXT

def clean_text(text):
    text = str(text).strip()

    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# 3. INTERVIEW MEMORY

def create_empty_memory():
    """
    Creates the structured memory for one interview.
    """

    return {
        "candidate_background": [],
        "projects_discussed": [],
        "technologies_used": [],
        "skills_demonstrated": [],
        "strengths": [],
        "knowledge_gaps": [],
        "topics_covered": [],
        "pending_followups": [],
        "important_candidate_details": [],
        "conversation_summary": ""
    }


def normalize_memory(memory):
    """
    Ensures that memory always follows the expected structure.
    """

    default_memory = create_empty_memory()

    if not isinstance(memory, dict):
        return default_memory

    normalized = {}

    for key, default_value in default_memory.items():

        value = memory.get(key, default_value)

        if isinstance(default_value, list):

            if isinstance(value, list):
                normalized[key] = [
                    clean_text(item)
                    for item in value
                    if isinstance(item, str) and item.strip()
                ]
            else:
                normalized[key] = []

        else:

            if isinstance(value, str):
                normalized[key] = clean_text(value)
            else:
                normalized[key] = ""

    return normalized


def format_interview_memory(memory):
    """
    Converts structured memory into readable context for the LLM.
    """

    memory = normalize_memory(memory)

    return json.dumps(
        memory,
        indent=2,
        ensure_ascii=False
    )



def merge_interview_memory(previous_memory, returned_memory):
    """
    Merge the LLM's updated memory with the existing memory.

    This protects useful older details if the model accidentally returns
    only newly learned items or omits a field.
    """
    previous = normalize_memory(previous_memory)
    returned = returned_memory if isinstance(returned_memory, dict) else {}

    merged = {}

    for key, default_value in create_empty_memory().items():
        if isinstance(default_value, list):
            old_items = previous.get(key, [])
            new_items = returned.get(key)

            if not isinstance(new_items, list):
                new_items = []

            combined = []
            seen = set()

            # Keep existing context first, then add newly returned details.
            for item in old_items + new_items:
                if not isinstance(item, str) or not item.strip():
                    continue

                cleaned = clean_text(item)
                comparison_key = cleaned.casefold()

                if comparison_key not in seen:
                    seen.add(comparison_key)
                    combined.append(cleaned)

            merged[key] = combined

        else:
            new_summary = returned.get(key)
            if isinstance(new_summary, str) and new_summary.strip():
                merged[key] = clean_text(new_summary)
            else:
                merged[key] = previous.get(key, "")

    return merged


# 4. FORMAT CONVERSATION HISTORY

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


# 5. PARSE AI JSON RESPONSE

def parse_json_response(response_text):
    """
    Parse a JSON object returned by the LLM.

    Handles plain JSON, Markdown code fences, and text surrounding
    the first valid JSON object.
    """
    text = str(response_text).strip()
    text = re.sub(r"^```(?:json)?\\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\\s*```$", "", text)

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # Decode from the first opening brace instead of using a greedy
    # regular expression, which can accidentally capture multiple objects.
    decoder = json.JSONDecoder()
    for index, character in enumerate(text):
        if character == "{":
            try:
                parsed, _ = decoder.raw_decode(text[index:])
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue

    raise ValueError(f"Could not parse AI response as a JSON object: {text}")


# 6. GENERATE INTERVIEW GREETING

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


# 7. GENERATE DYNAMIC NEXT INTERACTION

def generate_next_interaction(
    resume_text,
    jd_text,
    analysis,
    history,
    question_count,
    emergency_limit=25,
    difficulty="Intermediate",
    question_type="Mixed Questions",
    interview_memory=None
):
    """
    Generates the next interview interaction.

    Existing parameters are preserved.
    interview_memory is an optional new parameter.

    Returns:
    {
        "action": ...,
        "stage": ...,
        "question": ...,
        "acknowledgement": ...,
        "spoken_response": ...,
        "memory": {...}
    }
    """

    memory = normalize_memory(interview_memory)

    # Emergency safeguard, not a target question count
    if question_count >= emergency_limit:

        return {
            "action": "finish",
            "stage": "closing",
            "question": "",
            "acknowledgement": "",
            "spoken_response": "",
            "memory": memory
        }

    llm = get_llm()

    # Keep recent conversation alongside the rolling memory.
    # Older information should already be captured in memory.
    recent_history = history[-12:] if history else []

    conversation_history = format_conversation_history(
        recent_history
    )

    if isinstance(analysis, dict):
        analysis_text = json.dumps(analysis, indent=2)
    else:
        analysis_text = str(analysis)

    memory_context = format_interview_memory(memory)

    prompt = f"""
You are an intelligent, adaptive and professional AI interviewer.

Your responsibility is to conduct a realistic interview
that adapts continuously to the candidate's answers.

You must maintain strong conversational continuity.

There is NO fixed target number of interview questions.

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

Follow the selected question category:
- Technical: focus on role-relevant technical concepts and practical implementation.
- HR: focus on motivation, communication, teamwork, ownership and workplace situations.
- Project-Based: focus on the candidate's actual projects, decisions, implementation and challenges.
- Resume-Based: focus on claims, skills, education and experience stated in the resume.
- Mixed Questions: balance relevant technical, project, resume and HR questions.

Questions already asked: {question_count}

==================================================
PERSISTENT INTERVIEW MEMORY
==================================================

{memory_context}

==================================================
RECENT CONVERSATION HISTORY
==================================================

{conversation_history}

==================================================
YOUR DECISION-MAKING RESPONSIBILITY
==================================================

Choose exactly ONE action:

1. follow_up
   Ask a relevant follow-up based on the latest answer.

2. new_topic
   Explore another relevant area of the candidate's
   resume or the job description.

3. finish
   End the interview because sufficient information
   has been gathered.

==================================================
CONVERSATIONAL MEMORY RULES
==================================================

You must maintain and update the interview memory
after every candidate answer.

Remember:

1. Projects the candidate has discussed.
2. Technologies and tools the candidate has actually used.
3. Skills demonstrated through their answers.
4. Candidate strengths supported by their explanations.
5. Knowledge gaps or areas where explanations were weak.
6. Topics already covered.
7. Follow-up questions that are still worth exploring.
8. Important details shared by the candidate.
9. A concise summary of the conversation so far.

IMPORTANT:

- Return the complete updated memory, not only newly learned items.
- Preserve useful information from earlier answers.
- If the candidate corrects a detail, use the corrected detail and remove the incorrect version.
- Do not invent projects, skills or experience.
- Distinguish between skills mentioned in the resume
  and skills actually demonstrated in answers.
- Remove duplicate entries.
- Keep the memory concise and useful.
- Update the summary as the interview progresses.
- If the candidate corrects an earlier statement,
  retain the corrected information.

==================================================
CONTEXT-AWARE INTERVIEW RULES
==================================================

A. UNDERSTANDING ANSWERS

- Carefully analyse the latest candidate answer.
- Consider its relevance, clarity and detail.
- Use previous answers and persistent memory.
- Never invent experience or qualifications.

B. FOLLOW-UP QUESTIONS

- Ask about reasoning, implementation, decisions,
  examples, challenges or lessons learned.
- Refer to details the candidate mentioned earlier
  whenever relevant.
- Avoid asking questions already answered.
- Do not ask more than TWO consecutive follow-ups
  about the same topic.
- Move to another topic when appropriate.

C. VAGUE OR SHORT ANSWERS

- Ask one simple clarification question.
- If the candidate still cannot explain, move on.
- Do not repeatedly question the same point.

D. IRRELEVANT ANSWERS

- Ask one polite clarification.
- If the answer remains unrelated, move on.

E. HONEST ANSWERS

- If the candidate says they used AI tools,
  ask what they personally understood,
  implemented or learned.
- Do not assume every project was independently developed.
- Do not embarrass or judge the candidate.

F. TOPIC DIVERSITY

Explore relevant areas based on the resume and JD:

- Education and academic background
- Projects and practical experience
- Programming and technical skills
- Machine learning and AI knowledge
- LLMs and API integration
- Problem-solving
- Communication and teamwork
- Role-specific professional knowledge

Avoid spending the entire interview on one project.

G. ADAPTIVE DIFFICULTY

- If the candidate struggles, simplify the next question.
- If the candidate gives a strong explanation,
  ask a deeper question.
- Match difficulty to demonstrated understanding.

H. INTERVIEW COMPLETION

- There is no required minimum question count.
- Do not finish simply because a particular number
  of questions has been reached.
- Continue if important areas remain unexplored.
- Finish when sufficient relevant information
  has been gathered.
- A weak answer alone is not a reason to finish.

I. NATURAL CONVERSATION

Generate a short acknowledgement of the candidate's
latest answer before asking the next question.

The acknowledgement should:

- Sound natural and conversational.
- Be brief, usually one sentence.
- Refer to something meaningful in the answer.
- Avoid exaggerated praise.
- Avoid giving performance feedback or scores.
- Not reveal expected answers.

Then ask exactly ONE focused question.

For example:

Candidate:
"I used Python and TensorFlow for my prediction project."

Acknowledgement:
"Interesting, you mentioned using TensorFlow
for your prediction project."

Question:
"How did you decide which features were
important for your model?"

If the answer is unclear, acknowledge it politely
and ask one clarification question.

If finishing the interview, acknowledgement can be empty.

J. QUESTION QUALITY

- Ask exactly ONE focused question.
- Keep questions concise and conversational.
- Do not combine unrelated questions.
- Do not repeat previously asked questions.
- Never provide hints, expected answers, feedback
  or scores during the interview.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY a valid JSON object.

For follow_up or new_topic:

{{
    "action": "follow_up",
    "stage": "short descriptive topic name",
    "acknowledgement": "Brief natural acknowledgement",
    "question": "One focused next question",
    "memory": {{
        "candidate_background": [],
        "projects_discussed": [],
        "technologies_used": [],
        "skills_demonstrated": [],
        "strengths": [],
        "knowledge_gaps": [],
        "topics_covered": [],
        "pending_followups": [],
        "important_candidate_details": [],
        "conversation_summary": ""
    }}
}}

For finishing:

{{
    "action": "finish",
    "stage": "closing",
    "acknowledgement": "",
    "question": "",
    "memory": {{
        "candidate_background": [],
        "projects_discussed": [],
        "technologies_used": [],
        "skills_demonstrated": [],
        "strengths": [],
        "knowledge_gaps": [],
        "topics_covered": [],
        "pending_followups": [],
        "important_candidate_details": [],
        "conversation_summary": ""
    }}
}}

The memory values must be updated using the existing
memory and the complete available conversation context.

Do not include Markdown or explanations outside JSON.
"""

    response = llm.invoke(prompt)

    result = parse_json_response(response.content)

    action = result.get("action")
    action = action.strip().lower() if isinstance(action, str) else action
    stage = result.get("stage", "")
    question = result.get("question", "")
    acknowledgement = result.get("acknowledgement", "")

    # Validate action
    if action not in ["follow_up", "new_topic", "finish"]:
        raise ValueError(f"Invalid AI action: {action}")

    # Update structured memory
    updated_memory = merge_interview_memory(
        memory,
        result.get("memory", {})
    )

    # Finish interview
    if action == "finish":

        return {
            "action": "finish",
            "stage": "closing",
            "question": "",
            "acknowledgement": "",
            "spoken_response": "",
            "memory": updated_memory
        }

    # Validate question
    if not isinstance(question, str) or not question.strip():
        raise ValueError("The AI returned an empty question.")

    if not isinstance(stage, str) or not stage.strip():
        stage = "General Discussion"

    if not isinstance(acknowledgement, str):
        acknowledgement = ""

    question = clean_text(question)
    acknowledgement = clean_text(acknowledgement)

    # Used later by the voice interface.
    # Existing page can continue using "question".
    spoken_response = question

    if acknowledgement:
        spoken_response = (
            f"{acknowledgement} {question}"
        )

    return {
        "action": action,
        "stage": clean_text(stage),
        "question": question,
        "acknowledgement": acknowledgement,
        "spoken_response": spoken_response,
        "memory": updated_memory
    }


# 8. GENERATE INTERVIEW CLOSING


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

