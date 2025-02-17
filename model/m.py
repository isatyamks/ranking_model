import os
import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return text

def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return preprocess_text(file.read())

def load_resumes(folder_path):
    resumes = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            resumes[filename] = load_text(file_path)
    return resumes

def rank_resumes_multiple(job_desc_folder, resumes_folder):
    job_desc_files = [f for f in os.listdir(job_desc_folder) if f.endswith('.txt')]
    resumes = load_resumes(resumes_folder)
    
    results = {}
    
    for job_desc_file in job_desc_files:
        job_desc_path = os.path.join(job_desc_folder, job_desc_file)
        job_desc = load_text(job_desc_path)
        
        documents = [job_desc] + list(resumes.values())
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        job_vector = tfidf_matrix[0]
        resume_vectors = tfidf_matrix[1:]
        
        scores = cosine_similarity(job_vector, resume_vectors)[0]
        
        ranked_resumes = sorted(zip(resumes.keys(), scores), key=lambda x: x[1], reverse=True)
        
        results[job_desc_file] = [{"resume": name, "score": round(score, 4)} for name, score in ranked_resumes]
    
    with open("ranked_candidates_multiple.json", "w", encoding='utf-8') as f:
        json.dump(results, f, indent=4)
    
    return results

if __name__ == "__main__":
    job_desc_folder = "data\\employer\\"
    resumes_folder = "data\\resumes\\"
    ranked_results = rank_resumes_multiple(job_desc_folder, resumes_folder)
    print(json.dumps(ranked_results, indent=4))
