"""
Job Role Prediction Module
Predicts the most suitable job role based on resume skills using LSTM model
"""

import numpy as np
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import sequence
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os


class JobRolePredictor:
    """Predicts job roles from resume skills using trained LSTM model"""
    
    def __init__(self, model_path='JobPrediction_Model'):
        """
        Initialize the job role predictor
        
        Args:
            model_path: Path to directory containing model files
        """
        self.model_path = model_path
        self.max_review_length = 200
        
        # Download NLTK data if needed
        try:
            stopwords.words('english')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)
        
        self.stopwords = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Load model and preprocessing tools
        self._load_model()
        self._load_tokenizer()
        self._load_label_encoder()
    
    def _load_model(self):
        """Load the trained LSTM model"""
        model_file = os.path.join(self.model_path, 'job_prediction_bilstm.h5')
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"Model file not found: {model_file}")
        
        self.model = load_model(model_file)
        print(f"✅ Loaded job prediction model from {model_file}")
    
    def _load_tokenizer(self):
        """Load the tokenizer"""
        tokenizer_file = os.path.join(self.model_path, 'tokenizer.pkl')
        if not os.path.exists(tokenizer_file):
            raise FileNotFoundError(f"Tokenizer file not found: {tokenizer_file}")
        
        with open(tokenizer_file, 'rb') as f:
            self.tokenizer = pickle.load(f)
        print(f"✅ Loaded tokenizer from {tokenizer_file}")
    
    def _load_label_encoder(self):
        """Load the label encoder"""
        encoder_file = os.path.join(self.model_path, 'label_encoder.pkl')
        if not os.path.exists(encoder_file):
            raise FileNotFoundError(f"Label encoder file not found: {encoder_file}")
        
        with open(encoder_file, 'rb') as f:
            self.label_encoder = pickle.load(f)
        
        # Get job role names
        self.job_roles = self.label_encoder.classes_.tolist()
        print(f"✅ Loaded label encoder with {len(self.job_roles)} job roles")
        print(f"   Job roles: {', '.join(self.job_roles)}")
    
    def _preprocess_text(self, text):
        """
        Preprocess text: remove stopwords and lemmatize
        
        Args:
            text: Input text (skills, education, etc.)
            
        Returns:
            Preprocessed text string
        """
        # Convert to lowercase and split
        words = text.lower().split()
        
        # Remove stopwords
        words = [word for word in words if word not in self.stopwords]
        
        # Lemmatize
        words = [self.lemmatizer.lemmatize(word) for word in words]
        
        return ' '.join(words)
    
    def predict_job_role(self, skills_text, top_n=3):
        """
        Predict job role from skills text
        
        Args:
            skills_text: String containing skills (comma-separated or space-separated)
            top_n: Number of top predictions to return
            
        Returns:
            Dictionary with:
                - predicted_role: Most likely job role
                - confidence: Confidence score (0-1)
                - top_predictions: List of (role, probability) tuples
                - all_probabilities: Dictionary of all role probabilities
        """
        # Preprocess the text
        processed_text = self._preprocess_text(skills_text)
        
        # Tokenize and pad
        sequence_data = self.tokenizer.texts_to_sequences([processed_text])
        padded_data = sequence.pad_sequences(sequence_data, maxlen=self.max_review_length)
        
        # Predict
        predictions = self.model.predict(padded_data, verbose=0)
        probabilities = predictions[0]
        
        # Get top N predictions
        top_indices = np.argsort(probabilities)[-top_n:][::-1]
        top_predictions = [
            (self.job_roles[idx], float(probabilities[idx]))
            for idx in top_indices
        ]
        
        # Best prediction
        best_idx = np.argmax(probabilities)
        predicted_role = self.job_roles[best_idx]
        confidence = float(probabilities[best_idx])
        
        # All probabilities
        all_probs = {
            role: float(prob)
            for role, prob in zip(self.job_roles, probabilities)
        }
        
        return {
            'predicted_role': predicted_role,
            'confidence': confidence,
            'top_predictions': top_predictions,
            'all_probabilities': all_probs
        }
    
    def predict_from_resume_data(self, resume_skills, education=None, organizations=None, top_n=3):
        """
        Predict job role from resume components
        
        Args:
            resume_skills: List or string of skills
            education: Optional list or string of education info
            organizations: Optional list or string of organizations
            top_n: Number of top predictions to return
            
        Returns:
            Dictionary with prediction results
        """
        # Combine all information
        text_parts = []
        
        # Add skills
        if isinstance(resume_skills, list):
            text_parts.append(' '.join(resume_skills))
        else:
            text_parts.append(str(resume_skills))
        
        # Add education if provided
        if education:
            if isinstance(education, list):
                text_parts.append(' '.join(education))
            else:
                text_parts.append(str(education))
        
        # Add organizations if provided
        if organizations:
            if isinstance(organizations, list):
                text_parts.append(' '.join(organizations))
            else:
                text_parts.append(str(organizations))
        
        combined_text = ' '.join(text_parts)
        
        return self.predict_job_role(combined_text, top_n=top_n)
    
    def get_job_roles(self):
        """Get list of all possible job roles"""
        return self.job_roles.copy()


def main():
    """Test the job role predictor"""
    print("=" * 80)
    print("JOB ROLE PREDICTOR - TEST")
    print("=" * 80)
    
    # Initialize predictor
    predictor = JobRolePredictor()
    
    print("\n" + "=" * 80)
    print("TEST PREDICTIONS")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            'name': 'Machine Learning Engineer',
            'skills': 'Python, TensorFlow, Keras, Machine Learning, Deep Learning, Neural Networks, PyTorch, Scikit-learn, Pandas, NumPy'
        },
        {
            'name': 'Data Science',
            'skills': 'Python, R, SQL, Data Analysis, Statistics, Machine Learning, Pandas, NumPy, Matplotlib, Jupyter'
        },
        {
            'name': 'DevOps Engineer',
            'skills': 'Docker, Kubernetes, AWS, CI/CD, Jenkins, Terraform, Linux, Git, Python, Ansible'
        },
        {
            'name': 'Software Engineer',
            'skills': 'Java, Python, JavaScript, Git, SQL, REST API, Spring Boot, React, Node.js, Agile'
        },
        {
            'name': 'Cyber Security',
            'skills': 'Network Security, Penetration Testing, SIEM, Firewall, Encryption, Security Auditing, Python, Wireshark'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        print(f"Skills: {test_case['skills']}")
        
        result = predictor.predict_job_role(test_case['skills'], top_n=3)
        
        print(f"\n🎯 Predicted Role: {result['predicted_role']}")
        print(f"   Confidence: {result['confidence']:.1%}")
        
        print(f"\n📊 Top 3 Predictions:")
        for i, (role, prob) in enumerate(result['top_predictions'], 1):
            print(f"   {i}. {role:30s} {prob:.1%}")
        
        print("-" * 80)


if __name__ == "__main__":
    main()
