"""
Hiring Platform Web Application
Two-sided platform: Job Posters and Applicants
"""

import streamlit as st
import os
import tempfile
from hiring_platform_db import HiringPlatformDB
from matching_engine import HiringMatchingEngine

# Page config
st.set_page_config(
    page_title="AI Hiring Platform",
    page_icon="💼",
    layout="wide"
)

# Initialize
@st.cache_resource
def init_platform():
    db = HiringPlatformDB()
    engine = HiringMatchingEngine(use_rag=True, use_llm=False)  # Disable LLM for speed
    return db, engine

db, engine = init_platform()

# Session state
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'employer_id' not in st.session_state:
    st.session_state.employer_id = None

# Main app
def main():
    st.title("💼 AI-Powered Hiring Platform")
    st.markdown("### Match the right talent with the right opportunities")
    
    # User type selection
    if st.session_state.user_type is None:
        select_user_type()
    elif st.session_state.user_type == 'applicant':
        applicant_dashboard()
    elif st.session_state.user_type == 'employer':
        employer_dashboard()

def select_user_type():
    """User type selection page"""
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 I'm Looking for a Job")
        st.markdown("""
        - Browse job openings
        - Upload your resume
        - Get instant match scores
        - Apply to multiple jobs
        - Track your applications
        """)
        if st.button("Continue as Job Seeker", type="primary", use_container_width=True):
            st.session_state.user_type = 'applicant'
            st.rerun()
    
    with col2:
        st.markdown("### 🏢 I'm Hiring")
        st.markdown("""
        - Post job openings
        - Receive applications automatically
        - See ranked candidates
        - Filter by match score
        - Review top talent only
        """)
        if st.button("Continue as Employer", type="primary", use_container_width=True):
            st.session_state.user_type = 'employer'
            st.rerun()

def applicant_dashboard():
    """Dashboard for job seekers"""
    st.sidebar.markdown("## 👤 Job Seeker")
    
    # Simple login/register
    if st.session_state.user_id is None:
        applicant_login()
        return
    
    # Sidebar navigation
    page = st.sidebar.radio("Navigation", [
        "Browse Jobs",
        "Apply to Jobs",
        "My Applications",
        "My Profile"
    ])
    
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.user_type = None
        st.rerun()
    
    if page == "Browse Jobs":
        browse_jobs_page()
    elif page == "Apply to Jobs":
        apply_to_jobs_page()
    elif page == "My Applications":
        my_applications_page()
    elif page == "My Profile":
        applicant_profile_page()

def employer_dashboard():
    """Dashboard for employers"""
    st.sidebar.markdown("## 🏢 Employer")
    
    # Simple login/register
    if st.session_state.employer_id is None:
        employer_login()
        return
    
    # Sidebar navigation
    page = st.sidebar.radio("Navigation", [
        "Dashboard",
        "Post New Job",
        "My Job Postings",
        "View Candidates"
    ])
    
    if st.sidebar.button("Logout"):
        st.session_state.employer_id = None
        st.session_state.user_type = None
        st.rerun()
    
    if page == "Dashboard":
        employer_dashboard_page()
    elif page == "Post New Job":
        post_job_page()
    elif page == "My Job Postings":
        my_jobs_page()
    elif page == "View Candidates":
        view_candidates_page()

def applicant_login():
    """Simple applicant login/register"""
    st.subheader("Job Seeker Login/Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        if st.button("Login", type="primary"):
            # Simple email-based lookup (in production, use proper auth)
            st.session_state.user_id = 1  # Mock user ID
            st.success("Logged in successfully!")
            st.rerun()
    
    with tab2:
        name = st.text_input("Full Name")
        email = st.text_input("Email", key="register_email")
        if st.button("Register", type="primary"):
            user_id = db.create_user(email, name)
            st.session_state.user_id = user_id
            st.success(f"Account created! User ID: {user_id}")
            st.rerun()

def employer_login():
    """Simple employer login/register"""
    st.subheader("Employer Login/Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        email = st.text_input("Company Email", key="emp_login_email")
        if st.button("Login", type="primary"):
            st.session_state.employer_id = 1  # Mock employer ID
            st.success("Logged in successfully!")
            st.rerun()
    
    with tab2:
        company = st.text_input("Company Name")
        email = st.text_input("Company Email", key="emp_register_email")
        if st.button("Register", type="primary"):
            employer_id = db.create_employer(email, company)
            st.session_state.employer_id = employer_id
            st.success(f"Company registered! ID: {employer_id}")
            st.rerun()

def browse_jobs_page():
    """Browse available jobs"""
    st.subheader("📋 Browse Job Openings")
    
    jobs = db.get_active_jobs()
    
    if not jobs:
        st.info("No active jobs at the moment. Check back later!")
        return
    
    st.markdown(f"**{len(jobs)} active job openings**")
    
    for job in jobs:
        with st.expander(f"📌 {job['title']} - {job['location'] or 'Remote'}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:**\n{job['description'][:300]}...")
                if job['requirements']:
                    st.markdown(f"**Requirements:**\n{job['requirements'][:200]}...")
            
            with col2:
                if job['salary_range']:
                    st.metric("Salary", job['salary_range'])
                st.metric("Type", job['employment_type'])
                st.metric("Min Score", f"{job['minimum_score']}%")

def apply_to_jobs_page():
    """Apply to jobs with resume upload"""
    st.subheader("🚀 Apply to Jobs")
    
    # Upload resume
    resume_file = st.file_uploader("Upload Your Resume (PDF)", type=['pdf'])
    
    if not resume_file:
        st.info("👆 Upload your resume to see matching jobs and apply")
        return
    
    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(resume_file.getbuffer())
        resume_path = tmp_file.name
    
    st.success(f"✅ Resume uploaded: {resume_file.name}")
    
    # Get active jobs
    jobs = db.get_active_jobs()
    
    if not jobs:
        st.warning("No active jobs available")
        return
    
    # Select jobs to apply to
    st.markdown("### Select Jobs to Apply For:")
    
    selected_jobs = []
    for job in jobs[:10]:  # Show first 10
        if st.checkbox(f"{job['title']} ({job['location'] or 'Remote'})", key=f"job_{job['job_id']}"):
            selected_jobs.append(job['job_id'])
    
    if st.button("Apply to Selected Jobs", type="primary", disabled=len(selected_jobs) == 0):
        with st.spinner(f"Processing {len(selected_jobs)} applications..."):
            results = engine.batch_apply(
                user_id=st.session_state.user_id,
                job_ids=selected_jobs,
                resume_pdf_path=resume_path
            )
            
            st.success(f"✅ Applied to {results['successful_applications']} jobs!")
            
            # Show results
            for app in results['applications']:
                if app['status'] == 'success':
                    match_emoji = "🟢" if app['match_score'] >= 70 else "🟡" if app['match_score'] >= 50 else "🔴"
                    st.markdown(f"{match_emoji} **Job {app['job_id']}**: {app['match_score']:.1f}% match")
        
        # Cleanup
        os.unlink(resume_path)

def my_applications_page():
    """View user's applications"""
    st.subheader("📊 My Applications")
    
    applications = db.get_user_applications(st.session_state.user_id)
    
    if not applications:
        st.info("You haven't applied to any jobs yet.")
        return
    
    st.markdown(f"**Total Applications: {len(applications)}**")
    
    for app in applications:
        status_emoji = {
            'pending': '⏳',
            'reviewed': '👀',
            'shortlisted': '⭐',
            'rejected': '❌',
            'interviewed': '🎤',
            'hired': '🎉'
        }.get(app['status'], '❓')
        
        with st.expander(f"{status_emoji} {app['title']} - {app['match_score']:.1f}% match"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Match Score", f"{app['match_score']:.1f}%")
            with col2:
                st.metric("Status", app['status'].title())
            with col3:
                st.metric("Applied", app['applied_at'][:10])

def applicant_profile_page():
    """User profile page"""
    st.subheader("👤 My Profile")
    user = db.get_user(st.session_state.user_id)
    
    st.text_input("Name", value=user['name'], disabled=True)
    st.text_input("Email", value=user['email'], disabled=True)
    
    if user.get('skills_extracted'):
        st.markdown("### My Skills")
        skills = user['skills_extracted']
        st.markdown(", ".join(skills[:20]))

def employer_dashboard_page():
    """Employer dashboard with statistics"""
    st.subheader("📊 Dashboard")
    
    jobs = db.get_employer_jobs(st.session_state.employer_id, status='active')
    
    if not jobs:
        st.info("You haven't posted any jobs yet. Click 'Post New Job' to get started!")
        return
    
    # Overall stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Jobs", len(jobs))
    
    # Per-job stats
    for job in jobs:
        stats = db.get_job_statistics(job['job_id'])
        
        with st.expander(f"📌 {job['title']}"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Applications", stats['total_applications'])
            with col2:
                st.metric("Avg Score", f"{stats['average_match_score']:.1f}%")
            with col3:
                st.metric("Top Score", f"{stats['top_match_score']:.1f}%")
            with col4:
                if st.button("View Candidates", key=f"view_{job['job_id']}"):
                    st.session_state.selected_job_id = job['job_id']

def post_job_page():
    """Post a new job"""
    st.subheader("📝 Post New Job")
    
    with st.form("post_job_form"):
        title = st.text_input("Job Title *", placeholder="e.g., Senior Data Scientist")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location", placeholder="e.g., San Francisco, CA or Remote")
            employment_type = st.selectbox("Employment Type", 
                ["Full-time", "Part-time", "Contract", "Internship"])
        with col2:
            salary_range = st.text_input("Salary Range", placeholder="e.g., $100k - $150k")
            min_score = st.slider("Minimum Match Score (%)", 0, 100, 50, 5,
                help="Only show candidates above this score")
        
        description = st.text_area("Job Description *", height=200,
            placeholder="Describe the role, responsibilities, and what makes your company great...")
        
        requirements = st.text_area("Requirements *", height=150,
            placeholder="List required skills, experience, education, etc.")
        
        submit = st.form_submit_button("Post Job", type="primary")
        
        if submit:
            if not title or not description or not requirements:
                st.error("Please fill in all required fields (*)")
            else:
                job_id = db.create_job(
                    employer_id=st.session_state.employer_id,
                    title=title,
                    description=description,
                    requirements=requirements,
                    location=location,
                    salary_range=salary_range,
                    employment_type=employment_type,
                    minimum_score=min_score
                )
                st.success(f"✅ Job posted successfully! Job ID: {job_id}")

def my_jobs_page():
    """View employer's jobs"""
    st.subheader("📋 My Job Postings")
    
    jobs = db.get_employer_jobs(st.session_state.employer_id)
    
    if not jobs:
        st.info("You haven't posted any jobs yet.")
        return
    
    for job in jobs:
        stats = db.get_job_statistics(job['job_id'])
        
        status_color = {"active": "🟢", "closed": "🔴", "draft": "🟡"}.get(job['status'], "⚪")
        
        with st.expander(f"{status_color} {job['title']} - {stats['total_applications']} applications"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Posted:** {job['posted_at'][:10]}")
                st.markdown(f"**Location:** {job['location'] or 'Not specified'}")
                st.markdown(f"**Status:** {job['status'].title()}")
            
            with col2:
                if job['status'] == 'active':
                    if st.button("Close Job", key=f"close_{job['job_id']}"):
                        db.update_job_status(job['job_id'], 'closed')
                        st.success("Job closed")
                        st.rerun()

def view_candidates_page():
    """View and manage candidates"""
    st.subheader("👥 View Candidates")
    
    jobs = db.get_employer_jobs(st.session_state.employer_id, status='active')
    
    if not jobs:
        st.info("No active jobs to view candidates for.")
        return
    
    # Select job
    job_options = {f"{job['title']} (ID: {job['job_id']})": job['job_id'] for job in jobs}
    selected_job_name = st.selectbox("Select Job", list(job_options.keys()))
    job_id = job_options[selected_job_name]
    
    job = db.get_job(job_id)
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        min_score = st.slider("Minimum Score", 0, 100, int(job['minimum_score']))
    with col2:
        max_candidates = st.number_input("Max Candidates", 1, 100, 20)
    
    # Get ranked candidates
    candidates = engine.get_ranked_candidates(job_id, min_score=min_score, limit=max_candidates)
    
    if not candidates:
        st.warning(f"No candidates found with score >= {min_score}%")
        return
    
    st.markdown(f"### 🎯 Top {len(candidates)} Candidates (Score >= {min_score}%)")
    
    for i, candidate in enumerate(candidates, 1):
        score = candidate['match_score']
        score_color = "🟢" if score >= 75 else "🟡" if score >= 60 else "🟠"
        
        with st.expander(f"#{i} {score_color} {candidate['name']} - {score:.1f}% match"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Overall Match", f"{score:.1f}%")
                st.metric("Skills Match", f"{candidate['skills_match_score']:.1f}%")
                st.metric("ATS Score", f"{candidate['ats_score']:.0f}/100")
            
            with col2:
                st.markdown("**Matched Skills:**")
                matched = candidate['matched_skills'][:10]
                for skill in matched:
                    st.markdown(f"✅ {skill}")
                if len(candidate['matched_skills']) > 10:
                    st.caption(f"... and {len(candidate['matched_skills']) - 10} more")
            
            with col3:
                st.markdown("**Missing Skills:**")
                missing = candidate['missing_skills'][:5]
                for skill in missing:
                    st.markdown(f"❌ {skill}")
            
            # Actions
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Shortlist", key=f"shortlist_{candidate['application_id']}"):
                    db.update_application_status(candidate['application_id'], 'shortlisted')
                    st.success("Candidate shortlisted!")
            with col2:
                if st.button("Reject", key=f"reject_{candidate['application_id']}"):
                    db.update_application_status(candidate['application_id'], 'rejected')
                    st.warning("Candidate rejected")
            with col3:
                st.download_button(
                    "Download Resume",
                    data="Resume content here",  # You'd load the actual file
                    file_name=f"{candidate['name']}_resume.pdf",
                    key=f"download_{candidate['application_id']}"
                )

if __name__ == "__main__":
    main()
