"""
Hiring Platform Database Models
SQLite database for job postings, applications, and user management
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import hashlib


class HiringPlatformDB:
    """Database manager for the hiring platform"""
    
    def __init__(self, db_path: str = "hiring_platform.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table (applicants)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                resume_path TEXT,
                resume_text TEXT,
                skills_extracted TEXT,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Employers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                employer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                company_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Job postings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                requirements TEXT,
                location TEXT,
                salary_range TEXT,
                employment_type TEXT,  -- Full-time, Part-time, Contract
                required_skills TEXT,  -- JSON array
                minimum_score REAL DEFAULT 50.0,  -- Minimum match score to show
                status TEXT DEFAULT 'active',  -- active, closed, draft
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closes_at TIMESTAMP,
                FOREIGN KEY (employer_id) REFERENCES employers(employer_id)
            )
        """)
        
        # Applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                application_id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                match_score REAL NOT NULL,
                skills_match_score REAL,
                ats_score REAL,
                matched_skills TEXT,  -- JSON array
                missing_skills TEXT,  -- JSON array
                analysis_results TEXT,  -- Full JSON analysis
                status TEXT DEFAULT 'pending',  -- pending, reviewed, shortlisted, rejected, interviewed, hired
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                notes TEXT,  -- Employer notes
                FOREIGN KEY (job_id) REFERENCES jobs(job_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                UNIQUE(job_id, user_id)  -- One application per user per job
            )
        """)
        
        # Indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_employer ON jobs(employer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_score ON applications(match_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status)")
        
        conn.commit()
        conn.close()
    
    # ==================== USER MANAGEMENT ====================
    
    def create_user(self, email: str, name: str, resume_path: str = None, 
                   resume_text: str = None, skills: List[str] = None) -> int:
        """Create a new user/applicant"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (email, name, resume_path, resume_text, skills_extracted)
            VALUES (?, ?, ?, ?, ?)
        """, (email, name, resume_path, resume_text, json.dumps(skills) if skills else None))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = dict(row)
            if user['skills_extracted']:
                user['skills_extracted'] = json.loads(user['skills_extracted'])
            return user
        return None
    
    def update_user_resume(self, user_id: int, resume_path: str, 
                          resume_text: str, skills: List[str]):
        """Update user's resume and extracted skills"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET resume_path = ?, resume_text = ?, skills_extracted = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (resume_path, resume_text, json.dumps(skills), user_id))
        
        conn.commit()
        conn.close()
    
    # ==================== EMPLOYER MANAGEMENT ====================
    
    def create_employer(self, email: str, company_name: str) -> int:
        """Create a new employer account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO employers (email, company_name)
            VALUES (?, ?)
        """, (email, company_name))
        
        employer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return employer_id
    
    def get_employer(self, employer_id: int) -> Optional[Dict]:
        """Get employer by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM employers WHERE employer_id = ?", (employer_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    # ==================== JOB MANAGEMENT ====================
    
    def create_job(self, employer_id: int, title: str, description: str,
                   requirements: str = None, location: str = None,
                   salary_range: str = None, employment_type: str = "Full-time",
                   minimum_score: float = 50.0) -> int:
        """Create a new job posting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO jobs (employer_id, title, description, requirements, 
                            location, salary_range, employment_type, minimum_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (employer_id, title, description, requirements, location, 
              salary_range, employment_type, minimum_score))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get job by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            job = dict(row)
            if job['required_skills']:
                job['required_skills'] = json.loads(job['required_skills'])
            return job
        return None
    
    def get_employer_jobs(self, employer_id: int, status: str = None) -> List[Dict]:
        """Get all jobs for an employer"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE employer_id = ? AND status = ?
                ORDER BY posted_at DESC
            """, (employer_id, status))
        else:
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE employer_id = ?
                ORDER BY posted_at DESC
            """, (employer_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            job = dict(row)
            if job['required_skills']:
                job['required_skills'] = json.loads(job['required_skills'])
            jobs.append(job)
        
        return jobs
    
    def get_active_jobs(self, limit: int = 100) -> List[Dict]:
        """Get all active job postings"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM jobs 
            WHERE status = 'active'
            ORDER BY posted_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_job_status(self, job_id: int, status: str):
        """Update job status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE jobs SET status = ? WHERE job_id = ?", (status, job_id))
        
        conn.commit()
        conn.close()
    
    # ==================== APPLICATION MANAGEMENT ====================
    
    def create_application(self, job_id: int, user_id: int, match_score: float,
                          skills_match_score: float, ats_score: float,
                          matched_skills: List[str], missing_skills: List[str],
                          analysis_results: Dict) -> int:
        """Create a new application"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO applications (job_id, user_id, match_score, skills_match_score,
                                        ats_score, matched_skills, missing_skills, analysis_results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (job_id, user_id, match_score, skills_match_score, ats_score,
                  json.dumps(matched_skills), json.dumps(missing_skills), 
                  json.dumps(analysis_results)))
            
            application_id = cursor.lastrowid
            conn.commit()
            return application_id
        except sqlite3.IntegrityError:
            # Application already exists
            return None
        finally:
            conn.close()
    
    def get_application(self, application_id: int) -> Optional[Dict]:
        """Get application by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM applications WHERE application_id = ?", (application_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            app = dict(row)
            app['matched_skills'] = json.loads(app['matched_skills'])
            app['missing_skills'] = json.loads(app['missing_skills'])
            app['analysis_results'] = json.loads(app['analysis_results'])
            return app
        return None
    
    def get_job_applications(self, job_id: int, min_score: float = None,
                            status: str = None, limit: int = 100) -> List[Dict]:
        """
        Get all applications for a job, ranked by match score
        Only returns applications above minimum score threshold
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT a.*, u.name, u.email, u.resume_path
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.job_id = ?
        """
        params = [job_id]
        
        if min_score is not None:
            query += " AND a.match_score >= ?"
            params.append(min_score)
        
        if status:
            query += " AND a.status = ?"
            params.append(status)
        
        query += " ORDER BY a.match_score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        applications = []
        for row in rows:
            app = dict(row)
            app['matched_skills'] = json.loads(app['matched_skills'])
            app['missing_skills'] = json.loads(app['missing_skills'])
            app['analysis_results'] = json.loads(app['analysis_results'])
            applications.append(app)
        
        return applications
    
    def get_user_applications(self, user_id: int) -> List[Dict]:
        """Get all applications for a user"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.*, j.title, j.location, e.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN employers e ON j.employer_id = e.employer_id
            WHERE a.user_id = ?
            ORDER BY a.applied_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def update_application_status(self, application_id: int, status: str, notes: str = None):
        """Update application status (by employer)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE applications 
            SET status = ?, notes = ?, reviewed_at = CURRENT_TIMESTAMP
            WHERE application_id = ?
        """, (status, notes, application_id))
        
        conn.commit()
        conn.close()
    
    # ==================== STATISTICS ====================
    
    def get_job_statistics(self, job_id: int) -> Dict:
        """Get statistics for a job posting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total applications
        cursor.execute("SELECT COUNT(*) FROM applications WHERE job_id = ?", (job_id,))
        total_applications = cursor.fetchone()[0]
        
        # Average match score
        cursor.execute("SELECT AVG(match_score) FROM applications WHERE job_id = ?", (job_id,))
        avg_score = cursor.fetchone()[0] or 0
        
        # Applications by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM applications
            WHERE job_id = ?
            GROUP BY status
        """, (job_id,))
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Top score
        cursor.execute("SELECT MAX(match_score) FROM applications WHERE job_id = ?", (job_id,))
        top_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_applications': total_applications,
            'average_match_score': round(avg_score, 2),
            'top_match_score': round(top_score, 2),
            'status_breakdown': status_counts
        }


# Example usage
if __name__ == "__main__":
    db = HiringPlatformDB()
    
    # Create sample employer
    employer_id = db.create_employer("hr@techcorp.com", "TechCorp Inc.")
    print(f"Created employer: {employer_id}")
    
    # Create sample job
    job_id = db.create_job(
        employer_id=employer_id,
        title="Senior Data Scientist",
        description="Looking for an experienced data scientist...",
        requirements="5+ years experience, Python, Machine Learning, SQL",
        location="San Francisco, CA",
        salary_range="$120k - $180k",
        minimum_score=65.0
    )
    print(f"Created job: {job_id}")
    
    # Create sample user
    user_id = db.create_user(
        email="john@example.com",
        name="John Doe",
        skills=["Python", "Machine Learning", "SQL", "TensorFlow"]
    )
    print(f"Created user: {user_id}")
    
    print("\n✅ Database initialized successfully!")
