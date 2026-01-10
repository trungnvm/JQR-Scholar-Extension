import csv
import json
import re
import os
import unicodedata

# Paths
FILE_2025 = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/JCRI-impact-Factors_2025.csv"
FILE_2024 = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/journal_impact_2024.csv"
OUTPUT_DIR = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/scholar_extention_trung/data/rankings"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_name(name):
    """Clean Name (lowercase, alphanumeric) exactly as the JS reference."""
    if not name:
        return ""
    text = name.lower()
    text = text.replace('&', 'and')
    text = text.replace('-', ' ').replace('–', ' ').replace('—', ' ')
    text = unicodedata.normalize('NFD', text)
    text = re.sub(r'[\u0300-\u036f]', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_issn(issn):
    """Clean ISSN (remove hyphens)."""
    if not issn:
        return ""
    return issn.replace('-', '')

def generate_databases():
    impact_factors = {}
    impact_factors_names = {}

    # Task 1 & 2: Process 2025 File
    # Rank,Journal Name,Publisher,ISSN,JIF,Quartile
    with open(FILE_2025, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Journal Name', '').strip()
            issn = row.get('ISSN', '').strip()
            jif = row.get('JIF', '').strip()
            quartile = row.get('Quartile', '').strip()

            clean_issn_val = clean_issn(issn)
            clean_name_val = clean_name(name)

            # Task 1: ISSN Lookup (2025 file only)
            if clean_issn_val:
                impact_factors[clean_issn_val] = {
                    "value": jif,
                    "year": 2024,
                    "quartile": quartile,
                    "source": "JCR",
                    "name": name
                }

            # Task 2: Name Lookup (2025 first)
            if clean_name_val:
                impact_factors_names[clean_name_val] = {
                    "value": jif,
                    "year": 2024,
                    "quartile": quartile,
                    "issn": issn,
                    "source": "JCR"
                }

    # Task 2: Merge 2024 File (if missing)
    # Journal Name,JIF 2024
    with open(FILE_2024, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('Journal Name', '').strip()
            jif = row.get('JIF 2024', '').strip()

            clean_name_val = clean_name(name)

            if clean_name_val and clean_name_val not in impact_factors_names:
                impact_factors_names[clean_name_val] = {
                    "value": jif,
                    "year": 2023, # Assuming 2024 file contains 2023 data
                    "quartile": None,
                    "issn": None,
                    "source": "JCR"
                }

    # Write impact_factors.js
    with open(os.path.join(OUTPUT_DIR, "impact_factors.js"), "w", encoding='utf-8') as f:
        f.write("if (typeof sfc === 'undefined') var sfc = {};\n")
        f.write("sfc.impactFactors = ")
        json.dump(impact_factors, f, indent=2)
        f.write(";")

    # Write impact_factors_names.js
    with open(os.path.join(OUTPUT_DIR, "impact_factors_names.js"), "w", encoding='utf-8') as f:
        f.write("if (typeof sfc === 'undefined') var sfc = {};\n")
        f.write("sfc.impactFactorsNames = ")
        json.dump(impact_factors_names, f, indent=2)
        f.write(";")

    print(f"Generated impact_factors.js with {len(impact_factors)} entries.")
    print(f"Generated impact_factors_names.js with {len(impact_factors_names)} entries.")

if __name__ == "__main__":
    generate_databases()
