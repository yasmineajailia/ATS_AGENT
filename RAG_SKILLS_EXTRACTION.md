# RAG-Based Skills Extraction

This document explains how to use the RAG (Retrieval-Augmented Generation) approach for intelligent skills extraction from resumes and job descriptions.

## Overview

The RAG skills extractor uses semantic embeddings to match skills from a large dataset (3.2M+ skills) against resume and job description text. This provides:

- **More accurate matching**: Finds skills even with different phrasing
- **Semantic understanding**: Matches "Python programming" with "Python" 
- **Comprehensive coverage**: Uses real-world skills database
- **Flexible thresholds**: Adjust precision vs. recall

## Dataset

The system uses `data/skills_exploded (2).csv` which contains **3,254,965 unique skills** from real job postings.

## Installation

```bash
# Install required packages
pip install sentence-transformers pandas scikit-learn

# Or use requirements.txt (updated)
pip install -r requirements.txt
```

## Usage

### 1. Basic Skills Extraction

```python
from rag_skills_extractor import RAGSkillsExtractor

# Initialize (uses 50,000 skills by default for faster loading)
extractor = RAGSkillsExtractor(max_skills=50000)

# Extract skills from text
resume_text = "5 years experience in Python, React, and AWS..."
skills = extractor.extract_skills_rag(resume_text, threshold=0.65)

print(f"Found {len(skills)} skills:")
for skill in skills:
    print(f"  • {skill}")
```

### 2. Get Skills with Confidence Scores

```python
# Get skills with similarity scores
skills_with_scores = extractor.extract_skills_rag(
    resume_text, 
    threshold=0.65,
    return_scores=True
)

for skill, score in skills_with_scores:
    print(f"{skill}: {score:.3f}")
```

### 3. Compare Resume with Job Description

```python
job_description = "Looking for Full Stack Developer with React, Node.js, MongoDB..."

comparison = extractor.compare_skills(resume_text, job_description, threshold=0.65)

print(f"Matched: {len(comparison['matched_skills'])} skills")
print(f"Missing: {len(comparison['missing_skills'])} skills")
print(f"Match rate: {comparison['match_percentage']:.1f}%")
```

### 4. Get Skill Recommendations

```python
current_skills = ["Python", "React", "Django"]
target_role = "Full Stack Developer with React, Node.js, AWS, Docker"

recommendations = extractor.get_skill_recommendations(
    current_skills,
    target_role,
    top_n=10,
    threshold=0.65
)

print("Recommended skills to learn:")
for skill, relevance in recommendations:
    print(f"  • {skill} (relevance: {relevance:.3f})")
```

## Command Line Interface

### Test the Extractor

```bash
# Test with sample data (10,000 skills)
python rag_skills_extractor.py --max-skills 10000 --threshold 0.65 --test

# Test with more skills (slower but more accurate)
python rag_skills_extractor.py --max-skills 50000 --threshold 0.6 --test

# Use full dataset (very slow first time, cached afterward)
python rag_skills_extractor.py --max-skills None --threshold 0.65 --test
```

## Configuration Parameters

### `max_skills` (int or None)
- Controls how many skills to load from the CSV
- **10,000**: Fast, good for testing (~1-2 min first run)
- **50,000**: Balanced speed/coverage (~5-10 min first run)
- **100,000+**: High coverage (~15-30 min first run)
- **None**: Full dataset 3.2M skills (very slow, ~hours first run)
- **Note**: Embeddings are cached after first run!

### `threshold` (float, 0-1)
- Minimum similarity score for skill detection
- **0.5-0.6**: More skills detected (higher recall, lower precision)
- **0.65-0.7**: Balanced (recommended)
- **0.75+**: Fewer skills but more confident (higher precision, lower recall)

### `embedding_model` (string)
- Sentence transformer model to use
- **'all-MiniLM-L6-v2'**: Fast, good quality (default, recommended)
- **'all-mpnet-base-v2'**: Slower, better quality
- **'all-MiniLM-L12-v2'**: Balance of speed and quality

## Performance Tips

### First Run
The first run will:
1. Download the sentence transformer model (~80MB)
2. Load skills from CSV
3. Generate embeddings (slow - can take 10-60 min depending on max_skills)
4. Cache embeddings to disk

### Subsequent Runs
- Embeddings are loaded from cache (very fast! ~5-10 seconds)
- Only the model needs to be loaded

### Optimize Loading Time

```python
# For quick testing/development
extractor = RAGSkillsExtractor(max_skills=5000)  # ~30 sec first run

# For production use
extractor = RAGSkillsExtractor(max_skills=50000)  # ~5-10 min first run, cached afterward

# For maximum accuracy (be patient!)
extractor = RAGSkillsExtractor(max_skills=None)  # ~hours first run
```

## Integration with ATS Pipeline

### Update requirements.txt

```txt
# Add to requirements.txt
sentence-transformers>=5.0.0
```

### Use in Existing Pipeline

```python
from rag_skills_extractor import RAGSkillsExtractor
from pdf_extractor import PDFExtractor
from similarity_calculator import SimilarityCalculator

# Initialize components
pdf_extractor = PDFExtractor()
rag_extractor = RAGSkillsExtractor(max_skills=50000)
similarity_calc = SimilarityCalculator()

# Extract text from resume
resume_text = pdf_extractor.extract_text("resume.pdf")

# Extract skills using RAG
resume_skills = rag_extractor.extract_skills_rag(resume_text, threshold=0.65)
job_skills = rag_extractor.extract_skills_rag(job_description, threshold=0.65)

# Calculate similarity
similarity = similarity_calc.calculate_similarity(
    resume_skills,
    job_skills,
    resume_text,
    job_description
)

print(f"Match score: {similarity['overall_score']:.2%}")
```

## Comparison: Traditional vs RAG

### Traditional Keyword Extraction
```python
# Old method: exact string matching
skills = ["python", "javascript", "react", "django"]
detected = [s for s in skills if s in text.lower()]
# Result: Only exact matches, misses variations
```

### RAG-Based Extraction
```python
# New method: semantic similarity
skills = extractor.extract_skills_rag(text, threshold=0.65)
# Result: Finds "Python", "Python programming", "Python 3.x", etc.
```

### Benefits of RAG

| Aspect | Traditional | RAG |
|--------|------------|-----|
| **Exact matches** | ✅ Perfect | ✅ Perfect |
| **Variations** | ❌ Missed | ✅ Detected |
| **Synonyms** | ❌ Missed | ✅ Detected |
| **Context** | ❌ Ignored | ✅ Considered |
| **Coverage** | ~200 skills | 3.2M+ skills |
| **Speed** | ⚡ Very fast | 🐢 Slower |

## Examples

### Example 1: Software Engineer Resume

```python
resume = """
Senior Software Engineer with 5+ years building web applications.
Expert in Python, JavaScript, and React. Deployed applications on AWS.
Used Docker for containerization and PostgreSQL for databases.
"""

skills = extractor.extract_skills_rag(resume, threshold=0.65)
# Result: ['Python', 'JavaScript', 'React', 'AWS', 'Docker', 
#          'PostgreSQL', 'Web Applications', 'Containerization', etc.]
```

### Example 2: Data Scientist Resume

```python
resume = """
Data Scientist specializing in machine learning and deep learning.
Proficient in TensorFlow, PyTorch, and scikit-learn.
Experience with data analysis using pandas and numpy.
"""

skills = extractor.extract_skills_rag(resume, threshold=0.65)
# Result: ['Machine Learning', 'Deep Learning', 'TensorFlow', 
#          'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 
#          'Data Analysis', etc.]
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'sentence_transformers'"
```bash
pip install sentence-transformers
```

### "Out of memory" error
```python
# Reduce max_skills
extractor = RAGSkillsExtractor(max_skills=10000)
```

### Slow initial loading
- This is normal! Embeddings are being generated.
- Subsequent runs will be fast (cached).
- Use smaller `max_skills` for faster testing.

### Too many/few skills detected
- Increase `threshold` for fewer skills (more strict)
- Decrease `threshold` for more skills (less strict)

## Cache Management

Embeddings are cached in:
- `skills_embeddings_csv_5000.pkl` (for max_skills=5000)
- `skills_embeddings_csv_10000.pkl` (for max_skills=10000)
- `skills_embeddings_csv_50000.pkl` (for max_skills=50000)
- `skills_embeddings_csv_full.pkl` (for max_skills=None)

To regenerate embeddings:
```bash
# Delete cache file
rm skills_embeddings_csv_*.pkl

# Run again - will regenerate
python rag_skills_extractor.py --max-skills 10000 --test
```

## API Reference

### RAGSkillsExtractor

```python
RAGSkillsExtractor(
    skills_csv_path: str = 'data/skills_exploded (2).csv',
    embedding_model: str = 'all-MiniLM-L6-v2',
    max_skills: int = None
)
```

### extract_skills_rag()

```python
extract_skills_rag(
    text: str,
    threshold: float = 0.6,
    top_k: int = None,
    return_scores: bool = False
) -> List[str] | List[Tuple[str, float]]
```

### compare_skills()

```python
compare_skills(
    resume_text: str,
    job_desc_text: str,
    threshold: float = 0.6
) -> Dict
```

Returns:
```python
{
    'matched_skills': List[str],
    'missing_skills': List[str],
    'additional_skills': List[str],
    'match_percentage': float,
    'resume_skill_count': int,
    'job_skill_count': int
}
```

### get_skill_recommendations()

```python
get_skill_recommendations(
    current_skills: List[str],
    target_role: str,
    top_n: int = 10,
    threshold: float = 0.6
) -> List[Tuple[str, float]]
```

## Future Enhancements

- [ ] Category-based skill grouping
- [ ] Skill level detection (beginner/intermediate/expert)
- [ ] Years of experience extraction
- [ ] Industry-specific skill filtering
- [ ] Multi-language support
- [ ] Real-time API endpoint
- [ ] Web interface integration

## License

Part of ATS Resume Analyzer project.
