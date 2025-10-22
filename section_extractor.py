"""
Resume Section Extractor
Extracts and displays structured sections from a resume
"""

import sys
from pdf_extractor import PDFExtractor
import json


def print_extracted_sections(analysis: dict):
    """Print extracted sections in a readable format"""
    
    if not analysis.get('success'):
        print(f"❌ Error: {analysis.get('error', 'Unknown error')}")
        return
    
    structure = analysis['structure_analysis']
    extracted = structure.get('extracted_sections', {})
    
    print("\n" + "="*70)
    print("📋 EXTRACTED RESUME SECTIONS")
    print("="*70)
    
    # Show languages first if detected
    language_info = structure.get('languages', {})
    if language_info and language_info.get('detected_languages'):
        print(f"\n{'='*70}")
        print(f"🌍 LANGUAGES ({language_info['language_count']} detected)")
        print(f"{'='*70}")
        
        for lang in language_info['detected_languages']:
            proficiency = lang.get('proficiency')
            if proficiency:
                print(f"   • {lang['language']}: {proficiency}")
            else:
                print(f"   • {lang['language']}")
        
        # Show full language section if available
        if language_info.get('languages_section'):
            print(f"\n   📄 Full Language Section:")
            print(f"   {'-'*66}")
            for line in language_info['languages_section'].split('\n')[:5]:
                print(f"   {line}")
            if len(language_info['languages_section'].split('\n')) > 5:
                print(f"   ...")
    
    if not extracted:
        print("\n⚠️  No sections could be extracted from the resume.")
        return
    
    # Define section order for better presentation
    section_order = [
        'Summary', 'Profile', 'Objective', 'About Me',
        'Experience', 'Professional Experience', 'Work Experience', 'Employment',
        'Education', 'Academic Background', 'Qualifications',
        'Skills', 'Technical Skills', 'Core Competencies', 'Expertise',
        'Projects', 'Personal Projects',
        'Certifications', 'Certificates', 'Licenses',
        'Achievements', 'Accomplishments', 'Awards',
        'Publications', 'Research',
        'Volunteer', 'Volunteering',
        'Languages', 'Interests', 'Hobbies'
    ]
    
    # Print sections in order
    printed_sections = set()
    
    for section_name in section_order:
        if section_name in extracted and section_name not in printed_sections:
            content = extracted[section_name]
            if content:
                print(f"\n{'='*70}")
                print(f"📌 {section_name.upper()}")
                print(f"{'='*70}")
                print(content)
                printed_sections.add(section_name)
    
    # Print any remaining sections not in the order
    for section_name, content in extracted.items():
        if section_name not in printed_sections and content:
            print(f"\n{'='*70}")
            print(f"📌 {section_name.upper()}")
            print(f"{'='*70}")
            print(content)
    
    print("\n" + "="*70)
    print(f"✅ Total sections extracted: {len([s for s in extracted.values() if s])}")
    print("="*70)


def save_sections_to_json(analysis: dict, output_file: str):
    """Save extracted sections to JSON file"""
    
    if not analysis.get('success'):
        print(f"❌ Cannot save: {analysis.get('error', 'Unknown error')}")
        return
    
    structure = analysis['structure_analysis']
    extracted = structure.get('extracted_sections', {})
    language_info = structure.get('languages', {})
    
    # Create a clean output structure
    output = {
        'file_name': analysis['file_info']['file_name'],
        'languages': {
            'detected': language_info.get('detected_languages', []),
            'count': language_info.get('language_count', 0)
        },
        'sections': {}
    }
    
    for section_name, content in extracted.items():
        if content:
            output['sections'][section_name] = content
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Sections saved to: {output_file}")


def main():
    """Main function for section extraction"""
    
    if len(sys.argv) < 2:
        print("Usage: python section_extractor.py <resume.pdf>")
        print("\nExample:")
        print("  python section_extractor.py my_resume.pdf")
        print("\nThis tool extracts structured sections from your resume:")
        print("  • Experience")
        print("  • Education")
        print("  • Skills")
        print("  • Certifications")
        print("  • And more...")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    
    print("🔍 Analyzing and extracting resume sections...")
    
    # Analyze the CV
    extractor = PDFExtractor()
    analysis = extractor.analyze_pdf(resume_path)
    
    # Print extracted sections
    print_extracted_sections(analysis)
    
    # Save to JSON
    output_file = "extracted_sections.json"
    save_sections_to_json(analysis, output_file)
    
    # Show section statistics
    if analysis.get('success'):
        structure = analysis['structure_analysis']
        extracted = structure.get('extracted_sections', {})
        
        print(f"\n📊 Section Statistics:")
        for section_name, content in extracted.items():
            if content:
                word_count = len(content.split())
                char_count = len(content)
                lines = len([line for line in content.split('\n') if line.strip()])
                print(f"   • {section_name}: {word_count} words, {lines} lines")


if __name__ == "__main__":
    main()
