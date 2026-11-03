
import streamlit as st


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Interview Accelerator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# HTML RENDERING HELPER
# ==========================================

def render_html(html):

    # Remove leading indentation to prevent Markdown
    # from interpreting HTML as code blocks.
    html = "\n".join(
        line.lstrip() for line in html.splitlines()
    )

    st.markdown(
        html,
        unsafe_allow_html=True
    )


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

    /* Main page */
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Hero section */
    .hero {
        padding: 45px 38px;
        border-radius: 18px;
        background: linear-gradient(
            120deg,
            rgba(80, 100, 180, 0.18),
            rgba(100, 160, 190, 0.08)
        );
        border: 1px solid rgba(128,128,128,0.22);
        margin-top: 20px;
        margin-bottom: 38px;
    }

    .hero-tag {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #7799df;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    .hero-title {
        font-size: 43px;
        font-weight: 750;
        line-height: 1.2;
        margin-bottom: 16px;
    }

    .hero-description {
        font-size: 16px;
        line-height: 1.8;
        color: #999999;
        max-width: 760px;
    }

    /* Feature cards */
    .feature-card {
        padding: 25px;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 14px;
        min-height: 190px;
        margin-bottom: 12px;
        transition: border-color 0.2s ease;
    }

    .feature-card:hover {
        border-color: #7799df;
    }

    .feature-icon {
        font-size: 32px;
        margin-bottom: 12px;
    }

    .feature-title {
        font-size: 19px;
        font-weight: 650;
        margin-bottom: 10px;
    }

    .feature-description {
        font-size: 14px;
        line-height: 1.7;
        color: #999999;
    }

    /* Workflow */
    .step-number {
        font-size: 14px;
        font-weight: 700;
        color: #7799df;
        letter-spacing: 1px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #888888;
        font-size: 13px;
        padding: 15px 0;
    }

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🎯 Interview Accelerator")

    st.caption("AI-Powered Interview Preparation")

    st.divider()

    st.markdown("**Your personal interview preparation assistant.**")

    st.caption(
        "Analyze your profile, prepare for interviews "
        "and improve your performance."
    )

    st.divider()

    st.caption("Powered by Streamlit, Groq and AI.")


# ==========================================
# HERO SECTION
# ==========================================

render_html("""
    <div class="hero">

        <div class="hero-tag">
            AI-POWERED CAREER PREPARATION
        </div>

        <div class="hero-title">
            Prepare smarter.<br>
            Interview with confidence.
        </div>

        <div class="hero-description">
            Your personal interview preparation platform.
            Analyze your resume, understand job requirements,
            practice personalized questions and evaluate your
            interview performance — all in one place.
        </div>

    </div>
""")


# ==========================================
# FEATURES SECTION
# ==========================================

st.header("Everything you need to get interview-ready")

st.caption(
    "A complete journey from resume analysis to interview performance."
)

st.write("")


# ------------------------------------------
# FEATURE 1 AND FEATURE 2
# ------------------------------------------

col1, col2 = st.columns(2, gap="large")


with col1:

    render_html("""
        <div class="feature-card">

            <div class="feature-icon">📄</div>

            <div class="feature-title">
                Resume & JD Analysis
            </div>

            <div class="feature-description">
                Analyze your resume against a job description.
                Identify matching skills, missing qualifications,
                strengths and areas for improvement.
            </div>

        </div>
    """)

    st.page_link(
        "pages/1_Resume_Analysis.py",
        label="Analyze your resume",
        icon="📄"
    )


with col2:

    render_html("""
        <div class="feature-card">

            <div class="feature-icon">🧠</div>

            <div class="feature-title">
                Interview Preparation
            </div>

            <div class="feature-description">
                Generate personalized interview questions
                based on your resume, target role and
                job requirements.
            </div>

        </div>
    """)

    st.page_link(
        "pages/2_Interview_Preparation.py",
        label="Prepare for interviews",
        icon="🧠"
    )


# ------------------------------------------
# FEATURE 3 AND FEATURE 4
# ------------------------------------------

col1, col2 = st.columns(2, gap="large")


with col1:

    render_html("""
        <div class="feature-card">

            <div class="feature-icon">🎤</div>

            <div class="feature-title">
                Mock Interview
            </div>

            <div class="feature-description">
                Practice interview questions, submit your
                answers and experience a realistic
                interview simulation.
            </div>

        </div>
    """)

    st.page_link(
        "pages/3_Mock_Interview.py",
        label="Start mock interview",
        icon="🎤"
    )


with col2:

    render_html("""
        <div class="feature-card">

            <div class="feature-icon">📊</div>

            <div class="feature-title">
                Performance Report
            </div>

            <div class="feature-description">
                Review your interview progress, evaluate
                your responses and identify opportunities
                to improve.
            </div>

        </div>
    """)

    st.page_link(
        "pages/4_Performance_Report.py",
        label="View performance report",
        icon="📊"
    )


# ==========================================
# WORKFLOW SECTION
# ==========================================

st.divider()

st.header("How it works")

st.caption(
    "Four simple steps to become better prepared "
    "for your next interview."
)

st.write("")


steps = [
    (
        "01",
        "Upload",
        "Upload your resume and target job description."
    ),

    (
        "02",
        "Analyze",
        "Understand your profile and job compatibility."
    ),

    (
        "03",
        "Practice",
        "Prepare with personalized interview questions."
    ),

    (
        "04",
        "Improve",
        "Review your performance and identify areas to improve."
    )
]


columns = st.columns(4, gap="medium")


for column, (number, title, description) in zip(columns, steps):

    with column:

        with st.container(border=True):

            render_html(
                f'<div class="step-number">{number}</div>'
            )

            st.subheader(title)

            st.caption(description)


# ==========================================
# FOOTER
# ==========================================

st.divider()

render_html("""
    <div class="footer">
        Interview Accelerator · AI-Powered Career Preparation
    </div>
""")
