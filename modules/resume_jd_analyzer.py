
import os
import json

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


# Load environment variables
load_dotenv()

# Initialize Groq
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# General-purpose resume analysis prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert career advisor, professional recruiter,
        and resume analyst.

        Analyze the candidate's resume against the provided job
        description, regardless of industry or job role.

        The job may be technical, non-technical, managerial,
        creative, business-oriented, or any other profession.

        Analyze:

        1. Candidate information:
           - Name
           - Education
           - Experience
           - Projects
           - Certifications

        2. Candidate capabilities:
           - Technical skills (if relevant)
           - Non-technical skills
           - Soft skills
           - Domain knowledge
           - Tools and technologies (if relevant)

        3. Job requirements:
           - Required skills
           - Preferred skills
           - Qualifications
           - Experience requirements
           - Key responsibilities

        4. Comparison:
           - Matching skills
           - Missing skills
           - Additional skills
           - Relevant experience
           - Relevant projects

        5. Evaluation:
           - Match score (0-100)
           - Strengths
           - Areas to improve
           - Overall summary

        IMPORTANT:
        - Adapt analysis to the actual job role.
        - Do not assume every job requires programming.
        - Do not invent candidate qualifications or experience.
        - Distinguish demonstrated skills from inferred skills.
        - Separate mandatory and preferred requirements.
        - Missing preferred skills should be penalized less.
        - If information is unavailable, use empty strings or lists.

        Return ONLY valid JSON in this structure:

        {{
             "candidate_name": "",
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "candidate_skills": [],
            "required_skills": [],
            "preferred_skills": [],
            "matching_skills": [],
            "missing_skills": [],
            "additional_skills": [],
            "relevant_experience": [],
            "match_score": 0,
            "strengths": [],
            "areas_to_improve": [],
            "overall_summary": ""
        }}
        """
    ),
    (
        "human",
        """
        RESUME:

        {resume_text}

        JOB DESCRIPTION:

        {jd_text}
        """
    )
])


def analyze_resume(resume_text, jd_text):

    chain = prompt | llm

    response = chain.invoke({
        "resume_text": resume_text,
        "jd_text": jd_text
    })

    # Convert JSON response into Python dictionary
    result = json.loads(response.content)

    return result



if __name__ == "__main__":

    resume = """
    Rahul Sharma

    Education:
    BBA, Delhi University

    Experience:
    1 year as a Digital Marketing Intern.

    Skills:
    SEO, Social Media Marketing, Canva,
    Content Creation, Communication.

    Projects:
    Managed Instagram campaigns and
    improved social media engagement.
    """

    jd = """
    Job Role: Digital Marketing Executive

    Requirements:
    - SEO and SEM knowledge
    - Social Media Management
    - Content Marketing
    - Google Analytics
    - Communication Skills
    - Campaign Management

    Experience: 0-2 years.
    """

    print("\nAnalyzing Resume against Job Description...\n")

    try:
        result = analyze_resume(resume, jd)

        print("\n========== ANALYSIS RESULT ==========\n")

        import json
        print(json.dumps(result, indent=4, ensure_ascii=False))

    except Exception as e:
        print("Error:", e)
