"""
ATS Resume Analyzer - Web Interface
Streamlit-based web application for resume analysis
"""

import streamlit as st
import tempfile
import os
import json
from ats_pipeline import ATSPipeline
import time


# Page configuration
st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)


def get_match_color(score):
    """Get color based on match score"""
    if score >= 75:
        return "#28a745"  # Green
    elif score >= 60:
        return "#17a2b8"  # Blue
    elif score >= 45:
        return "#ffc107"  # Yellow
    elif score >= 30:
        return "#fd7e14"  # Orange
    else:
        return "#dc3545"  # Red


def display_results(results):
    """Display analysis results in a formatted way"""
    
    if not results.get('success'):
        st.error(f"❌ Error: {results.get('error', 'Unknown error occurred')}")
        return
    
    similarity = results['similarity_scores']
    overall_score = similarity['overall_percentage']
    match_level = similarity['match_level']
    
    # Header with overall score
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    
    # Main score display
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        score_color = get_match_color(overall_score)
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {score_color}22 0%, {score_color}44 100%); border-radius: 15px; border: 3px solid {score_color};">
                <h1 style="color: {score_color}; font-size: 4rem; margin: 0;">{overall_score}%</h1>
                <h3 style="color: {score_color}; margin: 0.5rem 0;">{match_level}</h3>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Detailed scores
    st.markdown("### 📋 Detailed Score Breakdown")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎯 Text Similarity",
            value=f"{similarity['detailed_scores']['text_similarity']:.1%}",
            help="Semantic similarity between resume and job description"
        )
    
    with col2:
        st.metric(
            label="🔧 Skills Match",
            value=f"{similarity['detailed_scores']['skills_match_rate']:.1%}",
            help="Percentage of required technical skills found"
        )
    
    with col3:
        st.metric(
            label="🔑 Keywords Match",
            value=f"{similarity['detailed_scores']['tfidf_match_rate']:.1%}",
            help="Important keywords overlap"
        )
    
    with col4:
        st.metric(
            label="📊 Overall Match",
            value=f"{similarity['detailed_scores']['all_keywords_match_rate']:.1%}",
            help="General keyword coverage"
        )
    
    st.markdown("---")
    
    # Two columns for matched and missing skills
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Matched Skills")
        matched_skills = similarity['matched_skills']
        if matched_skills:
            st.success(f"**{len(matched_skills)} skills found**")
            for skill in matched_skills:
                st.markdown(f"- ✓ **{skill}**")
        else:
            st.info("No technical skills matched")
    
    with col2:
        st.markdown("### ❌ Missing Skills")
        missing_skills = similarity['missing_skills']
        if missing_skills:
            st.warning(f"**{len(missing_skills)} skills missing**")
            for skill in missing_skills:
                st.markdown(f"- ✗ {skill}")
        else:
            st.success("All required skills present!")
    
    st.markdown("---")
    
    # Recommendations
    st.markdown("### 💡 Recommendations")
    recommendations = results['recommendations']
    
    if recommendations:
        for rec in recommendations:
            if "✅" in rec or "Strong match" in rec:
                st.success(rec)
            elif "⚠️" in rec or "Consider" in rec:
                st.warning(rec)
            else:
                st.info(rec)
    else:
        st.info("No specific recommendations at this time.")
    
    # Expandable sections for detailed information
    with st.expander("📄 Resume Analysis Details"):
        resume_analysis = results['resume_analysis']
        st.write(f"**Text Length:** {resume_analysis['text_length']} characters")
        st.write(f"**Total Keywords Found:** {len(resume_analysis['keywords'].get('all_keywords', []))}")
        st.write(f"**Technical Skills Detected:** {len(resume_analysis['technical_skills'])}")
        
        if resume_analysis['technical_skills']:
            st.write("**Skills:**", ", ".join(resume_analysis['technical_skills']))
    
    with st.expander("📋 Job Description Analysis Details"):
        job_analysis = results['job_analysis']
        st.write(f"**Text Length:** {job_analysis['text_length']} characters")
        st.write(f"**Total Keywords Found:** {len(job_analysis['keywords'].get('all_keywords', []))}")
        st.write(f"**Technical Skills Required:** {len(job_analysis['technical_skills'])}")
        
        if job_analysis['technical_skills']:
            st.write("**Required Skills:**", ", ".join(job_analysis['technical_skills']))
    
    # Download results
    st.markdown("---")
    st.markdown("### 💾 Download Results")
    
    json_results = json.dumps(results, indent=2)
    st.download_button(
        label="📥 Download Full Analysis (JSON)",
        data=json_results,
        file_name="ats_analysis_results.json",
        mime="application/json"
    )


def main():
    """Main application"""
    
    # Header
    st.markdown('<h1 class="main-header">📄 ATS Resume Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload your resume and job description to get an instant match analysis</p>', unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        use_spacy = st.checkbox(
            "Use Advanced NLP (spaCy)",
            value=True,
            help="Enable spaCy for more accurate keyword extraction. Disable for faster processing."
        )
        
        st.markdown("---")
        st.markdown("## ℹ️ About")
        st.info("""
        This tool analyzes how well your resume matches a job description using:
        
        - **Text Similarity**: Semantic analysis
        - **Skills Match**: Technical skills detection
        - **Keywords Match**: Important terms overlap
        
        **Score Ranges:**
        - 75%+: Excellent Match
        - 60-74%: Good Match
        - 45-59%: Moderate Match
        - 30-44%: Low Match
        - <30%: Poor Match
        """)
        
        st.markdown("---")
        st.markdown("### 📚 How to Use")
        st.markdown("""
        1. Upload your resume (PDF)
        2. Upload or paste job description
        3. Click 'Analyze'
        4. Review your match score
        5. Check recommendations
        """)
    
    # Main content area
    st.markdown("## 📤 Upload Files")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Resume (PDF)")
        resume_file = st.file_uploader(
            "Upload your resume in PDF format",
            type=['pdf'],
            help="Select a PDF file containing your resume"
        )
        
        if resume_file:
            st.success(f"✓ Uploaded: {resume_file.name}")
    
    with col2:
        st.markdown("### 📋 Job Description")
        
        # Option to upload file or paste text
        input_method = st.radio(
            "Choose input method:",
            ["Upload TXT file", "Paste text"],
            horizontal=True
        )
        
        job_description = None
        
        if input_method == "Upload TXT file":
            job_file = st.file_uploader(
                "Upload job description as TXT file",
                type=['txt'],
                help="Select a text file containing the job description"
            )
            
            if job_file:
                job_description = job_file.read().decode('utf-8')
                st.success(f"✓ Uploaded: {job_file.name}")
                with st.expander("Preview job description"):
                    st.text(job_description[:500] + "..." if len(job_description) > 500 else job_description)
        else:
            job_description = st.text_area(
                "Paste the job description here:",
                height=250,
                placeholder="Paste the complete job description including requirements, responsibilities, and qualifications..."
            )
            
            if job_description:
                st.success(f"✓ Job description entered ({len(job_description)} characters)")
    
    st.markdown("---")
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🚀 Analyze Resume", use_container_width=True, type="primary")
    
    # Analysis
    if analyze_button:
        if not resume_file:
            st.error("❌ Please upload a resume PDF file")
        elif not job_description:
            st.error("❌ Please provide a job description")
        else:
            # Show progress
            with st.spinner("🔍 Analyzing your resume..."):
                try:
                    # Save uploaded PDF to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(resume_file.read())
                        tmp_pdf_path = tmp_file.name
                    
                    # Initialize pipeline
                    pipeline = ATSPipeline(use_spacy=use_spacy)
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("📄 Extracting text from PDF...")
                    progress_bar.progress(20)
                    time.sleep(0.3)
                    
                    status_text.text("🔑 Extracting keywords...")
                    progress_bar.progress(50)
                    
                    # Run analysis
                    results = pipeline.analyze(
                        resume_pdf_path=tmp_pdf_path,
                        job_description=job_description,
                        verbose=False
                    )
                    
                    status_text.text("📊 Calculating similarity scores...")
                    progress_bar.progress(80)
                    time.sleep(0.3)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    time.sleep(0.5)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display results
                    display_results(results)
                    
                    # Clean up temporary file
                    os.unlink(tmp_pdf_path)
                    
                except Exception as e:
                    st.error(f"❌ An error occurred during analysis: {str(e)}")
                    st.exception(e)


if __name__ == "__main__":
    main()
