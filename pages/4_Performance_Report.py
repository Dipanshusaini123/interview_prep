import json
import re
import streamlit as st
from modules.question_generator import get_llm

st.set_page_config(page_title="Performance Report", page_icon="📊", layout="wide")
st.title("📊 Interview Performance Report")
st.caption("Evidence-based feedback from your completed mock interview.")

interview = st.session_state.get("completed_interview_data")
if not interview:
    st.warning("No completed voice interview found. Complete a mock interview first.")
    st.page_link("pages/3_Mock_Interview.py", label="Go to Mock Interview", icon="🎤")
    st.stop()

history = interview.get("history", [])
answered = [
    x for x in history
    if x.get("action") != "greeting"
    and str(x.get("question", "")).strip()
    and str(x.get("answer", "")).strip()
]
if not answered:
    st.warning("There are no submitted answers to evaluate.")
    st.stop()

if st.session_state.get("performance_report") is None:
    st.info(f"{len(answered)} answered questions are ready for evaluation.")
    if st.button("✨ Generate Performance Report", type="primary", use_container_width=True):
        interview_payload = {
            "candidate_name": interview.get("candidate_name", "Candidate"),
            "job_role": interview.get("job_role", "Not specified"),
            "difficulty": interview.get("difficulty", "Intermediate"),
            "question_type": interview.get("question_type", "Mixed Questions"),
            "resume_analysis": interview.get("resume_analysis", {}),
            "memory": interview.get("memory", {}),
            "question_answers": [
                {"stage": x.get("stage", "General"),
                 "question": x.get("question", ""),
                 "answer": x.get("answer", "")}
                for x in answered
            ]
        }
        prompt = f"""
You are an experienced interviewer. Evaluate ONLY evidence in the supplied resume/JD context
and actual interview answers. Do not invent facts. Do not infer personality or emotional state.
Assess confidence only from verbal answer style, and say when evidence is limited.
Return ONLY valid JSON matching this schema:
{{
 "overall_score": 0,
 "readiness": "Needs Preparation",
 "executive_summary": "specific concise summary",
 "competency_scores": [
  {{"name":"Role Fit","score":0,"reason":"evidence"}},
  {{"name":"Technical Knowledge","score":0,"reason":"evidence"}},
  {{"name":"Problem Solving","score":0,"reason":"evidence"}},
  {{"name":"Communication","score":0,"reason":"evidence"}},
  {{"name":"Confidence","score":0,"reason":"evidence or limited evidence"}},
  {{"name":"Depth of Understanding","score":0,"reason":"evidence"}},
  {{"name":"Behavioural Fit","score":0,"reason":"evidence"}}
 ],
 "question_feedback":[
  {{"question":"asked question","answer_summary":"accurate summary","score":0,
   "assessment":"specific assessment","what_was_good":["specific point"],
   "what_could_be_better":["specific gap"],"ideal_direction":"stronger answer direction"}}
 ],
 "strengths":["specific demonstrated strength"],
 "weaknesses":["specific observed weakness"],
 "preparation_gaps":[
  {{"priority":1,"topic":"topic","why_it_matters":"evidence",
   "what_to_review":["subtopic"]}}
 ],
 "recommendations":["actionable next step"]
}}
Rules: all scores are integers 0-100. Readiness must be exactly Not Ready, Needs Preparation,
Interview Ready, or Strong Candidate. Do not reward unanswered questions. Overall score must
reflect answer quality and competencies. Include question_feedback for every supplied answer.
Be constructive and specific. A resume-JD match score is context, not interview performance.

INTERVIEW DATA:
{json.dumps(interview_payload, ensure_ascii=False, default=str)}
"""
        try:
            with st.spinner("Evaluating your answers with AI..."):
                response = get_llm().invoke(prompt)
                raw = response.content if hasattr(response, "content") else str(response)
                raw = raw.strip()
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("AI response was not a JSON object.")
                st.session_state.performance_report = parsed
                st.session_state.performance_report_error = ""
            st.rerun()
        except Exception as exc:
            st.session_state.performance_report_error = str(exc)
            st.error(f"Report generation failed: {exc}")
    if st.session_state.get("performance_report_error"):
        st.error(st.session_state.performance_report_error)
    st.stop()

report = st.session_state.performance_report
try:
    overall = max(0, min(100, int(report.get("overall_score", 0))))
except (TypeError, ValueError):
    overall = 0

st.divider()
st.subheader(f"Candidate: {interview.get('candidate_name') or 'Candidate'}")
st.write(f"**Target role:** {interview.get('job_role', 'Not specified')}")
st.write(report.get("executive_summary", ""))

c1, c2, c3 = st.columns(3)
c1.metric("Overall Score", f"{overall}/100")
c2.metric("Readiness", report.get("readiness", "Not assessed"))
c3.metric("Answers Evaluated", len(answered))
st.progress(overall / 100)

st.divider()
st.header("Competency Assessment")
for item in report.get("competency_scores", []):
    try:
        value = max(0, min(100, int(item.get("score", 0))))
    except (TypeError, ValueError):
        value = 0
    st.markdown(f"**{item.get('name', 'Competency')} — {value}/100**")
    st.progress(value / 100)
    st.caption(item.get("reason", ""))

left, right = st.columns(2)
with left:
    st.subheader("💪 Strengths")
    for point in report.get("strengths", []):
        st.markdown(f"- {point}")
with right:
    st.subheader("🎯 Areas to Improve")
    for point in report.get("weaknesses", []):
        st.markdown(f"- {point}")

st.divider()
st.header("Question-wise Feedback")
for i, item in enumerate(report.get("question_feedback", []), 1):
    with st.expander(f"Question {i} · Score: {item.get('score', 'N/A')}/100"):
        st.markdown("**Question**")
        st.write(item.get("question", ""))
        st.markdown("**Answer summary**")
        st.write(item.get("answer_summary", ""))
        st.markdown("**Assessment**")
        st.write(item.get("assessment", ""))
        st.markdown("**What was good**")
        for point in item.get("what_was_good", []):
            st.markdown(f"- {point}")
        st.markdown("**What could be better**")
        for point in item.get("what_could_be_better", []):
            st.markdown(f"- {point}")
        st.markdown("**Ideal answer direction**")
        st.write(item.get("ideal_direction", ""))

st.divider()
st.header("📚 Preparation Plan")
for gap in report.get("preparation_gaps", []):
    priority = gap.get("priority", "")
    with st.expander(f"Priority {priority}: {gap.get('topic', 'Topic')}", expanded=(priority == 1)):
        st.write(gap.get("why_it_matters", ""))
        for topic in gap.get("what_to_review", []):
            st.markdown(f"- {topic}")

st.subheader("Recommended Next Steps")
for point in report.get("recommendations", []):
    st.markdown(f"- {point}")

st.divider()
if st.button("🔄 Regenerate Evaluation"):
    st.session_state.performance_report = None
    st.session_state.performance_report_error = ""
    st.rerun()

st.caption("AI-generated practice feedback, not a hiring decision or guarantee of interview outcomes.")
