import json
import re

def parse_employer_data(filename):
    """Parse employer details from the file and return as a list of dictionaries."""
    with open(filename, 'r') as file:
        data = file.read().strip()
    employers = data.split("________________")
    employer_list = []
    
    for emp in employers:
        lines = [line.strip() for line in emp.strip().split("\n") if line.strip()]
        if len(lines) < 2:
            continue
        employer = {
            'JobTitle': lines[1].strip(),
            'Description': " ".join(lines[2:]).strip()
        }
        for line in lines:
            if "Salary" in line and ":" in line:
                employer['Salary'] = line.split(":", 1)[1].strip()
            if "Experience" in line:
                employer['Experience'] = re.findall(r'\d+', line)
            if "Skills" in line and ":" in line:
                employer['Skills'] = [skill.strip() for skill in line.split(":", 1)[1].split(",")]
            if "Location" in line and ":" in line:
                employer['Location'] = line.split(":", 1)[1].strip()
        # Defaults for missing fields
        employer.setdefault('Salary', "0-0")
        employer.setdefault('Skills', [])
        employer.setdefault('Location', "Unknown")
        employer.setdefault('Experience', [0])
        employer_list.append(employer)
    
    return employer_list

def parse_candidate_data(filename):
    """Parse candidate details from the file and return as a list of dictionaries."""
    with open(filename, 'r') as file:
        data = file.read().strip()
    candidates = data.split("________________")
    candidate_list = []
    
    for cand in candidates:
        lines = [line.strip() for line in cand.strip().split("\n") if line.strip()]
        if len(lines) < 2:
            continue
        candidate = {
            'Name': lines[0].strip(),
            'Details': " ".join(lines[1:]).strip()
        }
        for line in lines:
            if "Salary desired" in line:
                candidate['Salary'] = re.findall(r'\d+', line)
            if "Skills" in line and ":" in line:
                candidate['Skills'] = [skill.strip() for skill in line.split(":", 1)[1].split(",")]
            if "Location" in line and ":" in line:
                candidate['Location'] = line.split(":", 1)[1].strip()
        # Defaults for missing fields
        candidate.setdefault('Salary', [0])
        candidate.setdefault('Skills', [])
        candidate.setdefault('Location', "Unknown")
        candidate_list.append(candidate)
    
    return candidate_list

# Parse data
employer_data = parse_employer_data("data\\Employer Profiles.txt")
candidate_data = parse_candidate_data("data\\Candidate Profiles.txt")

# Save to JSON
with open("/mnt/data/employers.json", "w") as emp_json:
    json.dump(employer_data, emp_json, indent=4)

with open("/mnt/data/candidates.json", "w") as cand_json:
    json.dump(candidate_data, cand_json, indent=4)

print("JSON files created: employers.json and candidates.json")
