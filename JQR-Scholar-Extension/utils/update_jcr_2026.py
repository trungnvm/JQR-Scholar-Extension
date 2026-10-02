import os
import json
import re
import unicodedata
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RANKINGS_DIR = os.path.join(DATA_DIR, "rankings")
EXCEL_FILE = os.path.join(DATA_DIR, "2026-newJCRimpactfactor.xlsx")

OLD_IF_FILE = os.path.join(RANKINGS_DIR, "impact_factors.js")
OLD_IF_NAMES_FILE = os.path.join(RANKINGS_DIR, "impact_factors_names.js")

OUTPUT_IF_FILE = os.path.join(RANKINGS_DIR, "impact_factors.js")
OUTPUT_IF_NAMES_FILE = os.path.join(RANKINGS_DIR, "impact_factors_names.js")

def clean_name(str_val):
    if not str_val:
        return ""
    s = str(str_val).lower()
    s = s.replace('&', 'and')
    s = re.sub(r'[-–—]', ' ', s)
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_issn(issn_val):
    if not issn_val or pd.isna(issn_val):
        return ""
    clean = re.sub(r'[^A-Za-z0-9]', '', str(issn_val)).upper().strip()
    return clean if len(clean) == 8 else ""

def format_jif_value(val):
    if pd.isna(val) or val is None or val == "":
        return None
    try:
        f = float(val)
        # Format as string with up to 3 decimals or 1 decimal if .0
        s = f"{f:.3f}".rstrip('0').rstrip('.')
        if '.' not in s:
            s = f"{s}.0"
        return s
    except Exception:
        return str(val).strip()

def run_update():
    print(f"Reading new JCR file: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE, sheet_name="Journals")
    print(f"Total rows in Excel: {len(df)}")

    new_impact_factors = {}
    new_impact_factors_names = {}

    processed_journals = 0
    skipped_no_jif = 0

    for _, row in df.iterrows():
        j_name = str(row.get("Journal name", "")).strip()
        abbr_name = str(row.get("Abbreviated journal", "")).strip() if pd.notna(row.get("Abbreviated journal")) else ""
        issn_raw = row.get("ISSN")
        eissn_raw = row.get("eISSN")
        jif_raw = row.get("2025 JIF")
        quartile_raw = row.get("JIF quartile")
        year_raw = row.get("JCR year")

        jif_val = format_jif_value(jif_raw)
        if not jif_val:
            skipped_no_jif += 1
            continue

        quartile = str(quartile_raw).strip() if pd.notna(quartile_raw) and str(quartile_raw).strip() != "nan" else ""
        try:
            year = int(year_raw) if pd.notna(year_raw) else 2025
        except Exception:
            year = 2025

        issn_clean_str = str(issn_raw).strip() if pd.notna(issn_raw) else ""
        eissn_clean_str = str(eissn_raw).strip() if pd.notna(eissn_raw) else ""
        primary_issn_display = issn_clean_str if issn_clean_str else eissn_clean_str
        secondary_issn_display = eissn_clean_str if (issn_clean_str and eissn_clean_str != issn_clean_str) else ""

        # Extract Category Quartiles JSON (Column AG)
        ag_raw = row.get("Category quartiles JSON")
        categories_list = []
        if pd.notna(ag_raw) and ag_raw:
            try:
                parsed_ag = json.loads(ag_raw) if isinstance(ag_raw, str) else ag_raw
                if isinstance(parsed_ag, list):
                    for item in parsed_ag:
                        cat_name = str(item.get("category", "")).strip()
                        cat_q = str(item.get("quartile", "")).strip()
                        cat_rank = str(item.get("jifRank", "")).strip()
                        cat_pct = str(item.get("jifPercentile", "")).strip()
                        if cat_name:
                            categories_list.append({
                                "cat": cat_name,
                                "q": cat_q,
                                "rank": cat_rank,
                                "pct": cat_pct
                            })
            except Exception:
                pass

        entry_issn = {
            "value": jif_val,
            "year": year,
            "quartile": quartile,
            "source": "JCR",
            "name": j_name,
            "categories": categories_list
        }

        entry_name = {
            "value": jif_val,
            "year": year,
            "quartile": quartile,
            "issn": primary_issn_display,
            "eissn": secondary_issn_display,
            "source": "JCR",
            "categories": categories_list
        }

        # Index by ISSN
        c_issn = clean_issn(issn_raw)
        if c_issn:
            new_impact_factors[c_issn] = entry_issn

        # Index by eISSN
        c_eissn = clean_issn(eissn_raw)
        if c_eissn:
            new_impact_factors[c_eissn] = entry_issn

        # Index by cleaned journal name
        c_name = clean_name(j_name)
        if c_name:
            new_impact_factors_names[c_name] = entry_name
            # Alias for 'the ' prefix
            if c_name.startswith('the '):
                without_the = c_name[4:].strip()
                if without_the and without_the not in new_impact_factors_names:
                    new_impact_factors_names[without_the] = entry_name
            else:
                with_the = f"the {c_name}"
                if with_the not in new_impact_factors_names:
                    new_impact_factors_names[with_the] = entry_name

        # Index by abbreviated journal name (if not colliding)
        if abbr_name:
            c_abbr = clean_name(abbr_name)
            if c_abbr and c_abbr not in new_impact_factors_names:
                new_impact_factors_names[c_abbr] = entry_name

        processed_journals += 1

    print(f"Processed {processed_journals} journals (skipped {skipped_no_jif} without JIF).")
    print(f"Total new ISSN keys: {len(new_impact_factors)}")
    print(f"Total new Name keys: {len(new_impact_factors_names)}")

    # Load old data for fallback (if any journal from previous years was missing in 2025)
    old_impact_factors = {}
    if os.path.exists(OLD_IF_FILE):
        try:
            with open(OLD_IF_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                # strip JS prefix: sfc.impactFactors = { ... };
                match = re.search(r'sfc\.impactFactors\s*=\s*({[\s\S]*});?', content)
                if match:
                    old_impact_factors = json.loads(match.group(1).rstrip(';'))
                    print(f"Loaded {len(old_impact_factors)} old ISSN entries for fallback preservation.")
        except Exception as e:
            print(f"Note: Could not parse old impact_factors.js ({e}), creating fresh.")

    old_impact_factors_names = {}
    if os.path.exists(OLD_IF_NAMES_FILE):
        try:
            with open(OLD_IF_NAMES_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'sfc\.impactFactorsNames\s*=\s*({[\s\S]*});?', content)
                if match:
                    old_impact_factors_names = json.loads(match.group(1).rstrip(';'))
                    print(f"Loaded {len(old_impact_factors_names)} old Name entries for fallback preservation.")
        except Exception as e:
            print(f"Note: Could not parse old impact_factors_names.js ({e}), creating fresh.")

    # Preserve old records if not in new
    preserved_issns = 0
    for k, v in old_impact_factors.items():
        if k not in new_impact_factors:
            new_impact_factors[k] = v
            preserved_issns += 1

    preserved_names = 0
    for k, v in old_impact_factors_names.items():
        if k not in new_impact_factors_names:
            new_impact_factors_names[k] = v
            preserved_names += 1

    print(f"Preserved {preserved_issns} fallback ISSNs and {preserved_names} fallback Names from previous database.")
    print(f"Final total ISSN keys: {len(new_impact_factors)}")
    print(f"Final total Name keys: {len(new_impact_factors_names)}")

    # Write output JS files
    os.makedirs(RANKINGS_DIR, exist_ok=True)

    with open(OUTPUT_IF_FILE, 'w', encoding='utf-8') as f:
        f.write("if (typeof sfc === 'undefined') var sfc = {};\n")
        f.write("sfc.impactFactors = ")
        json.dump(new_impact_factors, f, indent=2, ensure_ascii=False)
        f.write(";\n")
    print(f"Saved: {OUTPUT_IF_FILE}")

    with open(OUTPUT_IF_NAMES_FILE, 'w', encoding='utf-8') as f:
        f.write("if (typeof sfc === 'undefined') var sfc = {};\n")
        f.write("sfc.impactFactorsNames = ")
        json.dump(new_impact_factors_names, f, indent=2, ensure_ascii=False)
        f.write(";\n")
    print(f"Saved: {OUTPUT_IF_NAMES_FILE}")

if __name__ == "__main__":
    run_update()
