from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
import string
from src.stopwords import remove_stopwords
import requests
import io
from PyPDF2 import PdfReader
stopwords_file = 'src/stopwords.txt'

nltk.download('punkt_tab')

app = Flask(__name__)


@app.route('/',methods = ['GET'])
def hello():
    return "Hello"

@app.route('/extract', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
