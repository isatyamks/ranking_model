import io
import json
import re
import requests
import string
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from src.stopwords import remove_stopwords
from dotenv import load_dotenv
import os
from dotenv import load_dotenv

load_dotenv()

def compute_match_score(job_description, resume_text):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([job_description, resume_text])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round(similarity, 4)  

def get_location_score(job_location, candidate_location):
    return 1.0 if job_location in candidate_location else 0.5 

def get_salary_score(expected_salary, offered_salary=800000):
    if expected_salary <= offered_salary:
        return 1.0  
    elif expected_salary <= offered_salary * 1.2:
        return 0.8 
    else:
        return 0.5 


load_dotenv()
api_key = os.getenv('API_KEY')
client = Groq(api_key=api_key)

stopwords_file = 'src/stopwords.txt'


nltk.download('punkt_tab')

app = Flask(__name__)


@app.route('/',methods = ['GET'])
def hello():
    return "Hello"

@app.route('/extract', methods=['POST'])
def extraction():
    try:
        data = request.get_json()
        pdf_url = data.get("pdf_url")

        if not pdf_url:
            return jsonify({"error": "PDF URL is missing"}), 400

        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        text = ''
        for page in reader.pages:
            text += page.extraction() or ''

        job_description = text.strip()

        results = []
        results.append({
            "jobs": job_description
        })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500





@app.route('/rank', methods=['POST'])
def rank_candidates():
    try:
        data = request.get_json()

        employers = data.get("employers", [])
        candidates = data.get("candidates", [])

        if not employers or not candidates:
            return jsonify({"error": "Employers or candidates data is missing"}), 400

        results = []

        for employer in employers:
            employer_id = employer.get("employer_id")
            job_description = employer.get("job_description")
            #model enhancement work
            job_description = remove_stopwords(job_description,stopwords_file)

            


            #----------------------------------------------------------------------------------------->
            candidate_scores = []

            for candidate in candidates:
                user_id = candidate.get("user_id")
                resume_text = candidate.get("resume_text")
                # #model enhancement work ---------------------------------------------------------------->
                resume_text = remove_stopwords(resume_text,stopwords_file)

                #----------------------------------------------------------------------------------------->
                vectorizer = TfidfVectorizer().fit_transform([job_description, resume_text])
                vectors = vectorizer.toarray()
                cosine_sim = cosine_similarity(vectors)
                score = cosine_sim[0][1]

                candidate_scores.append({
                    "user_id": user_id,
                    "score": score
                })

            candidate_scores = sorted(candidate_scores, key=lambda x: x["score"], reverse=True)

            results.append({
                "jobs" : job_description,
                "employer_id": employer_id,
                "ranked_candidates": candidate_scores
            })

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/analyze', methods=['POST'])
def match_candidates():
    """POST endpoint to match candidates with jobs."""
    try:
        data = request.get_json()
        candidates = data.get("candidates", [])
        employers = data.get("employers", [])

        result = []

        for employer in employers:
            employer_id = employer["employer_id"]
            job_description = employer["job_description"]
            
            job_location = job_description.split()[-1]

            ranked_candidates = []

            for candidate in candidates:
                user_id = candidate["user_id"]
                resume_text = candidate["resume_text"]
                expected_salary = candidate["salary"]
                candidate_location = candidate["location"]

                skill_match_score = compute_match_score(job_description, resume_text)
                location_score = get_location_score(job_location, candidate_location)
                salary_score = get_salary_score(expected_salary)

                final_score = (skill_match_score * 0.7) + (location_score * 0.2) + (salary_score * 0.1)

                reason = f"Skill match: {skill_match_score:.2f}, Location match: {location_score:.2f}, Salary match: {salary_score:.2f}."
                if skill_match_score < 0.5:
                    reason += " Improve skill set relevant to the job."
                if location_score == 0:
                    reason += " Relocation might be needed."
                if salary_score < 0.8:
                    reason += " Expected salary might be too high."

                ranked_candidates.append({"score": final_score, "user_id": user_id, "Analysis": reason})

            ranked_candidates.sort(key=lambda x: x["score"], reverse=True)

            result.append({
                "employer_id": employer_id,
                "jobs": " ".join(job_description.split()[:10]),  
                "ranked_candidates": ranked_candidates
            })

        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/groq', methods=['POST'])
def extract_text():
    try:
        data = request.get_json()
        pdf_url = data.get("pdf_url")

        if not pdf_url:
            return jsonify({"error": "PDF URL is missing"}), 400

        response = requests.get(pdf_url, stream=True)
        response.raise_for_status()

        pdf_file = io.BytesIO(response.content)
        reader = PdfReader(pdf_file)

        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''

        prompt = f"""
Extract structured information from the following resume:

{text}

Ensure the output is a **valid JSON object** with these **exact fields**:

- name (string)
- contact (string)
- email (string)
- skills (list of strings)
- experience (list of objects with company, role, duration, responsibilities)
- education (list of objects with institution, degree, year)
- projects (list of objects with title, description, technologies)
- certifications (list of objects with name, issuer, year)
- github (string)
- linkedin (string)

### **Rules**:
1. **Strictly return only the JSON object** – no extra text, explanations, or markdown formatting.
2. **Ensure the JSON is well-formatted and valid.** 
"""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an AI that extracts structured information from resumes."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            top_p=1,
            stop=None,
            stream=False,
        )

        extracted_data = chat_completion.choices[0].message.content.strip()
        json_match = re.search(r"\{.*\}", extracted_data, re.DOTALL)
        if not json_match:
            return jsonify({"error": "Invalid JSON format received from API"}), 500

        json_str = json_match.group(0)  

        try:
            parsed_data = json.loads(json_str)  
            return jsonify({"resume_data": parsed_data})
        except json.JSONDecodeError:
            return jsonify({"error": "Received malformed JSON from API"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
