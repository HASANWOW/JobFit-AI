"""JobFit AI: upload a CV, paste a job posting, get an LLM-powered fit analysis and an application email."""

import streamlit as st
from dotenv import load_dotenv

from jobfit.llm import JobFitClient, LLMConfig
from jobfit.pdf import pdf_to_text
from jobfit.prompts import LANGUAGES

load_dotenv()

st.set_page_config(page_title="JobFit AI", page_icon="🎯", layout="wide")


def read_secrets() -> dict:
    """Streamlit Community Cloud stores the key in st.secrets; locally there may be no secrets file at all."""
    try:
        return dict(st.secrets)
    except Exception:
        return {}


@st.cache_resource
def get_client() -> JobFitClient:
    config = LLMConfig.from_env()
    secrets = read_secrets()
    if not config.api_key and secrets.get("LLM_API_KEY"):
        config.api_key = secrets["LLM_API_KEY"]
        config.base_url = secrets.get("LLM_BASE_URL", config.base_url)
        config.model = secrets.get("LLM_MODEL", config.model)
    return JobFitClient(config)


def bullet_list(items: list[str], empty: str = "-") -> str:
    return "\n".join(f"- {item}" for item in items) if items else empty


st.title("🎯 JobFit AI")
st.caption("Compare your CV with a job posting: match score, skill gaps, CV tips, likely interview questions, and an application email.")

left, right = st.columns(2, gap="large")
with left:
    st.subheader("1. Your CV")
    uploaded = st.file_uploader("Upload your CV (PDF)", type="pdf")
    cv_text = pdf_to_text(uploaded) if uploaded else ""
    cv_text = st.text_area("…or paste / edit the CV text", value=cv_text, height=260)
with right:
    st.subheader("2. The job posting")
    job_text = st.text_area("Paste the job description and requirements", height=330)

language_label = st.radio("Output language", list(LANGUAGES), horizontal=True)
language = LANGUAGES[language_label]

analyze_col, letter_col = st.columns(2)
run_analysis = analyze_col.button("Analyze fit", type="primary", use_container_width=True)
run_letter = letter_col.button("Write application email", use_container_width=True)

if (run_analysis or run_letter) and (not cv_text.strip() or not job_text.strip()):
    st.warning("Add both your CV and the job posting first.")
    st.stop()

try:
    client = get_client() if (run_analysis or run_letter) else None
except ValueError as exc:
    st.error(str(exc))
    st.stop()

if run_analysis and client:
    with st.spinner("Reading your CV against the posting…"):
        try:
            st.session_state["report"] = client.analyze(cv_text, job_text, language)
        except Exception as exc:  # network, auth, or a reply that never validated
            st.error(f"Analysis failed: {exc}")

if run_letter and client:
    with st.spinner("Drafting your application email…"):
        try:
            st.session_state["letter"] = client.cover_letter(cv_text, job_text, language)
        except Exception as exc:
            st.error(f"Could not write the email: {exc}")

report = st.session_state.get("report")
if report:
    st.divider()
    score_col, summary_col = st.columns([1, 3])
    score_col.metric("Match score", f"{report.match_score} / 100")
    score_col.progress(report.match_score / 100)
    summary_col.markdown(f"**Summary**\n\n{report.summary}")

    a, b = st.columns(2)
    a.markdown("**✅ Matched skills**\n" + bullet_list(report.matched_skills))
    b.markdown("**⚠️ Missing skills**\n" + bullet_list(report.missing_skills, "None, nice!"))
    a.markdown("**💪 Strengths for this job**\n" + bullet_list(report.strengths))
    b.markdown("**🛠️ CV improvement tips**\n" + bullet_list(report.improvement_tips))
    st.markdown("**🎤 Likely interview questions**\n" + bullet_list(report.interview_questions))

letter = st.session_state.get("letter")
if letter:
    st.divider()
    st.subheader("Application email")
    st.text_area("Copy and edit before sending", value=letter, height=320)

st.caption("Your CV is only sent to the LLM provider you configure; nothing is stored by this app.")
