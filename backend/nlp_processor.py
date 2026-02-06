"""
NLP Processor for Resume Parsing

Handles text preprocessing, skill extraction, experience detection,
resume-to-job matching, and provides improvement suggestions.
"""

import nltk
import re
from typing import Dict, List, Set

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Initialize NLP components
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Comprehensive skills list organized by category
SKILLS_BY_CATEGORY = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", 
        "rust", "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "bash"
    ],
    "web_technologies": [
        "react", "angular", "vue", "nextjs", "nodejs", "express", "django", "flask", 
        "fastapi", "spring", "rails", "laravel", "asp.net", "html", "css", "sass",
        "tailwind", "bootstrap", "jquery", "webpack", "vite"
    ],
    "databases": [
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "dynamodb", 
        "firebase", "oracle", "sqlite", "cassandra", "neo4j", "mariadb", "supabase"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", 
        "github actions", "ci/cd", "ansible", "puppet", "chef", "nginx", "apache",
        "linux", "unix", "cloudflare", "heroku", "vercel", "netlify"
    ],
    "data_ml": [
        "machine learning", "deep learning", "nlp", "natural language processing", 
        "computer vision", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", 
        "spark", "hadoop", "data analysis", "data science", "neural networks",
        "keras", "opencv", "huggingface", "llm", "ai", "artificial intelligence"
    ],
    "tools_practices": [
        "git", "agile", "scrum", "rest api", "graphql", "microservices", "api design",
        "unit testing", "integration testing", "tdd", "bdd", "jira", "confluence",
        "figma", "postman", "swagger"
    ],
    "soft_skills": [
        "leadership", "communication", "problem solving", "teamwork", "project management",
        "critical thinking", "time management", "creativity", "adaptability", "mentoring"
    ]
}

# Flatten skills list for easy searching
ALL_SKILLS = []
for category_skills in SKILLS_BY_CATEGORY.values():
    ALL_SKILLS.extend(category_skills)

# Patterns for extracting information
EXPERIENCE_PATTERNS = [
    r'(\d+)\s*\+?\s*(years?|yrs?)\s*(of\s*)?(experience|exp)?',
    r'(experience|exp)\s*:?\s*(\d+)\s*(years?|yrs?)',
    r'(\d+)\s*-\s*\d+\s*(years?|yrs?)',
]

EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_PATTERN = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
LINKEDIN_PATTERN = r'linkedin\.com/in/[\w-]+'
GITHUB_PATTERN = r'github\.com/[\w-]+'

# Education keywords
EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "doctorate", "mba", "b.tech", "m.tech", "b.sc", "m.sc",
    "b.e", "m.e", "bca", "mca", "computer science", "engineering", "university", "college",
    "degree", "diploma", "certification", "certified"
]

# Action verbs that make resumes stronger
STRONG_ACTION_VERBS = [
    "achieved", "implemented", "developed", "designed", "led", "managed", "created",
    "improved", "increased", "decreased", "reduced", "optimized", "built", "launched",
    "delivered", "executed", "spearheaded", "orchestrated", "streamlined", "transformed"
]

# Weak words to avoid
WEAK_WORDS = [
    "responsible for", "duties included", "helped", "assisted", "worked on",
    "participated", "was involved", "familiar with", "exposure to"
]


def preprocess_text(text: str) -> List[str]:
    """Preprocess text for NLP analysis."""
    text = text.lower()
    tokens = word_tokenize(text)
    cleaned_tokens = []
    for token in tokens:
        if token.isalnum() and token not in stop_words and len(token) > 1:
            lemmatized = lemmatizer.lemmatize(token)
            cleaned_tokens.append(lemmatized)
    return cleaned_tokens


def extract_skills(text: str, tokens: List[str]) -> Dict[str, List[str]]:
    """Extract skills organized by category."""
    found_skills = {}
    text_lower = text.lower()
    tokens_text = " ".join(tokens)
    
    for category, skills in SKILLS_BY_CATEGORY.items():
        category_skills = []
        for skill in skills:
            if skill in text_lower or skill in tokens_text:
                category_skills.append(skill)
        if category_skills:
            found_skills[category] = category_skills
    
    return found_skills


def extract_experience(text: str) -> str:
    """Extract years of experience from resume text."""
    text_lower = text.lower()
    max_years = 0
    
    for pattern in EXPERIENCE_PATTERNS:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            for group in match:
                if group and group.isdigit():
                    years = int(group)
                    if years <= 50:  # Reasonable experience limit
                        max_years = max(max_years, years)
    
    return str(max_years)


def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information from resume."""
    contact = {}
    
    email_match = re.search(EMAIL_PATTERN, text)
    if email_match:
        contact["email"] = email_match.group()
    
    phone_match = re.search(PHONE_PATTERN, text)
    if phone_match:
        contact["phone"] = phone_match.group()
    
    linkedin_match = re.search(LINKEDIN_PATTERN, text.lower())
    if linkedin_match:
        contact["linkedin"] = linkedin_match.group()
    
    github_match = re.search(GITHUB_PATTERN, text.lower())
    if github_match:
        contact["github"] = github_match.group()
    
    return contact


def analyze_education(text: str) -> Dict:
    """Analyze education section of resume."""
    text_lower = text.lower()
    found_education = []
    
    for keyword in EDUCATION_KEYWORDS:
        if keyword in text_lower:
            found_education.append(keyword)
    
    has_degree = any(word in text_lower for word in ["bachelor", "master", "phd", "degree", "b.tech", "m.tech"])
    
    return {
        "keywords_found": list(set(found_education)),
        "has_degree": has_degree
    }


def analyze_resume_quality(text: str) -> Dict:
    """Analyze the quality of the resume content."""
    text_lower = text.lower()
    sentences = sent_tokenize(text)
    
    # Count action verbs
    action_verb_count = 0
    found_action_verbs = []
    for verb in STRONG_ACTION_VERBS:
        if verb in text_lower:
            action_verb_count += text_lower.count(verb)
            found_action_verbs.append(verb)
    
    # Count weak words
    weak_word_count = 0
    found_weak_words = []
    for word in WEAK_WORDS:
        if word in text_lower:
            weak_word_count += text_lower.count(word)
            found_weak_words.append(word)
    
    # Check for quantifiable achievements
    numbers_pattern = r'\d+%|\$\d+|\d+\s*(users|customers|clients|projects|team|people)'
    quantifiable_achievements = len(re.findall(numbers_pattern, text_lower))
    
    # Word count analysis
    word_count = len(text.split())
    
    return {
        "word_count": word_count,
        "sentence_count": len(sentences),
        "action_verbs_used": found_action_verbs,
        "action_verb_count": action_verb_count,
        "weak_words_found": found_weak_words,
        "weak_word_count": weak_word_count,
        "quantifiable_achievements": quantifiable_achievements,
        "has_sufficient_content": word_count >= 200
    }


def generate_suggestions(
    skills_by_category: Dict,
    quality_analysis: Dict,
    education: Dict,
    experience_years: str,
    match_score: float = 0,
    job_desc: str = ""
) -> List[Dict]:
    """Generate actionable suggestions to improve the resume."""
    suggestions = []
    
    # Flatten skills for counting
    all_found_skills = []
    for skills in skills_by_category.values():
        all_found_skills.extend(skills)
    
    # Skill-related suggestions
    if len(all_found_skills) < 5:
        suggestions.append({
            "category": "Skills",
            "priority": "high",
            "title": "Add More Technical Skills",
            "description": f"Your resume only mentions {len(all_found_skills)} skills. Aim for 8-12 relevant skills to improve visibility.",
            "impact": "+10-15% match score"
        })
    
    if "cloud_devops" not in skills_by_category:
        suggestions.append({
            "category": "Skills",
            "priority": "medium",
            "title": "Add Cloud/DevOps Skills",
            "description": "Consider adding cloud platforms (AWS, Azure, GCP) or DevOps tools (Docker, Kubernetes) if you have experience with them.",
            "impact": "+5-10% match score"
        })
    
    # Quality-related suggestions
    if quality_analysis["weak_word_count"] > 0:
        suggestions.append({
            "category": "Language",
            "priority": "high",
            "title": "Replace Weak Phrases",
            "description": f"Found weak phrases: {', '.join(quality_analysis['weak_words_found'][:3])}. Replace with strong action verbs like 'achieved', 'implemented', 'led'.",
            "impact": "+5-8% readability"
        })
    
    if quality_analysis["action_verb_count"] < 5:
        suggestions.append({
            "category": "Language",
            "priority": "medium",
            "title": "Use More Action Verbs",
            "description": "Start bullet points with strong action verbs: 'Developed', 'Implemented', 'Optimized', 'Streamlined', 'Delivered'.",
            "impact": "+5% impact"
        })
    
    if quality_analysis["quantifiable_achievements"] < 3:
        suggestions.append({
            "category": "Achievements",
            "priority": "high",
            "title": "Add Quantifiable Results",
            "description": "Include numbers and metrics: 'Increased performance by 40%', 'Managed team of 5', 'Reduced costs by $10K'.",
            "impact": "+10-20% credibility"
        })
    
    if not quality_analysis["has_sufficient_content"]:
        suggestions.append({
            "category": "Content",
            "priority": "high",
            "title": "Expand Resume Content",
            "description": f"Your resume has only {quality_analysis['word_count']} words. Aim for 400-600 words with detailed descriptions.",
            "impact": "+15% completeness"
        })
    
    # Education suggestions
    if not education["has_degree"]:
        suggestions.append({
            "category": "Education",
            "priority": "medium",
            "title": "Highlight Education",
            "description": "Ensure your education section clearly states your degree, major, and institution.",
            "impact": "+3-5% completeness"
        })
    
    # Job matching suggestions
    if job_desc and match_score < 70:
        job_tokens = set(preprocess_text(job_desc))
        resume_tokens = set(preprocess_text(" ".join(all_found_skills)))
        missing_keywords = job_tokens - resume_tokens
        
        # Filter to get meaningful missing keywords
        meaningful_missing = [kw for kw in list(missing_keywords)[:5] if len(kw) > 3]
        
        if meaningful_missing:
            suggestions.append({
                "category": "Job Match",
                "priority": "high",
                "title": "Add Missing Keywords",
                "description": f"Consider adding these keywords from the job description: {', '.join(meaningful_missing)}",
                "impact": f"+{min(len(meaningful_missing) * 3, 15)}% match score"
            })
    
    # Professional profile suggestions
    suggestions.append({
        "category": "Format",
        "priority": "low",
        "title": "Add Professional Summary",
        "description": "Start with a 2-3 sentence summary highlighting your experience level, key skills, and career goals.",
        "impact": "+5% first impression"
    })
    
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: priority_order.get(x["priority"], 3))
    
    return suggestions[:8]  # Return top 8 suggestions


def calculate_resume_score(
    skills_by_category: Dict,
    quality_analysis: Dict,
    education: Dict,
    experience_years: str
) -> int:
    """Calculate an overall resume quality score out of 100."""
    score = 0
    
    # Skills score (max 30 points)
    all_skills = []
    for skills in skills_by_category.values():
        all_skills.extend(skills)
    skill_count = len(all_skills)
    score += min(skill_count * 3, 30)
    
    # Content quality (max 25 points)
    if quality_analysis["has_sufficient_content"]:
        score += 10
    score += min(quality_analysis["action_verb_count"] * 2, 10)
    score += min(quality_analysis["quantifiable_achievements"] * 2, 5)
    
    # Penalty for weak words
    score -= min(quality_analysis["weak_word_count"] * 2, 10)
    
    # Experience score (max 20 points)
    years = int(experience_years)
    if years >= 5:
        score += 20
    elif years >= 3:
        score += 15
    elif years >= 1:
        score += 10
    else:
        score += 5
    
    # Education score (max 15 points)
    if education["has_degree"]:
        score += 15
    elif len(education["keywords_found"]) > 0:
        score += 8
    
    # Category diversity bonus (max 10 points)
    score += min(len(skills_by_category) * 2, 10)
    
    return max(0, min(100, score))


def extract_keywords(text: str) -> Dict:
    """Main extraction function - extracts all relevant data from resume."""
    tokens = preprocess_text(text)
    
    # Extract various components
    skills_by_category = extract_skills(text, tokens)
    experience = extract_experience(text)
    contact = extract_contact_info(text)
    education = analyze_education(text)
    quality = analyze_resume_quality(text)
    
    # Flatten skills for backward compatibility
    all_skills = []
    for skills in skills_by_category.values():
        all_skills.extend(skills)
    
    # Calculate resume score
    resume_score = calculate_resume_score(skills_by_category, quality, education, experience)
    
    # Generate suggestions
    suggestions = generate_suggestions(
        skills_by_category, quality, education, experience
    )
    
    return {
        "skills": all_skills,
        "skills_by_category": skills_by_category,
        "experience_years": experience,
        "keywords": list(set(tokens[:50])),
        "contact": contact,
        "education": education,
        "quality_analysis": quality,
        "resume_score": resume_score,
        "suggestions": suggestions,
        "word_count": quality["word_count"]
    }


def match_resume(resume_data: Dict, job_desc: str) -> float:
    """Calculate match score between resume and job description."""
    job_tokens = set(preprocess_text(job_desc))
    
    if not job_tokens:
        return 0.0
    
    # Get resume tokens
    resume_tokens = set(resume_data.get("keywords", []))
    resume_skills = set(skill.lower() for skill in resume_data.get("skills", []))
    
    # Combine resume tokens with skills
    all_resume_terms = resume_tokens.union(resume_skills)
    
    # Calculate intersection
    matching_terms = job_tokens.intersection(all_resume_terms)
    
    # Calculate match percentage
    match_percentage = (len(matching_terms) / len(job_tokens)) * 100
    
    # Bonus points for skill matches (skills are weighted higher)
    job_text_lower = job_desc.lower()
    skill_matches = sum(1 for skill in resume_data.get("skills", []) if skill in job_text_lower)
    skill_bonus = min(skill_matches * 5, 25)
    
    # Category match bonus
    skills_by_category = resume_data.get("skills_by_category", {})
    category_bonus = len(skills_by_category) * 2
    
    final_score = min(match_percentage + skill_bonus + category_bonus, 100)
    
    # Update suggestions with job-specific recommendations
    if "suggestions" in resume_data:
        job_suggestions = generate_suggestions(
            skills_by_category,
            resume_data.get("quality_analysis", {}),
            resume_data.get("education", {}),
            resume_data.get("experience_years", "0"),
            final_score,
            job_desc
        )
        resume_data["suggestions"] = job_suggestions
    
    return round(final_score, 2)
