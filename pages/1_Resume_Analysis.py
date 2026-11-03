
import streamlit as st

from modules.pdf_extract import extract_pdf_text
from modules.resume_jd_analyzer import analyze_resume


# --------------------------------
# PAGE HEADER
# --------------------------------

st.title("📄 Resume & Job Description Analysis")

st.write(
    "Upload your resume and job description to understand "
    "how well your profile matches the target role."
)

st.divider()


# --------------------------------
# INITIALIZE SESSION STATE
# --------------------------------

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""

if "resume_analysis" not in st.session_state:
    st.session_state.resume_analysis = None


# --------------------------------
# OCR WARNING CALLBACK
# --------------------------------

def show_ocr_warning():

    st.warning(
        "⚠️ Your uploaded document contains scanned or "
        "image-based pages. OCR processing is required "
        "and may take some additional time. Please wait..."
    )


# --------------------------------
# DOCUMENT UPLOAD
# --------------------------------

st.header("Upload Your Documents")

col1, col2 = st.columns(2)

with col1:

    st.subheader("📄 Resume")

    resume_file = st.file_uploader(
        "Upload your Resume (PDF)",
        type=["pdf"],
        key="resume_upload"
    )

with col2:

    st.subheader("📋 Job Description")

    jd_file = st.file_uploader(
        "Upload Job Description (PDF)",
        type=["pdf"],
        key="jd_upload"
    )


st.divider()


# --------------------------------
# ANALYSIS BUTTON
# --------------------------------

if st.button("🚀 Analyze Resume", type="primary"):

    # Validate uploads
    if resume_file is None or jd_file is None:

        st.error(
            "Please upload both your Resume and Job Description."
        )

    else:

        # Reset previous results
        st.session_state.resume_text = ""
        st.session_state.jd_text = ""
        st.session_state.resume_analysis = None

        try:

            # --------------------------------
            # STEP 1: RESUME EXTRACTION
            # --------------------------------

            st.header("Resume Extraction")

            with st.spinner("Extracting Resume..."):

                resume_text = extract_pdf_text(
                    resume_file,
                    on_ocr_detected=show_ocr_warning
                )

            if not resume_text.strip():

                st.error("Could not extract text from Resume.")
                st.stop()

            st.session_state.resume_text = resume_text

            st.success("Resume extracted successfully!")


            # --------------------------------
            # STEP 2: JD EXTRACTION
            # --------------------------------

            st.header("Job Description Extraction")

            with st.spinner("Extracting Job Description..."):

                jd_text = extract_pdf_text(
                    jd_file,
                    on_ocr_detected=show_ocr_warning
                )

            if not jd_text.strip():

                st.error(
                    "Could not extract text from Job Description."
                )
                st.stop()

            st.session_state.jd_text = jd_text

            st.success(
                "Job Description extracted successfully!"
            )


            # --------------------------------
            # STEP 3: GROQ ANALYSIS
            # --------------------------------

            st.divider()

            st.header("🤖 AI Resume Analysis")

            with st.spinner(
                "Analyzing Resume against Job Description..."
            ):

                analysis = analyze_resume(
                    resume_text,
                    jd_text
                )

            st.session_state.resume_analysis = analysis

            st.success("Resume analysis completed successfully!")


        except Exception as e:

            st.error(f"Processing failed: {str(e)}")


# --------------------------------
# DISPLAY ANALYSIS RESULTS
# --------------------------------

analysis = st.session_state.resume_analysis

if analysis is not None:

    st.divider()

    st.header("📊 Analysis Results")


    # --------------------------------
    # MATCH SCORE
    # --------------------------------

    score = analysis.get("match_score", 0)

    try:
        score = float(score)
        score = max(0, min(100, score))
    except (ValueError, TypeError):
        score = 0

    st.subheader("Resume-JD Match Score")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.metric(
            label="Overall Match",
            value=f"{score:g}/100"
        )

    with col2:
        st.progress(score / 100)


    # --------------------------------
    # CANDIDATE INFORMATION
    # --------------------------------

    st.subheader("👤 Candidate Information")

    st.write(
        "**Candidate Name:**",
        analysis.get("candidate_name") or "Not available"
    )

    with st.expander("Education"):
        st.write(analysis.get("education", []))

    with st.expander("Experience"):
        st.write(analysis.get("experience", []))

    with st.expander("Projects"):
        st.write(analysis.get("projects", []))

    with st.expander("Certifications"):
        st.write(analysis.get("certifications", []))


    # --------------------------------
    # SKILLS ANALYSIS
    # --------------------------------

    st.divider()

    st.subheader("🧠 Skills Analysis")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("#### ✅ Matching Skills")
        st.write(analysis.get("matching_skills", []))

        st.markdown("#### ⭐ Additional Skills")
        st.write(analysis.get("additional_skills", []))

    with col2:

        st.markdown("#### ❌ Missing Skills")
        st.write(analysis.get("missing_skills", []))

        st.markdown("#### 🎯 Required Skills")
        st.write(analysis.get("required_skills", []))

    st.markdown("#### Preferred Skills")
    st.write(analysis.get("preferred_skills", []))


    # --------------------------------
    # CANDIDATE EVALUATION
    # --------------------------------

    st.divider()

    st.subheader("💡 Candidate Evaluation")

    st.markdown("#### Strengths")
    st.write(analysis.get("strengths", []))

    st.markdown("#### Areas to Improve")
    st.write(analysis.get("areas_to_improve", []))

    st.markdown("#### Relevant Experience")
    st.write(analysis.get("relevant_experience", []))


    # --------------------------------
    # OVERALL SUMMARY
    # --------------------------------

    st.divider()

    st.subheader("📝 Overall Summary")

    st.write(
        analysis.get("overall_summary", "")
    )


    # --------------------------------
    # EXTRACTED TEXT
    # --------------------------------

    st.divider()

    st.header("Extracted Document Text")

    with st.expander("View Resume Text"):

        st.text_area(
            "Resume Content",
            st.session_state.resume_text,
            height=300
        )

    with st.expander("View Job Description Text"):

        st.text_area(
            "Job Description Content",
            st.session_state.jd_text,
            height=300
        )


    # --------------------------------
    # RAW JSON
    # --------------------------------

    with st.expander("View Complete JSON Response"):

        st.json(analysis)
