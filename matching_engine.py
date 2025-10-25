"""
Automated Matching Engine for Hiring Platform
Analyzes resumes against job postings and ranks candidates
"""

from typing import Dict, List
from hiring_platform_db import HiringPlatformDB
from ats_pipeline import ATSPipeline
from rag_skills_extractor import RAGSkillsExtractor
from llm_extractor import LLMResumeExtractor
from pdf_extractor import PDFExtractor
import os


class HiringMatchingEngine:
    """
    Automated matching engine that:
    1. Analyzes applicant resume against job description
    2. Calculates comprehensive match score
    3. Ranks applicants by score
    4. Filters candidates below threshold
    """
    
    def __init__(self, use_rag: bool = True, use_llm: bool = True):
        self.db = HiringPlatformDB()
        self.ats_pipeline = ATSPipeline(use_spacy=True)
        self.pdf_extractor = PDFExtractor()
        
        # Initialize RAG if enabled
        self.use_rag = use_rag
        if use_rag:
            self.rag_extractor = RAGSkillsExtractor(
                skills_csv_path="data/skills_exploded (2).csv",
                max_skills=10000
            )
        
        # Initialize LLM if enabled
        self.use_llm = use_llm
        if use_llm:
            self.llm_extractor = LLMResumeExtractor(
                provider='gemini',
                model='gemini-2.5-flash'
            )
    
    def process_application(self, user_id: int, job_id: int, 
                           resume_pdf_path: str) -> Dict:
        """
        Process a job application:
        1. Extract text from resume
        2. Run comprehensive analysis
        3. Calculate match scores
        4. Store in database
        
        Returns:
            Application details with scores and analysis
        """
        print(f"\n{'='*80}")
        print(f"PROCESSING APPLICATION")
        print(f"{'='*80}")
        print(f"User ID: {user_id}")
        print(f"Job ID: {job_id}")
        print(f"Resume: {resume_pdf_path}")
        
        # Get job details
        job = self.db.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        if job['status'] != 'active':
            raise ValueError(f"Job {job_id} is not active")
        
        # Get user details
        user = self.db.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Extract resume text
        print("\n📄 Extracting resume text...")
        format_analysis = self.pdf_extractor.analyze_pdf(resume_pdf_path)
        resume_text = format_analysis.get('text', '')
        ats_score = format_analysis['structure_analysis']['ats_friendly_score']
        
        print(f"   ✓ Extracted {len(resume_text)} characters")
        print(f"   ✓ ATS Score: {ats_score}/100")
        
        # Build job description for matching
        job_description = self._build_job_description(job)
        
        # Run ATS analysis
        print("\n🔍 Running ATS analysis...")
        ats_results = self.ats_pipeline.analyze(
            resume_pdf_path,
            job_description,
            verbose=False,
            analyze_format=False
        )
        
        overall_match = ats_results['similarity_scores']['overall_percentage']
        skills_match = ats_results['similarity_scores']['detailed_scores']['skills_match_rate'] * 100
        matched_skills = ats_results['similarity_scores']['matched_skills']
        missing_skills = ats_results['similarity_scores']['missing_skills']
        
        print(f"   ✓ Overall Match: {overall_match}%")
        print(f"   ✓ Skills Match: {skills_match}%")
        print(f"   ✓ Matched Skills: {len(matched_skills)}")
        print(f"   ✓ Missing Skills: {len(missing_skills)}")
        
        # RAG analysis (if enabled)
        rag_skills = None
        if self.use_rag:
            print("\n🔍 Running RAG skills extraction...")
            rag_skills = self.rag_extractor.extract_skills_rag(resume_text, threshold=0.65)
            print(f"   ✓ Detected {len(rag_skills)} skills via RAG")
        
        # LLM analysis (if enabled)
        llm_analysis = None
        if self.use_llm:
            print("\n🤖 Running LLM structured extraction...")
            llm_analysis = self.llm_extractor.extract_from_text(resume_text)
            print(f"   ✓ Technical Skills: {len(llm_analysis.get('technical_skills', []))}")
            print(f"   ✓ Soft Skills: {len(llm_analysis.get('soft_skills', []))}")
            print(f"   ✓ Experience: {llm_analysis.get('total_experience_years', 0)} years")
        
        # Compile comprehensive analysis
        analysis_results = {
            'ats_analysis': ats_results,
            'format_analysis': format_analysis,
            'rag_skills': rag_skills[:50] if rag_skills else None,  # Top 50 for storage
            'llm_analysis': llm_analysis
        }
        
        # Create application in database
        print("\n💾 Saving application to database...")
        application_id = self.db.create_application(
            job_id=job_id,
            user_id=user_id,
            match_score=overall_match,
            skills_match_score=skills_match,
            ats_score=ats_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            analysis_results=analysis_results
        )
        
        if application_id:
            print(f"   ✓ Application created: ID {application_id}")
        else:
            print(f"   ⚠️ Application already exists")
            return {'error': 'You have already applied to this job'}
        
        # Update user's resume in database
        self.db.update_user_resume(
            user_id=user_id,
            resume_path=resume_pdf_path,
            resume_text=resume_text,
            skills=matched_skills + missing_skills
        )
        
        result = {
            'application_id': application_id,
            'match_score': overall_match,
            'skills_match_score': skills_match,
            'ats_score': ats_score,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'meets_threshold': overall_match >= job['minimum_score'],
            'recommendation': self._get_recommendation(overall_match, job['minimum_score'])
        }
        
        print(f"\n{'='*80}")
        print(f"APPLICATION COMPLETE")
        print(f"{'='*80}")
        print(f"Match Score: {overall_match}% (Threshold: {job['minimum_score']}%)")
        print(f"Status: {'✅ MEETS THRESHOLD' if result['meets_threshold'] else '❌ BELOW THRESHOLD'}")
        
        return result
    
    def get_ranked_candidates(self, job_id: int, min_score: float = None,
                             limit: int = 50) -> List[Dict]:
        """
        Get ranked candidates for a job posting
        
        Args:
            job_id: Job posting ID
            min_score: Minimum match score (uses job threshold if not provided)
            limit: Maximum number of candidates to return
            
        Returns:
            List of applications ranked by match score (highest first)
        """
        job = self.db.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Use job's minimum score if not specified
        if min_score is None:
            min_score = job['minimum_score']
        
        # Get applications above threshold, ranked by score
        applications = self.db.get_job_applications(
            job_id=job_id,
            min_score=min_score,
            limit=limit
        )
        
        return applications
    
    def get_top_candidates(self, job_id: int, top_n: int = 10) -> List[Dict]:
        """
        Get top N candidates for a job
        
        Args:
            job_id: Job posting ID
            top_n: Number of top candidates to return
            
        Returns:
            List of top N applications
        """
        return self.get_ranked_candidates(job_id, min_score=0, limit=top_n)
    
    def batch_apply(self, user_id: int, job_ids: List[int], 
                   resume_pdf_path: str) -> Dict:
        """
        Apply to multiple jobs at once
        
        Args:
            user_id: User ID
            job_ids: List of job IDs to apply to
            resume_pdf_path: Path to resume PDF
            
        Returns:
            Summary of applications and match scores
        """
        results = {
            'total_jobs': len(job_ids),
            'successful_applications': 0,
            'failed_applications': 0,
            'applications': []
        }
        
        for job_id in job_ids:
            try:
                result = self.process_application(user_id, job_id, resume_pdf_path)
                if 'error' not in result:
                    results['successful_applications'] += 1
                    results['applications'].append({
                        'job_id': job_id,
                        'status': 'success',
                        'match_score': result['match_score'],
                        'meets_threshold': result['meets_threshold']
                    })
                else:
                    results['failed_applications'] += 1
                    results['applications'].append({
                        'job_id': job_id,
                        'status': 'failed',
                        'error': result['error']
                    })
            except Exception as e:
                results['failed_applications'] += 1
                results['applications'].append({
                    'job_id': job_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Rank by match score
        results['applications'].sort(
            key=lambda x: x.get('match_score', 0), 
            reverse=True
        )
        
        return results
    
    def _build_job_description(self, job: Dict) -> str:
        """Build comprehensive job description for matching"""
        parts = [
            f"Job Title: {job['title']}",
            f"\nDescription:\n{job['description']}"
        ]
        
        if job.get('requirements'):
            parts.append(f"\nRequirements:\n{job['requirements']}")
        
        if job.get('location'):
            parts.append(f"\nLocation: {job['location']}")
        
        if job.get('employment_type'):
            parts.append(f"\nEmployment Type: {job['employment_type']}")
        
        return '\n'.join(parts)
    
    def _get_recommendation(self, match_score: float, threshold: float) -> str:
        """Get application recommendation message"""
        if match_score >= 80:
            return "Excellent match! You are a strong candidate for this position."
        elif match_score >= threshold + 10:
            return "Good match! You meet the requirements and should have a good chance."
        elif match_score >= threshold:
            return "You meet the minimum threshold. Consider highlighting relevant experience."
        else:
            return f"Your match score is below the threshold ({threshold}%). Consider building skills in missing areas."


# Example usage
if __name__ == "__main__":
    import sys
    
    # Initialize matching engine
    print("🚀 Initializing Matching Engine...")
    engine = HiringMatchingEngine(use_rag=True, use_llm=True)
    
    # Example: Process application
    if len(sys.argv) >= 4:
        user_id = int(sys.argv[1])
        job_id = int(sys.argv[2])
        resume_path = sys.argv[3]
        
        result = engine.process_application(user_id, job_id, resume_path)
        
        print("\n" + "="*80)
        print("RESULT SUMMARY")
        print("="*80)
        print(f"Application ID: {result.get('application_id')}")
        print(f"Match Score: {result['match_score']}%")
        print(f"Skills Match: {result['skills_match_score']}%")
        print(f"ATS Score: {result['ats_score']}/100")
        print(f"Meets Threshold: {result['meets_threshold']}")
        print(f"\n{result['recommendation']}")
    else:
        print("\nUsage: python matching_engine.py <user_id> <job_id> <resume.pdf>")
        print("\nOr import this module to use in your application")
