import spacy
import json
import re

def parse_person_section(section):
    """Extract details of a person from their section in the Markdown file."""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(section)
    
    person_data = {}
    
    # Extract the name (first line)
    lines = section.split("\n")
    person_data["Name"] = lines[0].strip() if lines else "Unknown"
    
    # Extract salary desired
    salary_match = re.search(r"Salary desired:\s*(.+)", section)
    person_data["Salary"] = salary_match.group(1).strip() if salary_match else "Unknown"
    
    # Extract education
    education = []
    education_section = re.search(r"EDUCATION\s*\n(.*?)(?:\n\n|\Z)", section, re.DOTALL)
    if education_section:
        for line in education_section.group(1).split("\n"):
            if line.strip():
                education.append(line.strip())
    person_data["Education"] = education
    
    # Extract skills
    skills = []
    skills_match = re.search(r"Skills[\s\S]*?\* (.*?)(?:\n\n|\Z)", section)
    if skills_match:
        skills = [skill.strip() for skill in skills_match.group(1).split(",")]
    person_data["Skills"] = skills
    
    # Extract experience
    experience = []
    experience_section = re.search(r"EXPERIENCE\s*\n(.*?)(?:\n\n|\Z)", section, re.DOTALL)
    if experience_section:
        for line in experience_section.group(1).split("\n"):
            if line.strip() and not line.strip().startswith("*"):
                experience.append(line.strip())
    person_data["Experience"] = experience

    # Extract other entities with spaCy (locations, organizations, etc.)
    person_data["Entities"] = {
        "Organizations": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
        "Locations": [ent.text for ent in doc.ents if ent.label_ == "GPE"],
    }

    return person_data

def parse_markdown_to_json(file_path):
    """Parse a Markdown file and convert it into JSON."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split by PERSON to isolate profiles
    sections = re.split(r"(?=PERSON\d+)", content)
    profiles = [parse_person_section(section.strip()) for section in sections if section.strip()]

    return {"Candidates": profiles}

# Input and output file paths
input_file = "..\\data\\Candidate Profiles.md"
output_file = "..\\data\\candidate_profiles.json"

# Parse and convert to JSON
data = parse_markdown_to_json(input_file)

# Save to a JSON file
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, indent=4)

print(f"JSON file created: {output_file}")
