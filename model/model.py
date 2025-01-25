import re
from collections import defaultdict

# Improved employer parsing
def parse_employer_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read().strip()
    employers = data.split("________________")
    employer_list = []
    for emp in employers:
        lines = [line.strip() for line in emp.strip().split("\n") if line.strip()]
        if len(lines) < 2:
            continue
        employer = {'JobTitle': lines[1].strip(), 'Description': " ".join(lines[2:]).strip()}
        for line in lines:
            if "Salary" in line and len(line.split(":", 1)) > 1:
                employer['Salary'] = line.split(":", 1)[1].strip()
            if "Experience" in line:
                employer['Experience'] = re.findall(r'\d+', line)
            if "Skills" in line and len(line.split(":", 1)) > 1:
                employer['Skills'] = [skill.strip() for skill in line.split(":", 1)[1].split(",")]
            if "Location" in line and len(line.split(":", 1)) > 1:
                employer['Location'] = line.split(":", 1)[1].strip()
        employer.setdefault('Salary', "0-0")
        employer.setdefault('Skills', [])
        employer.setdefault('Location', "Unknown")
        employer.setdefault('Experience', [0])
        employer_list.append(employer)
    return employer_list

# Improved candidate parsing
def parse_candidate_data(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = file.read().strip()
    candidates = data.split("________________")
    candidate_list = []
    for cand in candidates:
        lines = [line.strip() for line in cand.strip().split("\n") if line.strip()]
        if len(lines) < 2:
            continue
        candidate = {'Name': lines[0].strip(), 'Details': " ".join(lines[1:]).strip()}
        for line in lines:
            if "Salary desired" in line:
                candidate['Salary'] = re.findall(r'\d+', line)
            if "Skills" in line and len(line.split(":", 1)) > 1:
                candidate['Skills'] = [skill.strip() for skill in line.split(":", 1)[1].split(",")]
            if "Location" in line:
                candidate['Location'] = line.split(":", 1)[1].strip()
        candidate.setdefault('Salary', [0])
        candidate.setdefault('Skills', [])
        candidate.setdefault('Location', "Unknown")
        candidate_list.append(candidate)
    return candidate_list

# Calculate match score
def calculate_match(employer, candidate):
    skills_match = len(set(employer['Skills']).intersection(set(candidate['Skills']))) / max(1, len(employer['Skills']))
    location_match = 1 if employer['Location'] == candidate['Location'] else 0.5
    salary_match = 1 if int(candidate['Salary'][0]) <= int(re.findall(r'\d+', employer['Salary'].split('-')[1])[0]) else 0
    experience_match = 1  # Placeholder
    return 0.4 * skills_match + 0.3 * location_match + 0.2 * salary_match + 0.1 * experience_match

# Rank candidates
def rank_candidates(employers, candidates):
    rankings = defaultdict(list)
    for employer in employers:
        for candidate in candidates:
            score = calculate_match(employer, candidate)
            rankings[employer['JobTitle']].append((candidate['Name'], score))
        rankings[employer['JobTitle']].sort(key=lambda x: x[1], reverse=True)
    return rankings

# Parse files
employers = parse_employer_data("data\\Employer Profiles.txt")
candidates = parse_candidate_data("data\\Candidate Profiles.txt")

# Rank and output results
rankings = rank_candidates(employers, candidates)
for job, ranked_candidates in rankings.items():
    print(f"Job: {job}")
    for name, score in ranked_candidates:
        print(f"  Candidate: {name}, Score: {score:.2f}")
