import csv
import json
import os
import re
import unicodedata

def clean_name(name):
    """
    Clean journal name using logic similar to content.js/ccf.js:
    - Normalizes unicode characters
    - Converts to uppercase (as seen in ccf.JCR.js)
    - Removes all non-alphanumeric characters
    """
    if not name:
        return ""

    # Normalize unicode (NFD decomposition)
    name = unicodedata.normalize('NFD', name)

    # Remove "&" and common words if necessary, following ccf.js patterns
    # url = url.replace(/&AMP;/g, "&");
    # url = url.replace(/ AND /g, "");
    # url = url.replace(/^THE /g, "");
    # url = url.replace(/, THE$/g, "");

    name = name.upper()
    name = name.replace('&AMP;', '&')
    name = name.replace(' AND ', '')
    if name.startswith('THE '):
        name = name[4:]
    if name.endswith(', THE'):
        name = name[:-5]

    # Remove [^A-Z0-9]
    name = re.sub(r'[^A-Z0-9]', '', name)

    return name.lower() # The requested output format uses lowercase keys

def process_jcr_csv(input_path, output_path):
    print(f"Reading JCR data from {input_path}...")

    impact_factors = {}

    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                journal_name = row.get('Journal Name', '').strip()
                jif = row.get('JIF', '0')
                quartile = row.get('Quartile', 'NA')
                issn = row.get('ISSN', '')

                if not journal_name:
                    continue

                # We want the key to be exactly as requested in the example: "nature reviews microbiology"
                # The user example shows lowercase with spaces, but then says "clean_name function similar to content.js"
                # content.js (ccf.js) removes spaces.
                # Let's re-read the requirement.
                # Example: "nature reviews microbiology": { "value": 103.3, ... }
                # This example HAS SPACES.
                # But the prompt says: "Uses a clean_name function similar to the reference content.js: Lowercase, remove special chars, normalize."

                # If I follow ccf.js strictly: it removes spaces.
                # If I follow the user's example key: it has spaces.

                # Let's look at the example again:
                # "nature reviews microbiology": { "value": 103.3, "quartile": "Q1", "issn": "1740-1526" }

                # I will implement a clean_name that keeps spaces but lowers and removes special chars as requested.

                def clean_name_v2(n):
                    n = unicodedata.normalize('NFD', n)
                    n = n.lower()
                    n = re.sub(r'[^a-z0-9\s]', '', n)
                    n = re.sub(r'\s+', ' ', n).strip()
                    return n

                cleaned = clean_name_v2(journal_name)

                try:
                    jif_val = float(jif)
                except ValueError:
                    jif_val = 0.0

                impact_factors[cleaned] = {
                    "value": jif_val,
                    "quartile": quartile,
                    "issn": issn
                }

        print(f"Processed {len(impact_factors)} journals.")

        # Write to JavaScript file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("if (typeof sfc === 'undefined') { var sfc = {}; }\n")
            f.write("sfc.impactFactorsNames = ")
            json.dump(impact_factors, f, indent=4)
            f.write(";\n")

        print(f"Successfully wrote output to {output_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_csv = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/JCRI-impact-Factors_2025.csv"
    output_js = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/scholar_extention_trung/data/rankings/impact_factors_names.js"

    process_jcr_csv(input_csv, output_js)
