"""
RAG-based Skills Extraction Module
Uses embeddings and vector similarity to extract skills from resumes and job descriptions
Loads skills from the provided CSV dataset
"""

import json
import pickle
import numpy as np
import pandas as pd
from typing import List, Dict, Set, Tuple
from pathlib import Path
import re
from tqdm import tqdm


class RAGSkillsExtractor:
    """Extract skills using RAG (Retrieval-Augmented Generation) with CSV dataset"""
    
    def __init__(
        self, 
        skills_csv_path: str = r'C:\Users\Admin\Documents\ATS-agent\data\skills_exploded (2).csv',
        embedding_model: str = 'all-MiniLM-L6-v2',
        max_skills: int = None
    ):
        """
        Initialize RAG skills extractor
        
        Args:
            skills_csv_path: Path to CSV file containing skills
            embedding_model: Name of the sentence transformer model to use
            max_skills: Maximum number of skills to load (None = all). Use smaller number for faster loading.
        """
        self.skills_csv_path = skills_csv_path
        self.embedding_model_name = embedding_model
        self.max_skills = max_skills
        self.model = None
        self.skills_list = None
        self.skill_embeddings = None
        
        # Cache file based on max_skills setting
        cache_suffix = f'_{max_skills}' if max_skills else '_full'
        self.embeddings_cache_path = Path(f'skills_embeddings_csv{cache_suffix}.pkl')
        
        self._initialize_model()
        self._load_skills_from_csv()
        self._load_or_create_embeddings()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            print(f"Loading embedding model: {self.embedding_model_name}...")
            self.model = SentenceTransformer(self.embedding_model_name)
            print("✓ Model loaded successfully")
        except ImportError:
            print("ERROR: sentence-transformers not installed.")
            print("Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def _load_skills_from_csv(self):
        """Load skills from CSV file"""
        print(f"Loading skills from CSV: {self.skills_csv_path}")
        
        try:
            # Read CSV file
            if self.max_skills:
                df = pd.read_csv(self.skills_csv_path, nrows=self.max_skills)
                print(f"✓ Loaded {len(df)} skills (limited to {self.max_skills})")
            else:
                df = pd.read_csv(self.skills_csv_path)
                print(f"✓ Loaded {len(df)} skills from CSV")
            
            # Get unique skills and clean them
            skills = df.iloc[:, 0].dropna().unique().tolist()
            
            # Clean skills: remove very short ones, strip whitespace
            cleaned_skills = []
            for skill in skills:
                skill_str = str(skill).strip()
                # Keep skills that are at least 2 characters and not purely numeric
                if len(skill_str) >= 2 and not skill_str.isdigit():
                    cleaned_skills.append(skill_str)
            
            self.skills_list = cleaned_skills
            print(f"✓ {len(self.skills_list)} unique skills after cleaning")
            
        except Exception as e:
            print(f"Error loading CSV: {e}")
            raise
    
    def _load_or_create_embeddings(self):
        """Load existing embeddings or create new ones"""
        if self.embeddings_cache_path.exists():
            print(f"Loading cached skill embeddings from {self.embeddings_cache_path}...")
            try:
                with open(self.embeddings_cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                    self.skill_embeddings = cache_data['embeddings']
                    cached_skills = cache_data['skills']
                    
                    # Verify cache matches current skills
                    if cached_skills == self.skills_list:
                        print(f"✓ Loaded embeddings for {len(self.skills_list)} skills from cache")
                        return
                    else:
                        print("⚠ Cache doesn't match current skills, regenerating...")
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
        
        print("Creating skill embeddings (this may take a while)...")
        self._create_embeddings()
        self._save_embeddings()
    
    def _create_embeddings(self):
        """Create embeddings for all skills"""
        print(f"Encoding {len(self.skills_list)} skills...")
        
        # Batch encoding for efficiency
        batch_size = 1000
        embeddings_list = []
        
        for i in tqdm(range(0, len(self.skills_list), batch_size), desc="Encoding skills"):
            batch = self.skills_list[i:i+batch_size]
            batch_embeddings = self.model.encode(batch, show_progress_bar=False)
            embeddings_list.append(batch_embeddings)
        
        self.skill_embeddings = np.vstack(embeddings_list)
        print(f"✓ Created embeddings with shape: {self.skill_embeddings.shape}")
    
    def _save_embeddings(self):
        """Save embeddings to cache file"""
        try:
            cache_data = {
                'skills': self.skills_list,
                'embeddings': self.skill_embeddings
            }
            with open(self.embeddings_cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            print(f"✓ Saved embeddings to {self.embeddings_cache_path}")
        except Exception as e:
            print(f"Warning: Could not save embeddings cache: {e}")
    
    def _extract_ngrams(self, text: str, n_range: Tuple[int, int] = (1, 5)) -> List[str]:
        """
        Extract n-grams from text
        
        Args:
            text: Input text
            n_range: Tuple of (min_n, max_n) for n-gram extraction
            
        Returns:
            List of n-grams
        """
        # Clean and tokenize, preserve important characters
        text = re.sub(r'[^\w\s\.\-\+\#\(\)\/\&]', ' ', text)
        words = text.split()
        
        ngrams = []
        for n in range(n_range[0], n_range[1] + 1):
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                if len(ngram) > 1:  # Filter very short n-grams
                    ngrams.append(ngram)
        
        return ngrams
    
    def extract_skills_rag(
        self, 
        text: str, 
        threshold: float = 0.6,
        top_k: int = None,
        return_scores: bool = False
    ) -> List[str] | List[Tuple[str, float]]:
        """
        Extract skills using RAG approach with semantic similarity
        
        Args:
            text: Input text (resume or job description)
            threshold: Minimum similarity threshold (0-1). Higher = stricter matching
            top_k: If set, return only top k matches regardless of threshold
            return_scores: If True, return (skill, score) tuples
            
        Returns:
            List of detected skills or list of (skill, score) tuples
        """
        # Extract n-grams from text
        ngrams = self._extract_ngrams(text)
        
        if not ngrams:
            return [] if not return_scores else []
        
        # Encode all n-grams
        print(f"Encoding {len(ngrams)} text segments...")
        ngram_embeddings = self.model.encode(ngrams, show_progress_bar=False)
        
        # Calculate similarity between each n-gram and all skills
        from sklearn.metrics.pairwise import cosine_similarity
        
        print("Computing similarity scores...")
        # Compute similarity matrix (ngrams x skills)
        similarities = cosine_similarity(ngram_embeddings, self.skill_embeddings)
        
        # For each skill, get the maximum similarity with any n-gram
        max_similarities = np.max(similarities, axis=0)
        
        # Get skills above threshold
        detected_skills = []
        for idx, score in enumerate(max_similarities):
            if score >= threshold:
                skill = self.skills_list[idx]
                detected_skills.append((skill, float(score)))
        
        # Sort by score
        detected_skills.sort(key=lambda x: x[1], reverse=True)
        
        # Apply top_k if specified
        if top_k:
            detected_skills = detected_skills[:top_k]
        
        print(f"✓ Found {len(detected_skills)} skills above threshold {threshold}")
        
        if return_scores:
            return detected_skills
        else:
            return [skill for skill, _ in detected_skills]
    
    def compare_skills(
        self, 
        resume_text: str, 
        job_desc_text: str,
        threshold: float = 0.6
    ) -> Dict:
        """
        Compare skills from resume and job description
        
        Args:
            resume_text: Resume text
            job_desc_text: Job description text
            threshold: Minimum similarity threshold
            
        Returns:
            Dictionary with matched, missing, and additional skills
        """
        print("\n" + "="*80)
        print("EXTRACTING SKILLS FROM RESUME")
        print("="*80)
        resume_skills = set(self.extract_skills_rag(resume_text, threshold=threshold))
        
        print("\n" + "="*80)
        print("EXTRACTING SKILLS FROM JOB DESCRIPTION")
        print("="*80)
        job_skills = set(self.extract_skills_rag(job_desc_text, threshold=threshold))
        
        matched = resume_skills & job_skills
        missing = job_skills - resume_skills
        additional = resume_skills - job_skills
        
        return {
            'matched_skills': sorted(list(matched)),
            'missing_skills': sorted(list(missing)),
            'additional_skills': sorted(list(additional)),
            'match_percentage': len(matched) / len(job_skills) * 100 if job_skills else 0,
            'resume_skill_count': len(resume_skills),
            'job_skill_count': len(job_skills)
        }
    
    def get_skill_recommendations(
        self, 
        current_skills: List[str], 
        target_role: str,
        top_n: int = 10,
        threshold: float = 0.6
    ) -> List[Tuple[str, float]]:
        """
        Get recommended skills based on current skills and target role
        
        Args:
            current_skills: List of current skills
            target_role: Target job role or description
            top_n: Number of recommendations to return
            threshold: Minimum relevance threshold
            
        Returns:
            List of (skill, relevance_score) tuples
        """
        # Extract skills from target role
        target_skills = set(self.extract_skills_rag(target_role, threshold=threshold))
        
        # Skills that are in target but not in current
        recommended = target_skills - set(current_skills)
        
        # Encode target role
        role_embedding = self.model.encode([target_role])[0]
        
        # Calculate similarity between role and recommended skills
        from sklearn.metrics.pairwise import cosine_similarity
        
        recommendations = []
        for skill in recommended:
            skill_idx = self.skills_list.index(skill) if skill in self.skills_list else None
            if skill_idx is not None:
                skill_embedding = self.skill_embeddings[skill_idx]
                relevance = cosine_similarity([role_embedding], [skill_embedding])[0][0]
                recommendations.append((skill, float(relevance)))
        
        # Sort by relevance and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_n]


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RAG-based Skills Extractor using CSV dataset')
    parser.add_argument('--max-skills', type=int, default=50000, 
                       help='Maximum number of skills to load (default: 50000, use None for all)')
    parser.add_argument('--threshold', type=float, default=0.6,
                       help='Similarity threshold 0-1 (default: 0.6)')
    parser.add_argument('--test', action='store_true',
                       help='Run test with sample text')
    
    args = parser.parse_args()
    
    print("="*80)
    print("RAG SKILLS EXTRACTOR - CSV DATASET")
    print("="*80)
    
    # Initialize extractor
    extractor = RAGSkillsExtractor(max_skills=args.max_skills)
    
    if args.test:
        # Example resume text
        resume_text = """
        Senior Software Engineer with 5 years of experience in Python and JavaScript.
        Proficient in React, Django, and PostgreSQL. Experience with AWS and Docker.
        Strong background in machine learning and data analysis using pandas and scikit-learn.
        Led cross-functional teams in agile environment. Bachelor's degree in Computer Science.
        """
        
        # Example job description
        job_desc = """
        Looking for a Full Stack Developer with expertise in React, Node.js, and MongoDB.
        Experience with cloud platforms (AWS or Azure) required.
        Knowledge of Docker and Kubernetes is a plus.
        Strong problem-solving skills and ability to work in agile teams.
        Bachelor's degree in Computer Science or related field required.
        """
        
        print("\n" + "="*80)
        print("TEST: EXTRACTING SKILLS FROM RESUME")
        print("="*80)
        
        resume_skills = extractor.extract_skills_rag(
            resume_text, 
            threshold=args.threshold, 
            return_scores=True
        )
        print(f"\nFound {len(resume_skills)} skills:\n")
        for skill, score in resume_skills[:20]:
            print(f"  • {skill:50} (score: {score:.3f})")
        if len(resume_skills) > 20:
            print(f"\n  ... and {len(resume_skills) - 20} more skills")
        
        print("\n" + "="*80)
        print("TEST: COMPARING RESUME WITH JOB DESCRIPTION")
        print("="*80)
        
        comparison = extractor.compare_skills(resume_text, job_desc, threshold=args.threshold)
        
        print(f"\n✓ Matched Skills ({len(comparison['matched_skills'])}):")
        for skill in comparison['matched_skills']:
            print(f"  • {skill}")
        
        print(f"\n✗ Missing Skills ({len(comparison['missing_skills'])}):")
        for skill in comparison['missing_skills']:
            print(f"  • {skill}")
        
        print(f"\n📊 Match Percentage: {comparison['match_percentage']:.1f}%")
        
        print("\n" + "="*80)
        print("TEST: SKILL RECOMMENDATIONS")
        print("="*80)
        
        current_skills = [skill for skill, _ in resume_skills]
        recommendations = extractor.get_skill_recommendations(
            current_skills, 
            job_desc, 
            top_n=10,
            threshold=args.threshold
        )
        
        print("\nTop 10 recommended skills to learn:\n")
        for skill, score in recommendations:
            print(f"  • {skill:50} (relevance: {score:.3f})")
    
    print("\n" + "="*80)
    print("✓ Extractor ready for use!")
    print("="*80)


if __name__ == "__main__":
    main()
