# ATS Resume Analyzer

A comprehensive pipeline for analyzing resume-job description similarity using NLP techniques and keyword extraction.

## Features

- 📄 **PDF Text Extraction**: Extract text from PDF resumes
- 🔑 **Keyword Extraction**: Extract keywords using TF-IDF and spaCy NLP
- 🎯 **Technical Skills Detection**: Identify programming languages, frameworks, and tools
- 📊 **Similarity Scoring**: Multiple similarity metrics (Jaccard, Cosine, Weighted)
- 💡 **Smart Recommendations**: Get actionable advice to improve resume match
- 📈 **Detailed Analysis**: Comprehensive reporting with matched/missing skills

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Download the spaCy English language model:
```bash
python -m spacy download en_core_web_sm
```

## Quick Start

### 🌐 Web Interface (Recommended)

Launch the interactive web interface:

```bash
streamlit run app.py
```

Then open your browser and:
1. Upload your resume (PDF)
2. Upload job description (TXT) or paste it
3. Click "Analyze Resume"
4. View your match score and recommendations!

### 💻 Command Line Usage

```bash
python ats_pipeline.py "resume.pdf" "job_description.txt"
```

**Note:** In PowerShell, use quotes around paths with special characters:
```powershell
python ats_pipeline.py "path\with&special\chars.pdf" "job_description.txt"
```

### 🐍 Python API Usage

```python
from ats_pipeline import ATSPipeline

# Initialize pipeline
pipeline = ATSPipeline(use_spacy=True)

# Define job description
job_description = """
Senior Python Developer
Requirements:
- 5+ years Python experience
- Django or Flask
- AWS/Azure
- Docker, Kubernetes
...
"""

# Analyze resume
results = pipeline.analyze(
    resume_pdf_path="resume.pdf",
    job_description=job_description,
    verbose=True
)

# Save results
if results['success']:
    pipeline.save_results(results, 'results.json')
```

## Project Structure

```
ATS-agent/
├── app.py                    # 🌐 Web interface (Streamlit)
├── ats_pipeline.py           # Main pipeline orchestrator
├── pdf_extractor.py          # PDF text extraction module
├── keyword_extractor.py      # Keyword extraction using NLP
├── similarity_calculator.py  # Similarity scoring algorithms
├── example.py                # Usage examples
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Components

### 1. PDF Extractor (`pdf_extractor.py`)
Extracts text content from PDF resumes using PyPDF2.

### 2. Keyword Extractor (`keyword_extractor.py`)
- **TF-IDF**: Identifies important terms using statistical analysis
- **spaCy NLP**: Extracts nouns, entities, and key phrases
- **Technical Skills**: Detects programming languages, frameworks, databases, cloud platforms, etc.

### 3. Similarity Calculator (`similarity_calculator.py`)
- **Jaccard Similarity**: Measures keyword overlap
- **Cosine Similarity**: Compares text semantic similarity
- **Weighted Score**: Combines multiple metrics with intelligent weighting
  - Technical Skills: 40%
  - TF-IDF Keywords: 30%
  - Overall Text Similarity: 20%
  - All Keywords: 10%

### 4. ATS Pipeline (`ats_pipeline.py`)
Main orchestrator that combines all components and provides:
- End-to-end analysis workflow
- Detailed scoring breakdown
- Match level classification
- Actionable recommendations

## Output Format

```json
{
  "success": true,
  "resume_analysis": {
    "text_length": 2500,
    "keywords": [...],
    "technical_skills": ["python", "django", "aws", ...]
  },
  "job_analysis": {
    "text_length": 800,
    "keywords": [...],
    "technical_skills": ["python", "flask", "docker", ...]
  },
  "similarity_scores": {
    "overall_score": 0.72,
    "overall_percentage": 72.0,
    "match_level": "Good Match",
    "matched_skills": ["python", "django", ...],
    "missing_skills": ["kubernetes", ...],
    "skills_coverage": 75.0
  },
  "recommendations": [...]
}
```

## Match Levels

- **Excellent Match** (75%+): Strong alignment with job requirements
- **Good Match** (60-74%): Above average fit
- **Moderate Match** (45-59%): Reasonable fit with some gaps
- **Low Match** (30-44%): Significant improvements needed
- **Poor Match** (<30%): Major misalignment

## Examples

Check `example.py` for detailed usage examples:

1. **PDF Resume Analysis**: Full pipeline with PDF input
2. **Programmatic Access**: Access specific results programmatically
3. **Text Resume Analysis**: Use with plain text instead of PDF

Run examples:
```bash
python example.py
```

## Use Cases

- 📝 **Job Seekers**: Optimize your resume for specific job descriptions
- 🏢 **Recruiters**: Quickly screen candidates against job requirements
- 💼 **Career Coaches**: Help clients improve their resumes
- 🤖 **ATS Systems**: Build automated candidate screening tools

## Requirements

- Python 3.8+
- PyPDF2: PDF text extraction
- spaCy: Advanced NLP processing
- scikit-learn: TF-IDF and similarity calculations
- numpy: Numerical computations

## Customization

### Adjust Scoring Weights

Edit `similarity_calculator.py` to change the weighted scoring formula:

```python
weighted_score = (
    skills_overlap['match_rate'] * 0.40 +  # Technical skills weight
    tfidf_overlap['match_rate'] * 0.30 +   # Keywords weight
    text_similarity * 0.20 +                # Text similarity weight
    all_kw_overlap['match_rate'] * 0.10    # All keywords weight
)
```

### Add More Technical Skills

Edit the `skills_database` set in `keyword_extractor.py` to add more skills to detect.

### Disable spaCy

For faster processing without advanced NLP:

```python
pipeline = ATSPipeline(use_spacy=False)
```

## Limitations

- PDF extraction quality depends on PDF format/quality
- Technical skills database is predefined (can be extended)
- Works best with English text
- Requires clear, well-structured resumes and job descriptions

## Future Enhancements

- [ ] Support for Word documents (.docx)
- [ ] Multi-language support
- [ ] Web interface
- [ ] Resume optimization suggestions
- [ ] Batch processing for multiple resumes
- [ ] Integration with job boards APIs
- [ ] Machine learning-based scoring


## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Support

For questions or issues, please open an issue in the repository.

---

**Happy Job Hunting! 🚀**
