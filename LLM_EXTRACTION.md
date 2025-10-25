# LLM-Based Resume Information Extraction

Extract structured information from resumes using Large Language Models (LLMs) including technical skills, soft skills, years of experience, and certifications.

## Overview

The LLM extractor uses AI to intelligently parse resumes and extract:
- ✅ **Technical Skills** (with proficiency levels and years of experience)
- ✅ **Soft Skills** (with context where mentioned)
- ✅ **Total Years of Experience**
- ✅ **Certifications** (with issuers and dates)
- ✅ **Education** (degrees, institutions, years)
- ✅ **Job Titles** (all positions held)
- ✅ **Industries** (sectors worked in)

## Supported LLM Providers

| Provider | Model Examples | API Key Env Variable | Cost |
|----------|---------------|---------------------|------|
| **OpenAI** | gpt-3.5-turbo, gpt-4 | `OPENAI_API_KEY` | ~$0.001-0.03/resume |
| **Google Gemini** | gemini-pro | `GOOGLE_API_KEY` | Free tier available |
| **Anthropic** | claude-3-sonnet | `ANTHROPIC_API_KEY` | ~$0.003-0.015/resume |

## Installation

```bash
# Install required package for your provider
pip install openai              # For OpenAI
pip install google-generativeai # For Google Gemini
pip install anthropic           # For Anthropic Claude
```

## Quick Start

### 1. Set Your API Key

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY='your-api-key-here'
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**For other providers:**
```powershell
# Google Gemini
$env:GOOGLE_API_KEY='your-api-key-here'

# Anthropic Claude
$env:ANTHROPIC_API_KEY='your-api-key-here'
```

### 2. Basic Usage

```python
from llm_extractor import LLMResumeExtractor

# Initialize with OpenAI
extractor = LLMResumeExtractor(
    provider="openai",
    model="gpt-3.5-turbo"
)

# Extract from PDF
results = extractor.extract_from_pdf("resume.pdf")

# Print summary
extractor.print_summary(results)

# Save to JSON
extractor.save_results(results, "resume_analysis.json")
```

### 3. Command Line Usage

```bash
# With OpenAI (default)
python llm_extractor.py resume.pdf

# With specific model
python llm_extractor.py resume.pdf --model gpt-4

# With Google Gemini
python llm_extractor.py resume.pdf --provider gemini

# With Anthropic Claude
python llm_extractor.py resume.pdf --provider anthropic --model claude-3-sonnet-20240229

# Custom output file
python llm_extractor.py resume.pdf --output my_results.json
```

### 4. Run Example with Your Resume

```bash
python example_llm_extraction.py
```

## Output Structure

The extractor returns a JSON object with this structure:

```json
{
  "technical_skills": [
    {
      "skill": "Python",
      "years_experience": 5,
      "proficiency": "expert"
    },
    {
      "skill": "React",
      "years_experience": 3,
      "proficiency": "intermediate"
    }
  ],
  "soft_skills": [
    {
      "skill": "Leadership",
      "context": "Led cross-functional teams"
    },
    {
      "skill": "Communication",
      "context": "Presented to stakeholders"
    }
  ],
  "total_experience_years": 8,
  "certifications": [
    {
      "name": "AWS Certified Solutions Architect",
      "issuer": "Amazon Web Services",
      "year": 2023
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Science",
      "institution": "MIT",
      "year": 2015,
      "field": "Computer Science"
    }
  ],
  "job_titles": [
    "Senior Software Engineer",
    "Full Stack Developer"
  ],
  "industries": [
    "Technology",
    "FinTech"
  ],
  "summary": "Experienced software engineer with 8+ years...",
  "_metadata": {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "resume_length": 5234
  }
}
```

## Provider Comparison

### OpenAI (Recommended for most use cases)

**Pros:**
- ✅ Most accurate extraction
- ✅ Best JSON formatting
- ✅ Fast response times
- ✅ Well-documented API

**Cons:**
- ❌ Requires paid API key (but very affordable)
- ❌ Data sent to external service

**Models:**
- `gpt-3.5-turbo`: Fast, affordable (~$0.001/resume)
- `gpt-4`: More accurate (~$0.03/resume)
- `gpt-4-turbo`: Best balance

**Usage:**
```python
extractor = LLMResumeExtractor(
    provider="openai",
    model="gpt-3.5-turbo"  # or "gpt-4"
)
```

### Google Gemini (Best for free usage)

**Pros:**
- ✅ Free tier available
- ✅ Fast responses
- ✅ Good accuracy

**Cons:**
- ❌ Occasional JSON formatting issues
- ❌ Less consistent than GPT-4

**Models:**
- `gemini-pro`: General purpose (free tier)

**Usage:**
```python
extractor = LLMResumeExtractor(
    provider="gemini",
    model="gemini-pro"
)
```

### Anthropic Claude (Best for privacy-focused)

**Pros:**
- ✅ Strong reasoning capabilities
- ✅ Good at following instructions
- ✅ Privacy-focused company

**Cons:**
- ❌ More expensive than OpenAI
- ❌ Slightly slower responses

**Models:**
- `claude-3-sonnet-20240229`: Balanced
- `claude-3-opus-20240229`: Most capable

**Usage:**
```python
extractor = LLMResumeExtractor(
    provider="anthropic",
    model="claude-3-sonnet-20240229"
)
```

## Advanced Usage

### Extract with Custom Prompting

```python
# Access the raw text extraction first
from pdf_extractor import PDFExtractor

pdf_ext = PDFExtractor()
resume_text = pdf_ext.extract_text("resume.pdf")

# Use LLM extractor
extractor = LLMResumeExtractor(provider="openai")
results = extractor.extract_from_text(resume_text)
```

### Filter Skills by Experience

```python
results = extractor.extract_from_pdf("resume.pdf")

# Get skills with 5+ years experience
experienced_skills = [
    skill for skill in results['technical_skills']
    if skill.get('years_experience', 0) >= 5
]

print("Skills with 5+ years:")
for skill in experienced_skills:
    print(f"  • {skill['skill']}: {skill['years_experience']} years")
```

### Combine with RAG for Validation

```python
from llm_extractor import LLMResumeExtractor
from rag_skills_extractor import RAGSkillsExtractor

# Extract with LLM
llm_ext = LLMResumeExtractor(provider="openai")
llm_results = llm_ext.extract_from_pdf("resume.pdf")

# Validate with RAG
rag_ext = RAGSkillsExtractor(max_skills=10000)
rag_skills = rag_ext.extract_skills_rag(resume_text, threshold=0.65)

# Find skills detected by both methods
llm_skills = [s['skill'] for s in llm_results['technical_skills']]
validated_skills = set(llm_skills) & set(rag_skills)

print(f"Skills validated by both methods: {len(validated_skills)}")
```

### Compare Multiple Resumes

```python
import json

extractor = LLMResumeExtractor(provider="openai")

resumes = ["resume1.pdf", "resume2.pdf", "resume3.pdf"]
all_results = []

for resume_path in resumes:
    results = extractor.extract_from_pdf(resume_path)
    all_results.append({
        'file': resume_path,
        'experience_years': results['total_experience_years'],
        'tech_skills_count': len(results['technical_skills']),
        'certifications_count': len(results['certifications'])
    })

# Sort by experience
all_results.sort(key=lambda x: x['experience_years'], reverse=True)

for r in all_results:
    print(f"{r['file']}: {r['experience_years']} years, "
          f"{r['tech_skills_count']} skills, "
          f"{r['certifications_count']} certs")
```

## Cost Analysis

### OpenAI Pricing (as of 2024)

| Model | Input Cost | Output Cost | Avg Cost/Resume |
|-------|-----------|-------------|-----------------|
| gpt-3.5-turbo | $0.50/1M tokens | $1.50/1M tokens | ~$0.001 |
| gpt-4-turbo | $10/1M tokens | $30/1M tokens | ~$0.015 |
| gpt-4 | $30/1M tokens | $60/1M tokens | ~$0.030 |

**Example:** 
- Analyzing 100 resumes with gpt-3.5-turbo: ~$0.10
- Analyzing 100 resumes with gpt-4: ~$3.00

### Google Gemini Pricing

| Model | Free Tier | Paid Tier |
|-------|-----------|-----------|
| gemini-pro | 60 requests/min | Higher limits |

**Example:**
- First ~1000 resumes/day: FREE
- Beyond free tier: Very affordable

## Benefits vs RAG

| Feature | LLM Extraction | RAG Extraction |
|---------|---------------|----------------|
| **Categorization** | ✅ Auto-categorizes (technical/soft) | ❌ Requires manual categorization |
| **Experience Years** | ✅ Extracts years per skill | ❌ Not detected |
| **Proficiency Levels** | ✅ Detects (beginner/expert) | ❌ Not detected |
| **Certifications** | ✅ Structured extraction | ❌ Not detected |
| **Context Understanding** | ✅ Excellent | ⚠️ Limited |
| **Speed** | ⚠️ 2-5 seconds | ✅ <1 second |
| **Cost** | ⚠️ API costs | ✅ Free |
| **Offline** | ❌ Requires API | ✅ Works offline |
| **Accuracy** | ✅ Very high | ✅ High |

## Best Practice: Hybrid Approach

Combine both methods for best results:

```python
from llm_extractor import LLMResumeExtractor
from rag_skills_extractor import RAGSkillsExtractor
from pdf_extractor import PDFExtractor

# Extract text
pdf_ext = PDFExtractor()
resume_text = pdf_ext.extract_text("resume.pdf")

# Method 1: LLM - Structured extraction
llm_ext = LLMResumeExtractor(provider="openai", model="gpt-3.5-turbo")
llm_results = llm_ext.extract_from_text(resume_text)

# Method 2: RAG - Comprehensive skills list
rag_ext = RAGSkillsExtractor(max_skills=10000)
rag_skills = rag_ext.extract_skills_rag(resume_text, threshold=0.65)

# Combine: Use LLM for structure, RAG for completeness
combined_results = {
    **llm_results,
    'all_detected_skills_rag': rag_skills,
    'skills_count_comparison': {
        'llm_technical': len(llm_results['technical_skills']),
        'rag_total': len(rag_skills)
    }
}

print(f"LLM found: {len(llm_results['technical_skills'])} technical skills")
print(f"RAG found: {len(rag_skills)} total skills")
```

## Troubleshooting

### "API key not found"
Set environment variable:
```powershell
$env:OPENAI_API_KEY='sk-...'
```

### "Rate limit exceeded"
Add delay between requests:
```python
import time

for resume in resumes:
    results = extractor.extract_from_pdf(resume)
    time.sleep(1)  # Wait 1 second between requests
```

### "JSON parsing error"
LLM sometimes returns malformed JSON. The extractor handles most cases, but you can increase reliability by using GPT-4:
```python
extractor = LLMResumeExtractor(provider="openai", model="gpt-4")
```

### Too expensive
Use Google Gemini's free tier:
```python
extractor = LLMResumeExtractor(provider="gemini")
```

## Security Considerations

### Data Privacy
- OpenAI, Gemini, and Anthropic process data on their servers
- For sensitive resumes, consider:
  1. Using local models (future feature)
  2. Redacting PII before sending
  3. Checking provider's data retention policies

### API Key Security
- Never commit API keys to git
- Use environment variables
- Rotate keys periodically

## Future Enhancements

- [ ] Local model support (Ollama, Llama, etc.)
- [ ] Batch processing optimization
- [ ] Resume comparison features
- [ ] Job matching with extracted data
- [ ] Skills gap analysis
- [ ] Salary estimation based on skills/experience
- [ ] Web interface integration

## Examples

Check out these example scripts:
- `example_llm_extraction.py` - Basic usage with your resume
- `llm_extractor.py` - Command-line tool

## License

Part of ATS Resume Analyzer project.
