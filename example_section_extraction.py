"""
Example: Using Extracted Resume Sections
Demonstrates how to work with extracted sections programmatically
"""

from pdf_extractor import PDFExtractor
import json


def example_extract_and_analyze():
    """Extract sections and perform custom analysis"""
    
    # Initialize extractor
    extractor = PDFExtractor()
    
    # Analyze resume
    resume_path = "resume&job_description/11890896.pdf"
    analysis = extractor.analyze_pdf(resume_path)
    
    if not analysis['success']:
        print(f"Error: {analysis['error']}")
        return
    
    # Get extracted sections
    structure = analysis['structure_analysis']
    sections = structure['extracted_sections']
    
    print("="*70)
    print("WORKING WITH EXTRACTED RESUME SECTIONS")
    print("="*70)
    
    # Example 1: Get specific section
    print("\n📌 Example 1: Access Specific Section")
    print("-" * 70)
    
    if 'Skills' in sections:
        skills_text = sections['Skills']
        print(f"Skills Section ({len(skills_text)} characters):")
        print(skills_text[:200] + "..." if len(skills_text) > 200 else skills_text)
    
    # Example 2: Analyze all sections
    print("\n📌 Example 2: Analyze All Sections")
    print("-" * 70)
    
    for section_name, content in sections.items():
        if content:
            word_count = len(content.split())
            sentences = content.count('.') + content.count('!') + content.count('?')
            print(f"\n{section_name}:")
            print(f"  • Words: {word_count}")
            print(f"  • Sentences: ~{sentences}")
            print(f"  • Characters: {len(content)}")
    
    # Example 3: Check if specific sections exist
    print("\n📌 Example 3: Section Presence Check")
    print("-" * 70)
    
    required_sections = ['Experience', 'Education', 'Skills']
    optional_sections = ['Certifications', 'Projects', 'Publications']
    
    print("\nRequired Sections:")
    for section in required_sections:
        has_section = any(section.lower() in s.lower() for s in sections.keys())
        status = "✓ Found" if has_section else "✗ Missing"
        print(f"  {status}: {section}")
    
    print("\nOptional Sections:")
    for section in optional_sections:
        has_section = any(section.lower() in s.lower() for s in sections.keys())
        status = "✓ Found" if has_section else "✗ Not present"
        print(f"  {status}: {section}")
    
    # Example 4: Extract specific information
    print("\n📌 Example 4: Extract Specific Information")
    print("-" * 70)
    
    # Look for programming languages in Skills section
    if 'Skills' in sections:
        skills_lower = sections['Skills'].lower()
        programming_langs = ['python', 'java', 'javascript', 'c++', 'c#', 'sql', 'r']
        
        found_langs = [lang for lang in programming_langs if lang in skills_lower]
        
        print(f"\nProgramming Languages Found: {', '.join(found_langs) if found_langs else 'None'}")
    
    # Example 5: Generate section-based insights
    print("\n📌 Example 5: Section-Based Insights")
    print("-" * 70)
    
    insights = []
    
    if 'Summary' in sections or 'Profile' in sections:
        insights.append("✓ Has professional summary - good for ATS")
    else:
        insights.append("⚠ Consider adding a professional summary")
    
    if any('experience' in s.lower() for s in sections.keys()):
        exp_section = next((v for k, v in sections.items() if 'experience' in k.lower()), '')
        if len(exp_section) > 500:
            insights.append("✓ Detailed experience section")
        else:
            insights.append("⚠ Experience section could be more detailed")
    
    if 'Skills' in sections:
        skills_words = len(sections['Skills'].split())
        if skills_words > 30:
            insights.append("✓ Comprehensive skills section")
        else:
            insights.append("⚠ Skills section could list more skills")
    
    print("\nInsights:")
    for insight in insights:
        print(f"  {insight}")
    
    # Example 6: Export for further processing
    print("\n📌 Example 6: Export Sections")
    print("-" * 70)
    
    export_data = {
        'metadata': {
            'file_name': analysis['file_info']['file_name'],
            'page_count': analysis['pdf_metadata']['page_count'],
            'ats_score': structure['ats_friendly_score']
        },
        'sections': sections
    }
    
    output_file = 'resume_sections_export.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Sections exported to: {output_file}")
    
    print("\n" + "="*70)


def example_compare_sections():
    """Compare sections between resume and job requirements"""
    
    print("\n" + "="*70)
    print("COMPARING RESUME SECTIONS WITH JOB REQUIREMENTS")
    print("="*70)
    
    # Sample job requirements
    job_requirements = {
        'required_sections': ['Experience', 'Education', 'Skills'],
        'preferred_sections': ['Certifications', 'Projects'],
        'key_skills': ['data analysis', 'project management', 'sql', 'python']
    }
    
    # Extract resume sections
    extractor = PDFExtractor()
    resume_path = "resume&job_description/11890896.pdf"
    analysis = extractor.analyze_pdf(resume_path)
    
    if not analysis['success']:
        print(f"Error: {analysis['error']}")
        return
    
    sections = analysis['structure_analysis']['extracted_sections']
    
    # Check required sections
    print("\n✓ Required Sections Check:")
    for req_section in job_requirements['required_sections']:
        has_section = any(req_section.lower() in s.lower() for s in sections.keys())
        print(f"  {'✓' if has_section else '✗'} {req_section}")
    
    # Check preferred sections
    print("\n⭐ Preferred Sections Check:")
    for pref_section in job_requirements['preferred_sections']:
        has_section = any(pref_section.lower() in s.lower() for s in sections.keys())
        print(f"  {'✓' if has_section else '✗'} {pref_section}")
    
    # Check key skills
    print("\n🔑 Key Skills Check:")
    skills_text = sections.get('Skills', '').lower()
    
    for skill in job_requirements['key_skills']:
        has_skill = skill.lower() in skills_text
        print(f"  {'✓' if has_skill else '✗'} {skill}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("\n🚀 Running Section Extraction Examples\n")
    
    # Run examples
    example_extract_and_analyze()
    
    example_compare_sections()
    
    print("\n✅ Examples completed!")
    print("\n💡 Tips:")
    print("  • Extracted sections are in 'extracted_sections' dictionary")
    print("  • Section names are title-cased (e.g., 'Experience', 'Skills')")
    print("  • Content preserves original formatting and line breaks")
    print("  • Empty sections are excluded from results")
