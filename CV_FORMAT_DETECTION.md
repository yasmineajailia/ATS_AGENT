# CV Format Detection Guide

## Overview

The ATS Resume Analyzer now includes advanced CV format detection capabilities that analyze your resume's structure, formatting, and ATS compatibility.

## What Gets Detected

### 1. File Information
- **File name and extension**
- **File size**
- **Number of pages**
- **Encryption status**

### 2. CV Structure Detection

The analyzer identifies common CV sections:
- Experience / Professional Experience / Work History
- Education / Academic Background
- Skills / Technical Skills / Core Competencies
- Projects / Personal Projects
- Certifications / Licenses
- Summary / Profile / Objective
- Achievements / Accomplishments / Awards
- Publications / Research
- Volunteer Experience
- Languages / Interests / Hobbies

### 3. Contact Information Detection
- ✉️ Email address
- 📱 Phone number
- 💼 LinkedIn profile
- 💻 GitHub profile

### 4. Formatting Analysis
- **Bullet points**: Checks for proper use of bullets
- **Dates**: Identifies employment/education dates
- **Line length**: Analyzes text formatting
- **Text density**: Measures content distribution

### 5. ATS-Friendliness Score (0-100)

Your resume is scored based on:

| Factor | Points | Description |
|--------|--------|-------------|
| **Sections** | 30 | Having 3+ clear sections |
| **Email** | 10 | Email address present |
| **Phone** | 10 | Phone number present |
| **Bullets** | 15 | Uses bullet points |
| **Dates** | 15 | Has 2+ dates |
| **Clean Format** | 10 | No unusual characters |
| **Line Length** | 10 | Optimal line length (20-100 chars) |
| **Total** | **100** | Maximum possible score |

### Score Ratings:
- **80-100**: 🟢 Excellent - ATS Optimized
- **60-79**: 🟡 Good - ATS Friendly
- **40-59**: 🟠 Fair - Needs Improvement
- **0-39**: 🔴 Poor - Not ATS Friendly

## Usage

### Standalone Format Analysis

```bash
python cv_format_analyzer.py resume.pdf
```

**Output includes:**
- Complete format analysis
- ATS compatibility score
- Detected sections
- Contact information status
- Formatting quality metrics
- Specific recommendations

### Within Full Pipeline

```bash
python ats_pipeline.py resume.pdf job_description.txt
```

This automatically includes format analysis before the job match analysis.

### Python API

```python
from pdf_extractor import PDFExtractor

extractor = PDFExtractor()

# Full analysis
analysis = extractor.analyze_pdf("resume.pdf")

print(f"CV Format: {analysis['structure_analysis']['cv_format']}")
print(f"ATS Score: {analysis['structure_analysis']['ats_friendly_score']}/100")
print(f"Sections: {analysis['structure_analysis']['detected_sections']}")

# Just structure detection
text = extractor.extract_text("resume.pdf")
structure = extractor.detect_cv_structure(text)
```

## Common Issues Detected

### 🔴 Critical Issues
- **No sections detected**: CV lacks clear structure
- **Very short content**: Less than 500 characters
- **No contact information**: Missing email or phone
- **Encoding problems**: Unusual or corrupted characters

### 🟡 Moderate Issues
- **Missing bullet points**: Hard to scan
- **Few dates**: Employment history unclear
- **Short lines**: Possible extraction issue
- **Limited sections**: Could add more structure

## Tips for Improving Your ATS Score

1. **Add Clear Section Headers**
   - Use standard names: "Experience", "Education", "Skills"
   - Make them bold or larger font
   - Separate sections clearly

2. **Include Contact Information**
   - Email address (required)
   - Phone number (required)
   - LinkedIn URL (recommended)
   - GitHub (for technical roles)

3. **Use Bullet Points**
   - Start each responsibility/achievement with a bullet
   - Use consistent bullet style
   - Makes resume scannable

4. **Include Dates**
   - Format: MM/YYYY or YYYY
   - For all experiences and education
   - Shows timeline clearly

5. **Avoid Complex Formatting**
   - Don't use tables or columns (many ATS can't parse them)
   - Avoid headers/footers
   - Don't embed text in images
   - Use standard fonts

6. **Keep It Clean**
   - Remove special characters
   - Use standard characters only
   - Avoid graphics and images
   - Save as PDF (not image-based PDF)

## Example Output

```
======================================================================
📋 CV FORMAT ANALYSIS REPORT
======================================================================

📄 FILE INFORMATION:
   • File Name: john_doe_resume.pdf
   • Format: .PDF
   • File Size: 45.23 KB

📑 PDF DETAILS:
   • Page Count: 2
   • Encrypted: No
   • Text Length: 6521 characters
   • Extraction Quality: Good

🏗️  CV STRUCTURE:
   • Format Type: Well-Structured
   • Sections Found: 7

   📋 Detected Sections:
      ✓ Experience
      ✓ Education
      ✓ Skills
      ✓ Projects
      ✓ Certifications
      ✓ Summary
      ✓ Accomplishments

   📞 Contact Information:
      ✓ Email
      ✓ Phone Number
      ✓ LinkedIn
      ✗ GitHub

   🎨 Formatting:
      • Bullet Points: Yes ✓
      • Dates Found: 12
      • Average Line Length: 42.3 characters
      • Total Lines: 185
      • Non-Empty Lines: 142

🤖 ATS COMPATIBILITY:
   🟢 Score: 90/100
   [█████████████████████████████████████████████░░░░░] 90%
   Rating: Excellent - ATS Optimized

✅ No quality issues detected!

💡 RECOMMENDATIONS:
   ✅ Your CV is well-formatted and ATS-friendly!
```

## Integration with Job Match Analysis

When you run the full pipeline, format analysis happens first:

```
🔍 Starting ATS Analysis...
📋 Analyzing CV format and structure...
   ✓ CV Format: Well-Structured
   ✓ Sections Detected: 7
   ✓ ATS Score: 90/100 - Excellent - ATS Optimized
📄 Extracting text from resume PDF...
   ✓ Extracted 6521 characters from resume
...
```

The format analysis is included in the final JSON output:

```json
{
  "success": true,
  "format_analysis": {
    "structure_analysis": {
      "cv_format": "Well-Structured",
      "ats_friendly_score": 90,
      "detected_sections": [...],
      ...
    }
  },
  "similarity_scores": {...},
  ...
}
```

## Technical Details

### Section Detection Algorithm
1. Searches for common section keywords
2. Uses regex with word boundaries
3. Case-insensitive matching
4. Handles variations (e.g., "Work Experience", "Professional Experience")

### Contact Detection
- **Email**: Standard email regex pattern
- **Phone**: Multiple international formats
- **LinkedIn/GitHub**: Keyword search

### ATS Score Calculation
- Weighted scoring system
- Multiple quality factors
- Normalized to 0-100 scale
- Clear rating categories

## Limitations

- Works best with text-based PDFs (not scanned images)
- May miss non-standard section names
- Contact info detection depends on format
- Score is a guideline, not absolute measure

## Future Enhancements

- Support for DOCX files
- OCR for scanned PDFs
- Multi-language support
- Custom section names
- Industry-specific templates
- Visual format preview
