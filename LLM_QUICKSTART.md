# LLM Resume Extraction - Quick Start

## 🎯 What You Have Now

I've added **LLM-based resume extraction** that intelligently categorizes and extracts:

✅ **Technical Skills** (with years of experience & proficiency)  
✅ **Soft Skills** (with context)  
✅ **Total Years of Experience**  
✅ **Certifications** (with issuers and dates)  
✅ **Education** (degrees, institutions, fields)  
✅ **Job Titles** (all positions)  
✅ **Industries** (sectors worked in)  

## 📁 New Files

1. **`llm_extractor.py`** - Main LLM extraction class (supports OpenAI, Gemini, Anthropic)
2. **`example_llm_extraction.py`** - Example using your resume
3. **`LLM_EXTRACTION.md`** - Complete documentation
4. **Updated `requirements.txt`** - Added optional LLM dependencies

## 🆚 RAG vs LLM: When to Use Each

| Feature | RAG | LLM |
|---------|-----|-----|
| **Skills Detection** | ✅ Comprehensive (1,741 skills) | ✅ Categorized (technical/soft) |
| **Categorization** | ❌ No auto-categorization | ✅ Auto-categorizes |
| **Years of Experience** | ❌ Not detected | ✅ Per skill & total |
| **Proficiency Level** | ❌ Not detected | ✅ Beginner/Intermediate/Expert |
| **Certifications** | ❌ Not structured | ✅ Structured with details |
| **Context Understanding** | ⚠️ Limited | ✅ Excellent |
| **Speed** | ✅ Fast (<1 sec) | ⚠️ Slower (2-5 sec) |
| **Cost** | ✅ Free | ⚠️ API costs (~$0.001-0.03/resume) |
| **Offline** | ✅ Yes | ❌ Needs internet |

## 🚀 Quick Start

### Step 1: Get API Key

**OpenAI (Recommended):**
- Go to: https://platform.openai.com/api-keys
- Create API key
- Cost: ~$0.001 per resume with gpt-3.5-turbo

**Google Gemini (Free Tier):**
- Go to: https://makersuite.google.com/app/apikey
- Get free API key
- Cost: FREE for first ~1000/day

### Step 2: Install Package

```bash
# For OpenAI
pip install openai

# For Google Gemini (free)
pip install google-generativeai

# For Anthropic Claude
pip install anthropic
```

### Step 3: Set API Key

**Windows PowerShell:**
```powershell
# OpenAI
$env:OPENAI_API_KEY='sk-your-key-here'

# Google Gemini (free!)
$env:GOOGLE_API_KEY='your-key-here'

# Anthropic
$env:ANTHROPIC_API_KEY='your-key-here'
```

### Step 4: Run!

**Quick test:**
```bash
python example_llm_extraction.py
```

**Command line:**
```bash
# With OpenAI
python llm_extractor.py resume&job_description\11890896.pdf

# With Google Gemini (free)
python llm_extractor.py resume&job_description\11890896.pdf --provider gemini

# With GPT-4 (more accurate)
python llm_extractor.py resume&job_description\11890896.pdf --model gpt-4
```

## 💡 Example Output

```json
{
  "technical_skills": [
    {
      "skill": "Python",
      "years_experience": 5,
      "proficiency": "expert"
    },
    {
      "skill": "Data Analysis",
      "years_experience": 8,
      "proficiency": "expert"
    }
  ],
  "soft_skills": [
    {
      "skill": "Leadership",
      "context": "Led cross-functional teams"
    }
  ],
  "total_experience_years": 8,
  "certifications": [
    {
      "name": "Certified Analytics Professional",
      "issuer": "INFORMS",
      "year": 2020
    }
  ]
}
```

## 🔧 Python Usage

### Basic Example

```python
from llm_extractor import LLMResumeExtractor

# Initialize (using OpenAI)
extractor = LLMResumeExtractor(
    provider="openai",
    model="gpt-3.5-turbo"  # Fast & cheap
)

# Extract from PDF
results = extractor.extract_from_pdf("resume.pdf")

# Print summary
extractor.print_summary(results)

# Access specific data
print(f"Total Experience: {results['total_experience_years']} years")
print(f"Technical Skills: {len(results['technical_skills'])}")
print(f"Certifications: {len(results['certifications'])}")

# Save to JSON
extractor.save_results(results, "resume_analysis.json")
```

### Get Skills with 5+ Years Experience

```python
experienced_skills = [
    skill for skill in results['technical_skills']
    if skill.get('years_experience', 0) >= 5
]

for skill in experienced_skills:
    print(f"{skill['skill']}: {skill['years_experience']} years")
```

### Use Google Gemini (Free!)

```python
extractor = LLMResumeExtractor(
    provider="gemini",
    model="gemini-pro"
)

results = extractor.extract_from_pdf("resume.pdf")
```

## 🎨 Hybrid Approach (Best Results)

Combine RAG and LLM for maximum accuracy:

```python
from llm_extractor import LLMResumeExtractor
from rag_skills_extractor import RAGSkillsExtractor
from pdf_extractor import PDFExtractor

# Extract text
pdf_ext = PDFExtractor()
resume_text = pdf_ext.extract_text("resume.pdf")

# Method 1: LLM for structured data
llm_ext = LLMResumeExtractor(provider="openai")
llm_results = llm_ext.extract_from_text(resume_text)

# Method 2: RAG for comprehensive skills
rag_ext = RAGSkillsExtractor(max_skills=10000)
rag_skills = rag_ext.extract_skills_rag(resume_text, threshold=0.65)

# Combine results
print(f"LLM detected: {len(llm_results['technical_skills'])} technical skills")
print(f"RAG detected: {len(rag_skills)} total skills")
print(f"Total experience: {llm_results['total_experience_years']} years")
print(f"Certifications: {len(llm_results['certifications'])}")
```

## 💰 Cost Comparison

| Provider | Model | Cost/Resume | Free Tier | Speed |
|----------|-------|-------------|-----------|-------|
| **OpenAI** | gpt-3.5-turbo | ~$0.001 | ❌ No | ⚡ Fast |
| **OpenAI** | gpt-4 | ~$0.030 | ❌ No | ⚡ Fast |
| **Google** | gemini-pro | FREE | ✅ Yes | ⚡⚡ Very Fast |
| **Anthropic** | claude-3-sonnet | ~$0.003 | ❌ No | ⚡ Fast |

**Recommendation:**
- **Development/Testing**: Use Google Gemini (FREE)
- **Production**: Use OpenAI gpt-3.5-turbo (very cheap, very fast)
- **Best Accuracy**: Use OpenAI gpt-4 (more expensive but most accurate)

## 🎯 Use Cases

### 1. Skill Gap Analysis
```python
# Extract from resume
resume_results = extractor.extract_from_pdf("resume.pdf")

# Extract from job description
job_results = extractor.extract_from_text(job_description)

# Compare
resume_skills = {s['skill'] for s in resume_results['technical_skills']}
job_skills = {s['skill'] for s in job_results['technical_skills']}

missing_skills = job_skills - resume_skills
print(f"Missing skills: {missing_skills}")
```

### 2. Resume Ranking
```python
resumes = ["resume1.pdf", "resume2.pdf", "resume3.pdf"]
ranked = []

for resume in resumes:
    results = extractor.extract_from_pdf(resume)
    ranked.append({
        'file': resume,
        'experience': results['total_experience_years'],
        'skills': len(results['technical_skills']),
        'certs': len(results['certifications'])
    })

# Sort by experience
ranked.sort(key=lambda x: x['experience'], reverse=True)
```

### 3. Certification Tracking
```python
results = extractor.extract_from_pdf("resume.pdf")

for cert in results['certifications']:
    print(f"• {cert['name']}")
    print(f"  Issuer: {cert['issuer']}")
    print(f"  Year: {cert['year']}")
```

## 📊 What You Get

### Technical Skills (Structured)
- Skill name
- Years of experience
- Proficiency level (beginner/intermediate/expert)

### Soft Skills (Contextualized)
- Skill name
- Context where it was demonstrated

### Experience
- Total years of professional experience
- Years per technical skill (if mentioned)

### Certifications
- Certificate name
- Issuing organization
- Year obtained

### Education
- Degree type
- Institution
- Graduation year
- Field of study

## 🔍 Comparison with Traditional Methods

| Method | Skills Found | Categorized | Experience | Certifications |
|--------|--------------|-------------|------------|----------------|
| **Traditional Keyword** | 18 | ❌ | ❌ | ❌ |
| **RAG Embeddings** | 1,741 | ❌ | ❌ | ❌ |
| **LLM Extraction** | ~50-100 | ✅ | ✅ | ✅ |

**Best Approach:** Use RAG for comprehensive coverage, LLM for structure!

## ⚙️ Configuration

### Choose Your Provider

```python
# OpenAI - Most reliable
extractor = LLMResumeExtractor(
    provider="openai",
    model="gpt-3.5-turbo"  # or "gpt-4"
)

# Google Gemini - Free tier
extractor = LLMResumeExtractor(
    provider="gemini",
    model="gemini-pro"
)

# Anthropic - Privacy focused
extractor = LLMResumeExtractor(
    provider="anthropic",
    model="claude-3-sonnet-20240229"
)
```

### Pass API Key Directly

```python
extractor = LLMResumeExtractor(
    provider="openai",
    model="gpt-3.5-turbo",
    api_key="sk-your-key-here"
)
```

## 🛠️ Troubleshooting

### "API key not found"
```powershell
# Set environment variable
$env:OPENAI_API_KEY='your-key'
```

### "Rate limit exceeded"
Add delays between requests:
```python
import time
time.sleep(1)  # Wait 1 second
```

### "JSON parsing error"
Use GPT-4 for better reliability:
```python
extractor = LLMResumeExtractor(provider="openai", model="gpt-4")
```

### Too expensive?
Use Google Gemini (FREE):
```python
extractor = LLMResumeExtractor(provider="gemini")
```

## 📚 Documentation

- **`LLM_EXTRACTION.md`** - Complete documentation
- **`example_llm_extraction.py`** - Working example
- **`llm_extractor.py`** - Source code

## 🎉 Summary

**You now have 3 extraction methods:**

1. **Traditional** - Fast, basic (18 skills)
2. **RAG** - Comprehensive, semantic (1,741 skills)
3. **LLM** - Structured, intelligent (50-100 categorized skills + experience + certs)

**Recommended:** Use **RAG + LLM** together for best results!

---

**Ready to test?** Run: `python example_llm_extraction.py`

(Make sure to set your API key first!)
