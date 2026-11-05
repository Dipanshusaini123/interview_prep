
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
        background:
            radial-gradient(circle at 88% 18%, rgba(168, 85, 247, 0.20), transparent 32%),
            radial-gradient(circle at 8% 90%, rgba(34, 211, 238, 0.16), transparent 34%),
            linear-gradient(120deg, rgba(59, 130, 246, 0.16), rgba(139, 92, 246, 0.10), rgba(20, 184, 166, 0.08));
        border: 1px solid rgba(129, 140, 248, 0.35);
        box-shadow: 0 12px 35px rgba(59, 130, 246, 0.08);
        margin-top: 20px;
        margin-bottom: 28px;
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
        border: 1px solid rgba(129, 140, 248, 0.24);
        border-top: 3px solid rgba(99, 102, 241, 0.75);
        border-radius: 14px;
        min-height: 190px;
        margin-bottom: 12px;
        background: linear-gradient(145deg, rgba(59, 130, 246, 0.075), rgba(139, 92, 246, 0.035));
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .feature-card:hover {
        border-color: rgba(129, 140, 248, 0.75);
        box-shadow: 0 10px 24px rgba(99, 102, 241, 0.10);
        transform: translateY(-3px);
    }

    .feature-icon {
        display: inline-block;
        font-size: 30px;
        margin-bottom: 12px;
        padding: 8px 11px;
        border-radius: 12px;
        background: rgba(99, 102, 241, 0.13);
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

    /* Primary navigation link */
    a[data-testid="stPageLink-NavLink"] {
        border: 1px solid rgba(99, 102, 241, 0.45);
        border-radius: 12px;
        background: linear-gradient(100deg, rgba(59, 130, 246, 0.20), rgba(139, 92, 246, 0.18));
        padding: 0.55rem 0.9rem;
        transition: border-color 0.2s ease, filter 0.2s ease;
    }

    a[data-testid="stPageLink-NavLink"]:hover {
        border-color: rgba(129, 140, 248, 0.9);
        filter: brightness(1.12);
    }

    /* Workflow */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(45, 212, 191, 0.22);
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

    # st.caption("Powered by Streamlit, Groq and AI.")


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

# Primary navigation to the next step in the workflow.
st.caption("✨ GET STARTED")
st.page_link(
    "pages/1_Resume_Analysis.py",
    label="Start Resume Analysis",
    icon="📄",
    use_container_width=True
)


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
        "pages/5_Interview_Preparation.py",
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
