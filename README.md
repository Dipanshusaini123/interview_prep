# 🎯 Interview Accelerator – AI-Powered Interview Preparation Platform

An AI-powered interview preparation platform designed to help candidates prepare smarter and interview with confidence. Analyze your resume, generate personalized interview questions, practice through voice-based mock interviews, and receive AI-powered performance feedback.

🌐 **Live Application:** [Interview Accelerator](https://interviewprep2.streamlit.app/)

---

## 🚀 Features

### 📄 1. Resume & Job Description Analysis

- Upload resume and job description in PDF format.
- Extract information from text-based and scanned PDFs.
- Identify relevant skills, qualifications, and experience.
- Analyze compatibility between your profile and the target role.
- Highlight strengths, missing skills, and improvement areas.

### 🧠 2. AI-Powered Interview Preparation

Generate personalized interview questions using three categories:

**Category 1 – General Interview Questions**
- Role-specific technical and behavioural questions.
- Questions covering fundamental concepts and industry knowledge.

**Category 2 – Resume-Specific Questions**
- Questions based on projects, skills, internships, and experience mentioned in your resume.
- Focus on the candidate's actual background.

**Category 3 – Deep-Dive Resume Questions**
- Advanced questions exploring project architecture and implementation.
- Questions about technical decisions, challenges, limitations, and problem-solving.

**Additional capabilities:**
- Select the number of questions to generate.
- Generate personalized sample answers for individual questions.
- Tailor answers according to the resume and target job role.
- Download generated questions.

### 🎤 3. AI Voice-Based Mock Interview

- One-to-one, call-like interview with an AI interviewer.
- AI interviewer asks questions through voice.
- Answer questions using your microphone.
- Convert spoken responses into text using speech recognition.
- Generate adaptive follow-up questions based on candidate responses.
- Maintain conversational context and interview memory.
- Simulate a realistic interview experience.

### 📊 4. AI-Powered Performance Report

Receive detailed feedback based on your actual mock interview responses.

**Overall Evaluation**
- Overall score out of 100.
- Interview readiness assessment.

**Competency Evaluation**
- Role Fit
- Technical Knowledge
- Problem Solving
- Communication
- Confidence
- Depth of Understanding
- Behavioural Fit

**Detailed Feedback**
- Question-wise answer evaluation.
- Strengths and weaknesses.
- Preparation gaps.
- Actionable improvement recommendations.
- Personalized preparation roadmap.

---

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend & Application | Streamlit |
| LLM Integration | Groq API, LangChain |
| Language Model | GPT-OSS-120B |
| Speech Recognition | Groq Whisper – whisper-large-v3-turbo |
| Text-to-Speech | Edge TTS |
| PDF Processing | PyMuPDF, PyPDF |
| OCR | EasyOCR |
| Deployment | Streamlit Community Cloud |
| Version Control | Git & GitHub |

---

## 🔄 Application Workflow

1. **Resume Analysis:** Upload resume and provide job description.
2. **Interview Preparation:** Generate general, resume-specific, or deep-dive questions.
3. **Answer Preparation:** Generate personalized sample answers.
4. **Mock Interview:** Participate in an AI-powered voice interview.
5. **Performance Evaluation:** Receive detailed AI-generated feedback and recommendations.

---

## 🏗️ Project Architecture

```text
Interview Accelerator/
│
├── app.py
│
├── pages/
│   ├── 1_Resume_Analysis.py
│   ├── 3_Mock_Interview.py
│   ├── 4_Performance_Report.py
│   └── 5_Interview_Preparation.py
│
├── modules/
│   ├── resume_jd_analyzer.py
│   └── question_generator.py
│
├── voice/
│   ├── app.py
│   └── index.html
│
├── requirements.txt
│
└── README.md
```

---

## 🔮 Future Enhancements

- Advanced adaptive interview questioning.
- More job roles and interview categories.
- Improved voice interaction and response analysis.
- Interview history and performance tracking.
- Personalized learning recommendations.
- Enhanced interview evaluation and feedback.

---

## 👨‍💻 Developer

**Dipanshu Saini**

B.Tech – Mathematics and Computing  
Delhi Technological University (DTU)



---

⭐ If you find this project interesting, consider giving the repository a star!
