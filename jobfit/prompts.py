"""Prompt templates. Kept separate so they can be tuned without touching app logic."""

LANGUAGES = {"Bahasa Indonesia": "Indonesian", "English": "English"}

ANALYSIS_SYSTEM = """You are an experienced technical recruiter and career coach.
You compare a candidate's CV with a job posting and give an honest, specific assessment.
Rules:
- Base every statement only on the CV and the job posting. Never invent experience the CV does not show.
- Be concrete: name the actual skills, tools, and projects.
- Reply with ONE JSON object and nothing else."""

ANALYSIS_USER = """Compare this CV with the job posting.

Return a JSON object with exactly these keys:
- "match_score": integer 0-100, how well the CV fits the job's requirements
- "summary": 2-3 sentences on the overall fit
- "matched_skills": list of requirements from the posting the CV clearly covers
- "missing_skills": list of requirements the CV does not show
- "strengths": list of the candidate's strongest selling points for THIS job
- "improvement_tips": list of concrete edits to the CV for this job
- "interview_questions": list of 5 questions the interviewer is likely to ask this candidate

Write all text values in {language}.

=== JOB POSTING ===
{job}

=== CV ===
{cv}"""

COVER_LETTER_SYSTEM = """You write concise, sincere job application emails for students applying to internships.
Only use facts that appear in the CV. Do not exaggerate. Keep it under 250 words."""

COVER_LETTER_USER = """Write an application email in {language} for this job, from the candidate whose CV is below.
Include a subject line on the first line, starting with "Subject:" (or "Subjek:" in Indonesian).
Mention 2-3 of the candidate's most relevant projects or experiences for this job.

=== JOB POSTING ===
{job}

=== CV ===
{cv}"""
