"""
CV Format Analyzer
Standalone tool to analyze CV format and structure
"""

import sys
from pdf_extractor import PDFExtractor
import json


def print_format_analysis(analysis: dict):
    """Print a formatted analysis report"""
    
    if not analysis.get('success'):
        print(f"❌ Error: {analysis.get('error', 'Unknown error')}")
        return
    
    print("\n" + "="*70)
    print("📋 CV FORMAT ANALYSIS REPORT")
    print("="*70)
    
    # File Information
    file_info = analysis['file_info']
    print(f"\n📄 FILE INFORMATION:")
    print(f"   • File Name: {file_info['file_name']}")
    print(f"   • Format: {file_info['file_extension'].upper()}")
    print(f"   • File Size: {file_info['file_size_kb']:.2f} KB")
    
    # PDF Metadata
    pdf_meta = analysis['pdf_metadata']
    print(f"\n📑 PDF DETAILS:")
    print(f"   • Page Count: {pdf_meta['page_count']}")
    print(f"   • Encrypted: {'Yes' if pdf_meta['is_encrypted'] else 'No'}")
    print(f"   • Text Length: {analysis['text_length']} characters")
    print(f"   • Extraction Quality: {analysis['extraction_quality']}")
    
    # Structure Analysis
    structure = analysis['structure_analysis']
    print(f"\n🏗️  CV STRUCTURE:")
    print(f"   • Format Type: {structure['cv_format']}")
    print(f"   • Sections Found: {structure['section_count']}")
    
    if structure['detected_sections']:
        print(f"\n   📋 Detected Sections:")
        for section in structure['detected_sections'][:10]:
            print(f"      ✓ {section.title()}")
        if len(structure['detected_sections']) > 10:
            print(f"      ... and {len(structure['detected_sections']) - 10} more")
    
    # Contact Information
    contact = structure['has_contact_info']
    print(f"\n   📞 Contact Information:")
    print(f"      {'✓' if contact['email'] else '✗'} Email")
    print(f"      {'✓' if contact['phone'] else '✗'} Phone Number")
    print(f"      {'✓' if contact['linkedin'] else '✗'} LinkedIn")
    print(f"      {'✓' if contact['github'] else '✗'} GitHub")
    
    # Formatting Quality
    formatting = structure['formatting']
    print(f"\n   🎨 Formatting:")
    print(f"      • Bullet Points: {'Yes ✓' if formatting['has_bullets'] else 'No ✗'}")
    print(f"      • Dates Found: {formatting['dates_found']}")
    print(f"      • Average Line Length: {formatting['avg_line_length']:.1f} characters")
    print(f"      • Total Lines: {formatting['total_lines']}")
    print(f"      • Non-Empty Lines: {formatting['non_empty_lines']}")
    
    # ATS Score
    print(f"\n🤖 ATS COMPATIBILITY:")
    score = structure['ats_friendly_score']
    rating = structure['ats_friendly_rating']
    
    # Visual score bar
    bar_length = 50
    filled_length = int(bar_length * score / 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    # Color based on score
    if score >= 80:
        emoji = "🟢"
    elif score >= 60:
        emoji = "🟡"
    elif score >= 40:
        emoji = "🟠"
    else:
        emoji = "🔴"
    
    print(f"   {emoji} Score: {score}/100")
    print(f"   [{bar}] {score}%")
    print(f"   Rating: {rating}")
    
    # Quality Issues
    if structure['quality_issues']:
        print(f"\n⚠️  QUALITY ISSUES:")
        for issue in structure['quality_issues']:
            print(f"   • {issue}")
    else:
        print(f"\n✅ No quality issues detected!")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if score >= 80:
        print("   ✅ Your CV is well-formatted and ATS-friendly!")
    elif score >= 60:
        print("   👍 Good format, but some improvements possible:")
    else:
        print("   ⚠️  Your CV needs significant improvements:")
    
    if not contact['email']:
        print("   • Add your email address")
    if not contact['phone']:
        print("   • Add your phone number")
    if not formatting['has_bullets']:
        print("   • Use bullet points for better readability")
    if structure['section_count'] < 3:
        print("   • Add clear section headers (Experience, Education, Skills, etc.)")
    if formatting['dates_found'] < 2:
        print("   • Include dates for your experience and education")
    if analysis['text_length'] < 500:
        print("   • Your CV seems too short - add more details")
    
    print("\n" + "="*70)
    
    # Language information
    language_info = structure.get('languages', {})
    if language_info and language_info.get('detected_languages'):
        print("\n🌍 LANGUAGES:")
        print("="*70)
        print(f"   • Total Languages: {language_info['language_count']}")
        print(f"   • Has Language Section: {'Yes' if language_info['has_language_section'] else 'No'}")
        
        print(f"\n   📋 Detected Languages:")
        for lang in language_info['detected_languages']:
            proficiency = lang.get('proficiency')
            if proficiency:
                print(f"      • {lang['language']}: {proficiency}")
            else:
                print(f"      • {lang['language']}")
    
    # Show extracted section summary
    extracted = structure.get('extracted_sections', {})
    if extracted:
        print("\n📝 EXTRACTED SECTIONS SUMMARY:")
        print("="*70)
        for section_name, content in extracted.items():
            if content:
                word_count = len(content.split())
                lines = len([line for line in content.split('\n') if line.strip()])
                preview = content[:100].replace('\n', ' ') + '...' if len(content) > 100 else content.replace('\n', ' ')
                print(f"\n   📌 {section_name}:")
                print(f"      • {word_count} words, {lines} lines")
                print(f"      • Preview: {preview}")
        
        print("\n" + "="*70)
        print(f"💡 Use 'python section_extractor.py <resume.pdf>' to see full extracted sections")
    
    print("\n" + "="*70)


def main():
    """Main function for CV format analysis"""
    
    if len(sys.argv) < 2:
        print("Usage: python cv_format_analyzer.py <resume.pdf>")
        print("\nExample:")
        print("  python cv_format_analyzer.py my_resume.pdf")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    
    print("🔍 Analyzing CV format...")
    
    # Analyze the CV
    extractor = PDFExtractor()
    analysis = extractor.analyze_pdf(resume_path)
    
    # Print results
    print_format_analysis(analysis)
    
    # Save to JSON
    output_file = "cv_format_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Detailed analysis saved to: {output_file}")


if __name__ == "__main__":
    main()
