import io
import json
import re
import requests
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

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

        # Use regex to extract only the JSON portion
        json_match = re.search(r"\{.*\}", extracted_data, re.DOTALL)
        if not json_match:
            return jsonify({"error": "Invalid JSON format received from API"}), 500

        json_str = json_match.group(0)  # Extract JSON string

        try:
            parsed_data = json.loads(json_str)  # Convert JSON string to Python dictionary
            return jsonify({"resume_data": parsed_data})
        except json.JSONDecodeError:
            return jsonify({"error": "Received malformed JSON from API"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
