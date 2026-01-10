import csv
import json
import re
import os

def clean_name(name):
    if not name:
        return ""
    # Lowercase and remove special characters (non-alphanumeric)
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
    return cleaned

def merge_data():
    file_2025 = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/JCRI-impact-Factors_2025.csv"
    file_2024 = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/journal_impact_2024.csv"
    output_dir = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/scholar_extention_trung/data/rankings"
    output_file = os.path.join(output_dir, "impact_factors_names.js")

    impact_factors = {}

    # Process 2025 data
    print(f"Processing 2025 data from {file_2025}...")
    if os.path.exists(file_2025):
        with open(file_2025, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Journal Name', '').strip()
                cleaned = clean_name(name)
                if not cleaned:
                    continue

                try:
                    jif = float(row.get('JIF', 0))
                except (ValueError, TypeError):
                    jif = 0.0

                impact_factors[cleaned] = {
                    "value": jif,
                    "quartile": row.get('Quartile', '').strip(),
                    "issn": row.get('ISSN', '').strip(),
                    "source": "2025",
                    "name": name
                }
    else:
        print(f"Warning: 2025 file not found at {file_2025}")

    # Process 2024 data
    print(f"Processing 2024 data from {file_2024}...")
    if os.path.exists(file_2024):
        with open(file_2024, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('Journal Name', '').strip()
                cleaned = clean_name(name)
                if not cleaned:
                    continue

                if cleaned not in impact_factors:
                    try:
                        jif = float(row.get('JIF 2024', 0))
                    except (ValueError, TypeError):
                        jif = 0.0

                    impact_factors[cleaned] = {
                        "value": jif,
                        "quartile": "",
                        "issn": "",
                        "source": "2024",
                        "name": name
                    }
    else:
        print(f"Warning: 2024 file not found at {file_2024}")

    # Write output
    print(f"Writing output to {output_file}...")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("if (typeof sfc === 'undefined') { var sfc = {}; }\n")
        f.write("sfc.impactFactorsNames = ")
        json.dump(impact_factors, f, indent=4)
        f.write(";\n")

    print(f"Successfully merged {len(impact_factors)} records.")

if __name__ == "__main__":
    merge_data()
