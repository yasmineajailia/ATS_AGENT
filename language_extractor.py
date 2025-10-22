"""
Language Extractor
Extracts language information from resumes
"""

import sys
from pdf_extractor import PDFExtractor
import json


def print_language_info(analysis: dict):
    """Print language information in a readable format"""
    
    if not analysis.get('success'):
        print(f"❌ Error: {analysis.get('error', 'Unknown error')}")
        return
    
    structure = analysis['structure_analysis']
    language_info = structure.get('languages', {})
    
    print("\n" + "="*70)
    print("🌍 LANGUAGE EXTRACTION REPORT")
    print("="*70)
    
    # Basic info
    print(f"\n📊 Summary:")
    print(f"   • Languages Detected: {language_info.get('language_count', 0)}")
    print(f"   • Has Dedicated Language Section: {'Yes' if language_info.get('has_language_section') else 'No'}")
    
    # Detected languages
    detected = language_info.get('detected_languages', [])
    
    if detected:
        print(f"\n📋 Detected Languages:")
        print("-" * 70)
        
        for i, lang in enumerate(detected, 1):
            proficiency = lang.get('proficiency')
            
            if proficiency:
                print(f"   {i}. {lang['language']}: {proficiency}")
            else:
                print(f"   {i}. {lang['language']}")
        
        # Categorize by proficiency
        proficiency_groups = {}
        for lang in detected:
            prof = lang.get('proficiency', 'Not Specified')
            if prof not in proficiency_groups:
                proficiency_groups[prof] = []
            proficiency_groups[prof].append(lang['language'])
        
        if len(proficiency_groups) > 1 or 'Not Specified' not in proficiency_groups:
            print(f"\n📊 By Proficiency Level:")
            print("-" * 70)
            
            # Order by proficiency level
            level_order = ['Native', 'Fluent', 'Proficient', 'Advanced', 'Intermediate', 
                          'Basic', 'Beginner', 'Elementary', 'Conversational', 'Not Specified']
            
            for level in level_order:
                if level in proficiency_groups:
                    langs = ', '.join(proficiency_groups[level])
                    print(f"   • {level}: {langs}")
    else:
        print(f"\n⚠️  No languages detected in the resume.")
        print(f"   💡 Tip: Add a 'Languages' section to your resume")
    
    # Show full language section if available
    lang_section = language_info.get('languages_section')
    if lang_section:
        print(f"\n📄 Full Language Section Content:")
        print("="*70)
        print(lang_section)
    
    print("\n" + "="*70)
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 70)
    
    if not detected:
        print("   ⚠️  No languages found. Consider adding a 'Languages' section.")
        print("   📝 Example format:")
        print("      Languages:")
        print("      • English: Native")
        print("      • Spanish: Fluent")
        print("      • French: Intermediate")
    elif language_info.get('language_count', 0) == 1:
        print("   ℹ️  Only one language detected.")
        print("   💡 If you speak multiple languages, list them all!")
    else:
        print("   ✅ Multiple languages detected - great for international roles!")
    
    # Check if proficiency levels are specified
    missing_proficiency = [lang['language'] for lang in detected if not lang.get('proficiency')]
    if missing_proficiency:
        print(f"\n   📝 Consider adding proficiency levels for:")
        for lang in missing_proficiency:
            print(f"      • {lang}")
        print(f"\n   Suggested levels: Native, Fluent, Advanced, Intermediate, Basic")
    
    print("\n" + "="*70)


def export_languages(analysis: dict, output_file: str = "languages.json"):
    """Export language information to JSON"""
    
    if not analysis.get('success'):
        print(f"❌ Cannot export: {analysis.get('error', 'Unknown error')}")
        return
    
    structure = analysis['structure_analysis']
    language_info = structure.get('languages', {})
    
    output = {
        'file_name': analysis['file_info']['file_name'],
        'language_count': language_info.get('language_count', 0),
        'has_language_section': language_info.get('has_language_section', False),
        'languages': language_info.get('detected_languages', []),
        'language_section_text': language_info.get('languages_section')
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Language data exported to: {output_file}")


def main():
    """Main function for language extraction"""
    
    if len(sys.argv) < 2:
        print("Usage: python language_extractor.py <resume.pdf>")
        print("\nExample:")
        print("  python language_extractor.py my_resume.pdf")
        print("\nThis tool extracts language information from your resume including:")
        print("  • Language names")
        print("  • Proficiency levels")
        print("  • Full language section content")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    
    print("🔍 Extracting language information from resume...")
    
    # Analyze the CV
    extractor = PDFExtractor()
    analysis = extractor.analyze_pdf(resume_path)
    
    # Print language information
    print_language_info(analysis)
    
    # Export to JSON
    export_languages(analysis, "languages.json")
    
    # Additional statistics
    if analysis.get('success'):
        structure = analysis['structure_analysis']
        language_info = structure.get('languages', {})
        detected = language_info.get('detected_languages', [])
        
        if detected:
            print(f"\n📈 Statistics:")
            print(f"   • Total languages: {len(detected)}")
            print(f"   • With proficiency specified: {sum(1 for l in detected if l.get('proficiency'))}")
            print(f"   • Without proficiency: {sum(1 for l in detected if not l.get('proficiency'))}")


if __name__ == "__main__":
    main()
