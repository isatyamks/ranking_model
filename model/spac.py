import spacy
import json
import os

def extract_employer_details(text):
    """Extract employer details from the text."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    employer_data = []
    current_employer = {}

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        # Detect Job Title
        if any(keyword in line for keyword in ["Developer", "Designer", "Writer", "Officer"]):
            if current_employer:
                employer_data.append(current_employer)
                current_employer = {}
            current_employer["JobTitle"] = line
        
        # Extract salary
        if "Salary" in line and ":" in line:
            salary = line.split(":", 1)[1].strip()
            current_employer["Salary"] = salary
        
        # Extract location
        if "Location" in line and ":" in line:
            location = line.split(":", 1)[1].strip()
            current_employer["Location"] = location
        
        # Extract skills
        if "Skills" in line and ":" in line:
            skills = line.split(":", 1)[1].strip().split(",")
            current_employer["Skills"] = [skill.strip() for skill in skills if skill.strip()]
        
        # Extract experience
        if "Experience" in line and ":" in line:
            experience = line.split(":", 1)[1].strip()
            current_employer["Experience"] = experience
    
    # Add the last employer if it exists
    if current_employer:
        employer_data.append(current_employer)
    
    # Assign default values for missing fields
    for employer in employer_data:
        employer.setdefault("Salary", "Unknown")
        employer.setdefault("Location", "Unknown")
        employer.setdefault("Skills", [])
        employer.setdefault("Experience", "Unknown")
    
    return employer_data

def extract_candidate_details(text):
    """Extract candidate details from the text."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    candidate_data = []
    current_candidate = {}

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        # Detect Candidate Name
        if line.startswith("PERSON"):
            if current_candidate:
                candidate_data.append(current_candidate)
                current_candidate = {}
            current_candidate["Name"] = line
        
        # Extract salary
        if "Salary desired" in line and ":" in line:
            salary = line.split(":", 1)[1].strip()
            current_candidate["Salary"] = salary
        
        # Extract location
        if "Location" in line and ":" in line:
            location = line.split(":", 1)[1].strip()
            current_candidate["Location"] = location
        
        # Extract skills
        if " Technical Skills" in line :

            skills = line.split(":", 1)[1].strip().split(",")
            current_candidate["Skills"] = [skill.strip() for skill in skills if skill.strip()]
    
    # Add the last candidate if it exists
    if current_candidate:
        candidate_data.append(current_candidate)
    
    # Assign default values for missing fields
    for candidate in candidate_data:
        candidate.setdefault("Salary", "Unknown")
        candidate.setdefault("Location", "Unknown")
        candidate.setdefault("Skills", [])
    
    return candidate_data

def process_files(employer_file, candidate_file):
    """Process input files and generate structured data."""
    with open(employer_file, "r", encoding="utf-8") as ef:
        employer_text = ef.read()
    with open(candidate_file, "r", encoding="utf-8") as cf:
        candidate_text = cf.read()

    employers = extract_employer_details(employer_text)
    candidates = extract_candidate_details(candidate_text)

    return {"employers": employers, "candidates": candidates}

# File paths
employer_file = "..\\data\\Employer Profiles.txt"
candidate_file ="..\\data\\Candidate Profiles.txt"
output_file = "..\\data\\employer_candidate_data.json"

# Process files and generate JSON
data = process_files(employer_file, candidate_file)

# Save JSON to file
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, indent=4)

print(f"JSON file created: {output_file}")
