"""
Example Usage of ATS Pipeline
Demonstrates how to use the resume analyzer
"""

from ats_pipeline import ATSPipeline


def example_with_pdf_and_text():
    """Example: Analyze a PDF resume against a job description"""
    
    # Sample job description
    job_description = """
    Senior Python Developer
    
    We are seeking an experienced Python Developer to join our team.
    
    Requirements:
    - 5+ years of experience with Python
    - Strong knowledge of Django or Flask frameworks
    - Experience with RESTful API development
    - Proficiency in SQL databases (PostgreSQL, MySQL)
    - Experience with Docker and Kubernetes
    - Knowledge of AWS or Azure cloud services
    - Familiarity with Git version control
    - Experience with agile methodologies
    - Strong problem-solving and communication skills
    
    Nice to have:
    - Experience with React or Angular
    - Knowledge of machine learning libraries (TensorFlow, PyTorch)
    - Experience with CI/CD pipelines
    - Familiarity with microservices architecture
    """
    
    # Initialize pipeline
    pipeline = ATSPipeline(use_spacy=True)
    
    # Analyze resume (replace with your actual PDF path)
    resume_pdf_path = "path/to/your/resume.pdf"
    
    print("="*60)
    print("ATS RESUME ANALYZER - EXAMPLE")
    print("="*60)
    
    # Run analysis
    results = pipeline.analyze(
        resume_pdf_path=resume_pdf_path,
        job_description=job_description,
        verbose=True
    )
    
    # Save results
    if results.get('success'):
        pipeline.save_results(results, 'example_results.json')
        print("\n✅ Analysis complete! Check 'example_results.json' for detailed results.")
    else:
        print(f"\n❌ Analysis failed: {results.get('error')}")


def example_programmatic_access():
    """Example: Programmatically access analysis results"""
    
    job_description = """
    Data Scientist Position
    
    Requirements:
    - Python programming
    - Machine learning experience
    - Experience with pandas, numpy, scikit-learn
    - SQL knowledge
    - Data visualization skills
    - Statistical analysis background
    """
    
    pipeline = ATSPipeline(use_spacy=False)  # Disable spaCy for faster processing
    
    # Analyze (replace with your PDF)
    results = pipeline.analyze(
        resume_pdf_path="path/to/resume.pdf",
        job_description=job_description,
        verbose=False  # Silent mode
    )
    
    if results.get('success'):
        # Access specific results
        overall_score = results['similarity_scores']['overall_percentage']
        matched_skills = results['similarity_scores']['matched_skills']
        missing_skills = results['similarity_scores']['missing_skills']
        
        print(f"\nQuick Results:")
        print(f"  Score: {overall_score}%")
        print(f"  Matched Skills: {', '.join(matched_skills)}")
        print(f"  Missing Skills: {', '.join(missing_skills)}")
        
        # Make decisions based on score
        if overall_score >= 70:
            print("\n✅ Recommend applying for this position!")
        elif overall_score >= 50:
            print("\n⚠️ Consider updating resume to better match requirements.")
        else:
            print("\n❌ Resume needs significant updates for this position.")


def example_with_text_resume():
    """Example: Use with plain text resume instead of PDF"""
    
    resume_text = """
    John Doe
    Senior Software Engineer
    
    Skills:
    - Python, Java, JavaScript
    - Django, Flask, Spring Boot
    - PostgreSQL, MongoDB
    - Docker, Kubernetes
    - AWS, Git
    - REST API development
    - Agile methodologies
    
    Experience:
    5 years of backend development experience...
    """
    
    job_description = """
    Backend Developer needed with Python and cloud experience.
    Must have: Python, Django, Docker, AWS, PostgreSQL
    """
    
    # For text resume, you can directly use the components
    from keyword_extractor import KeywordExtractor
    from similarity_calculator import SimilarityCalculator
    
    keyword_extractor = KeywordExtractor(use_spacy=True)
    similarity_calculator = SimilarityCalculator()
    
    # Extract keywords
    resume_keywords = keyword_extractor.extract_keywords(resume_text)
    job_keywords = keyword_extractor.extract_keywords(job_description)
    
    # Calculate similarity
    results = similarity_calculator.calculate_weighted_score(
        resume_text,
        job_description,
        resume_keywords,
        job_keywords
    )
    
    print(f"\nText Resume Analysis:")
    print(f"  Match Score: {results['overall_percentage']}%")
    print(f"  Match Level: {results['match_level']}")
    print(f"  Matched Skills: {results['matched_skills']}")


if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Analyze PDF resume against job description")
    print("2. Programmatic access to results")
    print("3. Analyze text resume (no PDF)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        example_with_pdf_and_text()
    elif choice == "2":
        example_programmatic_access()
    elif choice == "3":
        example_with_text_resume()
    else:
        print("Invalid choice. Running example 3 (text resume)...")
        example_with_text_resume()
