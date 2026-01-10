import pandas as pd
import json
import os

def process_jcr_data(csv_path, output_path):
    # Read the CSV file
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Required columns: ISSN, JIF, Quartile, Journal Name
    # Based on the head output: Rank,Journal Name,Publisher,ISSN,JIF,Quartile

    # Extract and clean data
    impact_factors = {}

    for index, row in df.iterrows():
        issn = str(row.get('ISSN', '')).replace('-', '').strip()
        if not issn or issn.lower() == 'nan':
            continue

        jif = row.get('JIF')
        try:
            jif_value = float(jif) if pd.notnull(jif) else 0.0
        except ValueError:
            jif_value = 0.0

        quartile = str(row.get('Quartile', '')).strip()
        name = str(row.get('Journal Name', '')).strip()

        impact_factors[issn] = {
            "value": jif_value,
            "quartile": quartile if pd.notnull(quartile) and quartile != 'nan' else "",
            "year": 2024,
            "source": "JCR",
            "name": name if pd.notnull(name) and name != 'nan' else ""
        }

    # Format as JavaScript object string
    js_content = "if (typeof sfc === 'undefined') { var sfc = {}; }\n"
    js_content += "sfc.impactFactors = " + json.dumps(impact_factors, indent=4) + ";"

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write the output
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"Successfully wrote data to {output_path}")
    except Exception as e:
        print(f"Error writing JS file: {e}")

if __name__ == "__main__":
    csv_file = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/JCRI-impact-Factors_2025.csv"
    output_file = "/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/scholar_extention_trung/data/rankings/impact_factors.js"
    process_jcr_data(csv_file, output_file)
