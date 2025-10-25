# 💼 AI-Powered Hiring Platform

## Overview

A **two-sided hiring platform** that automatically matches candidates with job postings using AI-powered resume analysis.

## 🎯 How It Works

### For Job Seekers (Applicants):
1. **Register** with name and email
2. **Upload resume** (PDF format)
3. **Browse jobs** and see all openings
4. **Apply to multiple jobs** at once
5. **Get instant match scores** for each application
6. **Track applications** and their status

### For Employers (Hiring Managers):
1. **Register** company account
2. **Post job openings** with requirements
3. **Set minimum score threshold** (e.g., only see candidates >65% match)
4. **Receive applications automatically**
5. **View ranked candidates** sorted by match score
6. **See only qualified candidates** above your threshold
7. **Shortlist/reject** with one click

## 🚀 Key Features

### Automated Matching Engine
- **ATS Analysis**: Text similarity, keyword matching, format analysis
- **RAG Skills Extraction**: Semantic matching with 3.2M skills database
- **LLM Analysis** (optional): Structured information extraction
- **Comprehensive Scoring**: Overall match, skills match, ATS compatibility

### Smart Filtering
- **Threshold-based**: Only show candidates above minimum score
- **Automatic Ranking**: Best candidates at the top
- **No manual screening**: System does the initial filtering

### Database-Backed
- **SQLite database**: All data persisted
- **User accounts**: Applicants and employers
- **Job postings**: Active, closed, draft states
- **Applications tracking**: Status updates, notes, timestamps

## 📁 Files Created

### Core Platform:
1. **`hiring_platform_db.py`** - Database management (SQLite)
2. **`matching_engine.py`** - Automated candidate matching and ranking
3. **`hiring_platform_app.py`** - Streamlit web interface

### Database Schema:
- **`users`** - Job seekers (email, resume, skills)
- **`employers`** - Companies (email, company name)
- **`jobs`** - Job postings (title, description, requirements, minimum_score)
- **`applications`** - Applications (job_id, user_id, scores, status)

## 🎯 Current Status

✅ **Database initialized** with sample data:
- 1 employer account (TechCorp Inc.)
- 1 job posting (Senior Data Scientist)
- 1 user account (John Doe)

✅ **Platform running** at: http://localhost:8501

## 💡 Usage Examples

### Example 1: Applicant Applies to Job
```python
from matching_engine import HiringMatchingEngine

engine = HiringMatchingEngine(use_rag=True, use_llm=False)

# User 1 applies to Job 1 with their resume
result = engine.process_application(
    user_id=1,
    job_id=1,
    resume_pdf_path="resume.pdf"
)

print(f"Match Score: {result['match_score']}%")
print(f"Meets Threshold: {result['meets_threshold']}")
```

### Example 2: Employer Views Top Candidates
```python
# Get top 10 candidates for job
top_candidates = engine.get_top_candidates(job_id=1, top_n=10)

for i, candidate in enumerate(top_candidates, 1):
    print(f"#{i}: {candidate['name']} - {candidate['match_score']:.1f}%")
```

### Example 3: Batch Application
```python
# Apply to multiple jobs at once
results = engine.batch_apply(
    user_id=1,
    job_ids=[1, 2, 3, 4, 5],
    resume_pdf_path="resume.pdf"
)

print(f"Applied to {results['successful_applications']} jobs")
```

## 🔧 Configuration

### Job Posting Settings:
- **minimum_score**: Threshold percentage (default: 50%)
- Only candidates above this score will be shown to employer
- Prevents wasting time on unqualified candidates

### Matching Engine Settings:
```python
engine = HiringMatchingEngine(
    use_rag=True,   # Use RAG for comprehensive skills (slower but better)
    use_llm=False   # Use LLM for structured data (slower, costs API calls)
)
```

**Recommendation**: Use `use_rag=True, use_llm=False` for best balance of speed and accuracy.

## 📊 Scoring Algorithm

### Overall Match Score = Weighted Average of:
1. **Skills Match (60%)** - Most important
2. **All Keywords Match (30%)**
3. **Text Similarity (10%)** - Least important

### Additional Scores:
- **ATS Score** (0-100): Resume format quality
- **Skills Match Score**: Technical skills alignment

### Match Levels:
- **80%+**: Excellent Match 🟢
- **65-79%**: Good Match 🟡
- **50-64%**: Moderate Match 🟠
- **35-49%**: Low Match 🔴
- **<35%**: Poor Match ⚫

## 🎨 Web Interface Features

### Job Seeker Portal:
- ✅ Browse all active jobs
- ✅ Upload resume and apply to multiple jobs
- ✅ See match scores for each application
- ✅ Track application status
- ✅ View profile and extracted skills

### Employer Portal:
- ✅ Post new job openings
- ✅ View all job postings
- ✅ Dashboard with statistics
- ✅ View ranked candidates filtered by score
- ✅ Shortlist/reject candidates
- ✅ Add notes to applications

## 🚀 Next Steps to Enhance

### Phase 1: Quick Wins
1. **Email notifications** when status changes
2. **Resume download** for employers
3. **Search and filters** (location, salary, skills)
4. **Application deadlines**

### Phase 2: Advanced Features
5. **Interview scheduling** integration
6. **Candidate messaging** system
7. **Analytics dashboard** (application trends, time-to-hire)
8. **Resume suggestions** for applicants

### Phase 3: Scale
9. **User authentication** (proper login system)
10. **Payment integration** (job posting fees)
11. **Multi-language support**
12. **Mobile app**

## 📞 API Usage (Programmatic Access)

```python
from hiring_platform_db import HiringPlatformDB
from matching_engine import HiringMatchingEngine

# Initialize
db = HiringPlatformDB()
engine = HiringMatchingEngine()

# Create employer
employer_id = db.create_employer("hr@company.com", "My Company")

# Post job
job_id = db.create_job(
    employer_id=employer_id,
    title="Software Engineer",
    description="Looking for a talented developer...",
    requirements="Python, SQL, 3+ years experience",
    minimum_score=60.0
)

# Create applicant
user_id = db.create_user("john@email.com", "John Doe")

# Process application
result = engine.process_application(user_id, job_id, "resume.pdf")

# Get ranked candidates
candidates = engine.get_ranked_candidates(job_id, min_score=60)

# Update application status
db.update_application_status(application_id, 'shortlisted', 'Great candidate!')
```

## 🎯 Benefits Over Traditional ATS

### For Applicants:
- ✅ **Instant feedback** on match quality
- ✅ **Apply to multiple jobs** quickly
- ✅ **Know your chances** before applying
- ✅ **Track all applications** in one place

### For Employers:
- ✅ **Auto-filtering** - No manual resume screening
- ✅ **Ranked candidates** - Best first
- ✅ **Time savings** - Only review qualified candidates
- ✅ **Data-driven** - Objective scoring
- ✅ **Scalable** - Handle hundreds of applications

## 🔒 Data Privacy

- All data stored locally in SQLite database
- No external data sharing
- Can be easily deployed on your own server
- Full control over candidate information

## 📈 Performance

- **Processing time**: ~10-30 seconds per application (with RAG)
- **Database**: Handles thousands of jobs and applications
- **Scalable**: Can process batch applications
- **Caching**: Embeddings cached for faster subsequent analyses

---

## 🎉 You're All Set!

Your hiring platform is ready to use. Access it at:
**http://localhost:8501**

Choose your role (Job Seeker or Employer) and start matching!
