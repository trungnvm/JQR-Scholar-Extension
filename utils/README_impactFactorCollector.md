# Impact Factor Collector

## Overview

The Impact Factor Collector is a comprehensive Python module for aggregating journal impact metrics from multiple sources:

1. **ScimagoJR (SJR)** - Local CSV database with SJR scores, quartiles, and H-index
2. **OpenAlex API** - 2-year mean citedness as Impact Factor proxy, plus citation metrics
3. **Fallback mechanisms** - Graceful handling of missing data

## Features

- **Multi-source data aggregation** with priority ordering
- **Batch processing** for efficient large-scale data collection
- **Multiple export formats** - JavaScript (for browser extensions) and CSV
- **ISSN normalization** - Handles ISSNs with/without hyphens
- **Error handling** - Robust error handling and logging
- **Rate limiting** - Built-in rate limiting for API calls

## Installation

### Requirements

```bash
pip install pandas requests urllib3
```

Or using the project's requirements file:

```bash
cd scholar_extention_trung
pip install -r requirements.txt
```

### SJR Data Setup

1. Download SJR data from https://www.scimagojr.com/journalrank.php
2. Save as `scholar_extention_trung/data/raw/scimagojr.csv`
3. Verify using the download helper:

```bash
python scholar_extention_trung/utils/download_sjr_data.py
```

## Usage Examples

### Example 1: Basic Single ISSN Query

```python
from scholar_extention_trung.utils.impactFactorCollector import ImpactFactorCollector

# Initialize collector with SJR data
collector = ImpactFactorCollector(
    sjr_csv_path="scholar_extention_trung/data/raw/scimagojr.csv",
    email="your-email@example.com"  # For OpenAlex polite pool
)

# Query single ISSN
issn = "0028-0836"  # Nature journal
if_data = collector.get_impact_factor(issn)

print(f"Journal: {if_data['alternative_metrics'].get('title')}")
print(f"Impact Factor: {if_data['if_value']}")
print(f"Quartile: {if_data['quartile']}")
print(f"H-index: {if_data['h_index']}")
print(f"Source: {if_data['source']}")
```

**Output:**
```
Journal: Nature
Impact Factor: 14.3
Quartile: Q1
H-index: 1234
Source: sjr
```

### Example 2: Batch Processing Multiple ISSNs

```python
from scholar_extention_trung.utils.impactFactorCollector import ImpactFactorCollector

collector = ImpactFactorCollector(
    sjr_csv_path="scholar_extention_trung/data/raw/scimagojr.csv",
    email="your-email@example.com"
)

# List of ISSNs to process
issn_list = [
    "0028-0836",  # Nature
    "0036-8075",  # Science
    "0140-6736",  # The Lancet
    "1474-547X",  # Cell
    "0027-8424",  # PNAS
]

# Batch collect
results = collector.batch_collect(issn_list)

# Print summary
for issn, data in results.items():
    if data['if_value']:
        print(f"{issn}: IF={data['if_value']:.2f}, Q={data['quartile']}, Source={data['source']}")
    else:
        print(f"{issn}: No data available")
```

### Example 3: Export to JavaScript for Browser Extension

```python
from scholar_extention_trung.utils.impactFactorCollector import ImpactFactorCollector

collector = ImpactFactorCollector(
    sjr_csv_path="scholar_extention_trung/data/raw/scimagojr.csv"
)

# Collect data for your journal list
issn_list = ["0028-0836", "0036-8075", "0140-6736"]
results = collector.batch_collect(issn_list)

# Export to JavaScript file
output_file = "scholar_extention_trung/extension/data/impact_factors.js"
collector.export_to_js(results, output_file)

print(f"Exported {len(results)} journals to {output_file}")
```

**Generated JavaScript file:**
```javascript
// Auto-generated Impact Factor data
// Generated on: 2024-01-10 15:30:00
// Total journals: 3

if (typeof sfc === 'undefined') {
  var sfc = {};
}

sfc.impactFactors = {
  "0028-0836": {
    "value": 14.3,
    "year": 2023,
    "source": "sjr",
    "quartile": "Q1",
    "h_index": 1234,
    "title": "Nature"
  },
  "0036-8075": {
    "value": 12.1,
    "year": 2023,
    "source": "sjr",
    "quartile": "Q1",
    "h_index": 1100,
    "title": "Science"
  }
}
```

### Example 4: Export to CSV for Analysis

```python
from scholar_extention_trung.utils.impactFactorCollector import ImpactFactorCollector

collector = ImpactFactorCollector(
    sjr_csv_path="scholar_extention_trung/data/raw/scimagojr.csv"
)

# Collect data
issn_list = ["0028-0836", "0036-8075", "0140-6736"]
results = collector.batch_collect(issn_list)

# Export to CSV
output_file = "scholar_extention_trung/data/processed/impact_factors.csv"
collector.export_to_csv(results, output_file)

# Now you can analyze with pandas
import pandas as pd
df = pd.read_csv(output_file)
print(df[['issn', 'if_value', 'quartile', 'h_index', 'source']])
```

### Example 5: Using Only OpenAlex (No SJR Data)

```python
from scholar_extention_trung.utils.impactFactorCollector import ImpactFactorCollector

# Initialize without SJR data - will use OpenAlex only
collector = ImpactFactorCollector(email="your-email@example.com")

# Query using OpenAlex
issn = "0028-0836"
if_data = collector.get_impact_factor(issn)

print(f"Source: {if_data['source']}")  # Will be 'openalex'
print(f"2yr Mean Citedness: {if_data['if_value']}")
print(f"H-index: {if_data['h_index']}")
```

### Example 6: Direct SJR Data Access

```python
from scholar_extention_trung.utils.impactFactorCollector import SJRDataLoader

# Load SJR data directly
loader = SJRDataLoader()
loader.load_sjr_csv("scholar_extention_trung/data/raw/scimagojr.csv")

# Get detailed metrics
metrics = loader.get_impact_metrics("0028-0836")

if metrics:
    print(f"Title: {metrics['title']}")
    print(f"SJR: {metrics['sjr']}")
    print(f"Quartile: {metrics['sjr_best_quartile']}")
    print(f"H-index: {metrics['h_index']}")
    print(f"Rank: {metrics['rank']}")
    print(f"Total Docs: {metrics['total_docs']}")
    print(f"Total Cites: {metrics['total_cites']}")
    print(f"Cites/Doc: {metrics['cites_per_doc']}")
    print(f"Country: {metrics['country']}")
    print(f"Publisher: {metrics['publisher']}")
```

### Example 7: Direct OpenAlex API Access

```python
from scholar_extention_trung.utils.impactFactorCollector import OpenAlexMetrics

# Initialize OpenAlex client
openalex = OpenAlexMetrics(email="your-email@example.com")

# Get citation metrics
metrics = openalex.get_citation_metrics("0028-0836")

if metrics:
    print(f"Journal: {metrics['display_name']}")
    print(f"Works Count: {metrics['works_count']}")
    print(f"Total Citations: {metrics['cited_by_count']}")
    print(f"2yr Mean Citedness: {metrics['cited_by_count_2yr_mean']}")
    print(f"H-index: {metrics['h_index']}")
    print(f"i10-index: {metrics['i10_index']}")
    print(f"Open Access: {metrics['is_oa']}")
    print(f"In DOAJ: {metrics['is_in_doaj']}")

# Get just the 2-year mean citedness
citedness = openalex.get_2yr_mean_citedness("0028-0836")
print(f"2yr Mean: {citedness}")
```

### Example 8: Processing ISSN List from File

```python
from scholar_extention_trung.utils.impactFactorCollector import ImpactFactorCollector
import pandas as pd

# Initialize collector
collector = ImpactFactorCollector(
    sjr_csv_path="scholar_extention_trung/data/raw/scimagojr.csv",
    email="your-email@example.com"
)

# Read ISSNs from CSV file
issn_df = pd.read_csv("scholar_extention_trung/data/ISSNs.csv")
issn_list = issn_df['ISSN'].tolist()

print(f"Processing {len(issn_list)} journals...")

# Batch collect with progress tracking
results = collector.batch_collect(issn_list)

# Export results
collector.export_to_js(results, "output/impact_factors.js")
collector.export_to_csv(results, "output/impact_factors.csv")

# Print statistics
sources = {}
for data in results.values():
    source = data['source']
    sources[source] = sources.get(source, 0) + 1

print("\nData Sources Breakdown:")
for source, count in sources.items():
    print(f"  {source}: {count} journals")
```

## API Reference

### ImpactFactorCollector

Main orchestrator class for collecting impact factors.

#### `__init__(sjr_csv_path=None, email=None)`

Initialize the collector.

- `sjr_csv_path`: Path to SJR CSV file (optional)
- `email`: Email for OpenAlex polite pool (optional, recommended)

#### `get_impact_factor(issn) -> Dict`

Get impact factor for a single ISSN.

**Returns:**
```python
{
    'if_value': float or None,
    'year': int or None,
    'source': str,  # 'sjr', 'openalex', or 'none'
    'quartile': str or None,  # 'Q1', 'Q2', 'Q3', 'Q4'
    'h_index': int or None,
    'alternative_metrics': dict  # Additional source-specific metrics
}
```

#### `batch_collect(issn_list) -> Dict[str, Dict]`

Batch process multiple ISSNs efficiently.

- `issn_list`: List of ISSN strings
- Returns: Dictionary mapping ISSN to impact factor data

#### `export_to_js(data_dict, output_file)`

Export data to JavaScript format for browser extensions.

#### `export_to_csv(data_dict, output_file)`

Export data to CSV format for analysis.

### SJRDataLoader

Load and parse ScimagoJR CSV data.

#### `load_sjr_csv(file_path) -> bool`

Load SJR CSV data. Returns True if successful.

#### `get_impact_metrics(issn) -> Dict or None`

Get comprehensive metrics for a journal.

**Returns:**
```python
{
    'title': str,
    'issn': str,
    'sjr': float,
    'sjr_best_quartile': str,
    'h_index': int,
    'total_docs': int,
    'total_refs': int,
    'total_cites': int,
    'cites_per_doc': float,
    'rank': int,
    'country': str,
    'publisher': str,
    'year': int
}
```

### OpenAlexMetrics

Fetch citation metrics from OpenAlex API.

#### `get_citation_metrics(issn) -> Dict or None`

Get comprehensive citation metrics.

#### `get_2yr_mean_citedness(issn) -> float or None`

Get 2-year mean citedness (Impact Factor proxy).

#### `batch_get_metrics(issn_list) -> Dict[str, Dict]`

Batch fetch metrics for multiple ISSNs.

## Data Priority Order

The collector uses the following priority order:

1. **SJR Data** (if available)
   - Most comprehensive
   - Includes quartile information
   - Includes detailed publication metrics

2. **OpenAlex** (fallback)
   - Uses 2-year mean citedness as IF proxy
   - Includes citation counts and H-index
   - Real-time data

3. **None** (no data found)
   - Returns empty/null values
   - Logs warning message

## ISSN Format

The module handles various ISSN formats:

- With hyphen: `0028-0836`
- Without hyphen: `00280836`
- With spaces: `0028 0836`
- Automatically normalized for lookup

## Error Handling

The module includes comprehensive error handling:

- File not found errors for SJR CSV
- API request failures with retry logic
- Invalid ISSN format validation
- Missing data graceful fallback
- Detailed logging at all levels

## Performance Considerations

- **SJR lookup**: O(1) using ISSN index
- **OpenAlex API**: Rate limited to 10 requests/second
- **Batch processing**: Progress logging every 50-100 journals
- **Caching**: Not implemented yet (future enhancement)

## Testing

Run the test suite:

```bash
cd scholar_extention_trung/utils
python test_impactFactorCollector.py
```

Run tests with coverage:

```bash
python -m pytest test_impactFactorCollector.py --cov=impactFactorCollector --cov-report=html
```

## Troubleshooting

### SJR CSV not loading

**Problem:** CSV file not found or invalid format

**Solution:**
1. Check file path is correct
2. Verify CSV delimiter (should be semicolon `;`)
3. Check encoding (UTF-8 or Latin-1)
4. Verify required columns exist

### OpenAlex API rate limiting

**Problem:** Getting 429 Too Many Requests errors

**Solution:**
1. Provide email parameter for polite pool
2. Increase `rate_limit_delay` in OpenAlexMetrics
3. Use batch processing with delays

### No data found for ISSN

**Problem:** `get_impact_factor()` returns source='none'

**Solution:**
1. Verify ISSN format is correct (8 digits)
2. Check if journal is in SJR database
3. Try direct OpenAlex lookup
4. Check if journal uses different ISSN variant

## Future Enhancements

- [ ] Caching mechanism for API results
- [ ] Database backend for persistent storage
- [ ] Additional data sources (Scopus, Web of Science)
- [ ] Async API calls for faster batch processing
- [ ] Historical impact factor tracking
- [ ] Journal metadata enrichment
- [ ] Web interface for interactive queries

## License

This module is part of the Scholar Extension project.

## Contact

For questions or issues, please contact the development team.
