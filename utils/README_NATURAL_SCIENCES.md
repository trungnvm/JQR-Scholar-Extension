# Natural Sciences Data Collection

This directory contains scripts for orchestrating the collection, classification, and conversion of natural sciences journal data.

## Overview

The data collection pipeline consists of two main scripts:

1. **`collect_natural_sciences_data.py`** - Collects and enriches journal data
2. **`convert_to_js.py`** - Converts CSV data to JavaScript format for the extension

## Scripts

### 1. collect_natural_sciences_data.py

Orchestrates the collection of journal data for natural sciences fields using the implemented modules.

**Features:**
- Fetches journals from OpenAlex API for Physics, Chemistry, Biology, and Mathematics
- Classifies journals using OECD field classification
- Enriches with impact factors from SJR data (optional)
- Deduplicates across fields
- Exports to organized CSV files

**Usage:**

```bash
# Basic collection (without impact factors)
python collect_natural_sciences_data.py

# With email for API polite pool (recommended)
python collect_natural_sciences_data.py --email your-email@example.com

# With SJR data for impact factor enrichment
python collect_natural_sciences_data.py \
  --sjr-csv ../data/raw/scimagojr.csv \
  --email your-email@example.com

# Custom output directory
python collect_natural_sciences_data.py \
  --output-dir /path/to/output \
  --email your-email@example.com

# Debug mode
python collect_natural_sciences_data.py \
  --log-level DEBUG \
  --email your-email@example.com
```

**Arguments:**
- `--email`: Email for API polite pools (faster rate limits)
- `--sjr-csv`: Path to SJR CSV file for impact factor enrichment
- `--output-dir`: Output directory for CSV files (default: `../data/processed/`)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)

**Output Files:**
- `physics_journals.csv` - Physics journals
- `chemistry_journals.csv` - Chemistry journals
- `biology_journals.csv` - Biology/Life Sciences journals
- `mathematics_journals.csv` - Mathematics journals
- `natural_sciences_combined.csv` - Deduplicated combined data

**Target Counts:**
- Physics: 1000+ journals
- Chemistry: 800+ journals
- Biology: 1200+ journals
- Mathematics: 600+ journals

### 2. convert_to_js.py

Converts processed CSV files to JavaScript format compatible with the browser extension.

**Features:**
- Reads CSV files from `data/processed/`
- Converts to JavaScript `sfc.*` format
- Generates individual field files and combined file
- Includes metadata and statistics

**Usage:**

```bash
# Convert all fields
python convert_to_js.py

# Convert specific fields only
python convert_to_js.py --fields physics chemistry

# Custom directories
python convert_to_js.py \
  --input-dir /path/to/csv \
  --output-dir /path/to/js

# Debug mode
python convert_to_js.py --log-level DEBUG
```

**Arguments:**
- `--input-dir`: Input directory with CSV files (default: `../data/processed/`)
- `--output-dir`: Output directory for JS files (default: `../data/fields/natural_sciences/`)
- `--fields`: Specific fields to convert (physics, chemistry, biology, mathematics, all)
- `--log-level`: Logging level (DEBUG, INFO, WARNING, ERROR)

**Output Files:**
- `sfc.physics.js` - Physics journals in JS format
- `sfc.chemistry.js` - Chemistry journals in JS format
- `sfc.biology.js` - Biology journals in JS format
- `sfc.mathematics.js` - Mathematics journals in JS format
- `sfc.natural_sciences.js` - All fields combined in one file

**JavaScript Format:**
```javascript
// Example output format
if (typeof sfc === 'undefined') {
  var sfc = {};
}

sfc.physics = {
  "0028-0836": {
    "name": "Nature",
    "field": "physics",
    "if": 42.778,
    "quartile": "Q1",
    "h_index": 1234,
    "oecd_code": "1.3",
    "oecd_field": "Physical sciences"
  },
  // ... more journals
};

sfc.physics_meta = {
  count: 1000,
  field: "physics",
  generated: "2026-01-10T12:00:00",
  version: "1.0"
};
```

## Complete Workflow

### Step 1: Collect Data

```bash
cd scholar_extention_trung/utils

# Collect all natural sciences data with impact factors
python collect_natural_sciences_data.py \
  --email your-email@example.com \
  --sjr-csv ../data/raw/scimagojr.csv
```

This will:
1. Fetch journals from OpenAlex for each field
2. Classify using OECD field classifier
3. Enrich with SJR impact factors (if available)
4. Deduplicate and export to CSV

**Expected runtime:** 30-60 minutes depending on API rate limits

### Step 2: Convert to JavaScript

```bash
# Convert all CSV files to JavaScript
python convert_to_js.py
```

This will:
1. Read all field CSV files
2. Convert to JavaScript format
3. Export individual and combined JS files

**Expected runtime:** Less than 1 minute

### Step 3: Verify Output

```bash
# Check CSV files
ls -lh ../data/processed/*.csv

# Check JavaScript files
ls -lh ../data/fields/natural_sciences/*.js

# View statistics
tail -n 50 natural_sciences_collection.log
```

## Output Structure

```
data/
├── processed/
│   ├── physics_journals.csv
│   ├── chemistry_journals.csv
│   ├── biology_journals.csv
│   ├── mathematics_journals.csv
│   └── natural_sciences_combined.csv
└── fields/
    └── natural_sciences/
        ├── sfc.physics.js
        ├── sfc.chemistry.js
        ├── sfc.biology.js
        ├── sfc.mathematics.js
        └── sfc.natural_sciences.js
```

## CSV Format

Each CSV file contains the following columns:

**Core Columns:**
- `name` - Journal name
- `issn` - ISSN(s) (comma-separated if multiple)
- `field` - Primary field
- `source` - Data source (OpenAlex, Crossref)
- `url` - Journal homepage URL
- `publisher` - Publisher name

**Classification Columns:**
- `classified_field_code` - OECD field code (e.g., "1.3")
- `classified_field_name` - OECD field name
- `classification_confidence` - Confidence score (0-1)
- `classification_methods` - Methods used for classification

**Impact Factor Columns (if SJR data available):**
- `impact_factor` - SJR or 2-year mean citedness
- `if_year` - Year of impact factor
- `if_source` - Source (sjr, openalex)
- `quartile` - SJR quartile (Q1, Q2, Q3, Q4)
- `h_index` - H-index

**Citation Metrics:**
- `works_count` - Number of published works
- `cited_by_count` - Total citations
- `topics` - Associated topics (comma-separated)

## Dependencies

Required Python packages:
- pandas
- requests
- urllib3

All dependencies are listed in `requirements.txt`

## Troubleshooting

### Issue: No journals collected for a field

**Solution:**
- Check OpenAlex API connectivity
- Verify search terms in `FIELDS_CONFIG`
- Try with different search terms
- Check log file for errors

### Issue: Impact factor enrichment fails

**Solution:**
- Verify SJR CSV file path
- Check SJR CSV format (should have `Title`, `Issn`, `SJR` columns)
- Try running without `--sjr-csv` flag (will use OpenAlex metrics only)

### Issue: Conversion to JS fails

**Solution:**
- Verify CSV files exist in input directory
- Check CSV file format (must have `issn` and `name` columns)
- Verify output directory permissions

### Issue: API rate limiting

**Solution:**
- Use `--email` flag for polite pool access
- Reduce target counts in `FIELDS_CONFIG`
- Add delays between requests (modify `rate_limiter` settings)

## Advanced Configuration

### Customizing Field Targets

Edit `FIELDS_CONFIG` in `collect_natural_sciences_data.py`:

```python
FIELDS_CONFIG = {
    'physics': {
        'search_terms': ['physics', 'quantum'],  # Customize search terms
        'target_count': 500,  # Reduce target
        'oecd_codes': ['1.3'],
        'description': 'Physics journals'
    },
    # ... other fields
}
```

### Adding New Fields

Add new field configuration:

```python
'astronomy': {
    'search_terms': ['astronomy', 'astrophysics', 'cosmology'],
    'target_count': 300,
    'oecd_codes': ['1.3'],
    'description': 'Astronomy and Astrophysics journals'
}
```

Then update `FIELD_MAPPINGS` in `convert_to_js.py`:

```python
FIELD_MAPPINGS = {
    'physics': 'physics',
    'chemistry': 'chemistry',
    'biology': 'biology',
    'mathematics': 'mathematics',
    'astronomy': 'astronomy'  # Add new field
}
```

## Logging

Both scripts generate detailed logs:

- Console output: Real-time progress
- Log file: `natural_sciences_collection.log`

Log levels:
- `DEBUG`: Detailed API calls and processing
- `INFO`: Progress and summary information (default)
- `WARNING`: Non-critical issues
- `ERROR`: Critical errors

## Performance Tips

1. **Use email for polite pool**: Provides faster API rate limits
2. **Run during off-peak hours**: Better API responsiveness
3. **Monitor progress**: Check log files periodically
4. **Adjust targets**: Start with smaller targets for testing
5. **Use SJR data**: Faster than fetching impact factors from APIs

## Data Quality

The pipeline includes several quality checks:

- **Deduplication**: Removes duplicate journals by ISSN
- **Validation**: Verifies required fields (name, ISSN)
- **Classification confidence**: Scores indicate classification reliability
- **Multiple sources**: Combines OpenAlex, SJR, and Crossref data

## License

Part of the Scholar Extension project.
See main project LICENSE file for details.

## Contact

For issues or questions, see the main project repository.

---

**Last Updated:** January 10, 2026
**Version:** 1.0
