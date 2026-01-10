# Journal List Aggregator

A Python module for fetching and aggregating journal metadata from multiple academic sources (OpenAlex and Crossref APIs).

## Features

- **OpenAlex API Integration**: Fetch comprehensive journal data with cursor pagination
- **Crossref API Integration**: Enrich journal metadata with additional information
- **Rate Limiting**: Respects API rate limits (10 requests/second)
- **Retry Logic**: Automatic retry with exponential backoff for failed requests
- **Deduplication**: Intelligent merging of duplicate journals by ISSN
- **Flexible Filtering**: Fetch journals by specific fields or get comprehensive lists
- **CSV Export**: Save results with optional timestamps

## Installation

Required dependencies are already in `requirements.txt`:

```bash
pip install pandas requests
```

The module uses Python's built-in `urllib3` which comes with `requests`.

## Quick Start

```python
from journalListAggregator import JournalAggregator

# Initialize aggregator (optionally with email for better rate limits)
aggregator = JournalAggregator(email="your-email@example.com")

# Fetch journals for a specific field
df = aggregator.fetch_by_field("machine learning", limit=500)

# Save to CSV
aggregator.save_to_csv(df, "ml_journals.csv")
```

## Classes

### 1. OpenAlexAPI

Fetch journals from OpenAlex API (https://api.openalex.org/venues)

**Methods:**

- `fetch_journals_by_field(field_name, limit=1000)`: Fetch journals for a specific field
- `fetch_all_journals(limit=10000)`: Fetch comprehensive journal list

**Features:**
- Cursor pagination for large datasets
- Extracts: journal name, ISSN, display_name, homepage_url, topics, citation counts
- Rate limiting: 10 requests/second
- Automatic retry on failures

**Example:**

```python
from journalListAggregator import OpenAlexAPI

openalex = OpenAlexAPI(email="your-email@example.com")

# Fetch computer science journals
df = openalex.fetch_journals_by_field("computer science", limit=200)

# Fetch all journals
df_all = openalex.fetch_all_journals(limit=5000)
```

### 2. CrossrefAPI

Fetch journals from Crossref API for enrichment

**Methods:**

- `fetch_journal_by_issn(issn)`: Get journal metadata by ISSN
- `enrich_journal_data(issn_list)`: Batch enrich multiple journals

**Features:**
- Extracts: title, ISSN, subjects, publisher
- Rate limiting and retry logic
- Useful for enriching OpenAlex data

**Example:**

```python
from journalListAggregator import CrossrefAPI

crossref = CrossrefAPI(email="your-email@example.com")

# Fetch single journal
journal = crossref.fetch_journal_by_issn("0028-0836")  # Nature

# Batch enrichment
issn_list = ["0028-0836", "0036-8075", "1476-4687"]
df = crossref.enrich_journal_data(issn_list)
```

### 3. JournalAggregator

Main orchestrator for fetching and aggregating journal data

**Methods:**

- `fetch_by_field(field_name, limit=1000, enrich_with_crossref=False)`: Get journals for a field
- `fetch_all_journals(limit=10000)`: Fetch comprehensive journal list
- `deduplicate_journals(df)`: Merge duplicates by ISSN
- `save_to_csv(df, filename, include_timestamp=True)`: Save results

**Example:**

```python
from journalListAggregator import JournalAggregator

aggregator = JournalAggregator(email="your-email@example.com")

# Fetch by field with Crossref enrichment
df = aggregator.fetch_by_field(
    "artificial intelligence",
    limit=500,
    enrich_with_crossref=True
)

# Deduplicate manually
df_clean = aggregator.deduplicate_journals(df)

# Save with timestamp
aggregator.save_to_csv(df_clean, "ai_journals.csv")
```

## Output DataFrame Structure

The resulting DataFrame contains the following columns:

| Column | Description | Source |
|--------|-------------|--------|
| `name` | Journal display name | OpenAlex/Crossref |
| `issn` | Journal ISSN(s), comma-separated | OpenAlex/Crossref |
| `field` | Subject field(s) or topics | OpenAlex/Crossref |
| `source` | Data source (OpenAlex/Crossref) | Both |
| `url` | Journal homepage URL | OpenAlex/Crossref |
| `publisher` | Publisher name | OpenAlex/Crossref |
| `works_count` | Number of published works | OpenAlex |
| `cited_by_count` | Total citations | OpenAlex |
| `topics` | Detailed topics, comma-separated | OpenAlex |
| `subjects` | Subject categories | Crossref |

## Advanced Usage

### Fetch Multiple Fields

```python
aggregator = JournalAggregator(email="your-email@example.com")

fields = ["machine learning", "data science", "bioinformatics"]
all_journals = []

for field in fields:
    df = aggregator.fetch_by_field(field, limit=100)
    all_journals.append(df)

# Combine and deduplicate
import pandas as pd
combined = pd.concat(all_journals, ignore_index=True)
combined = aggregator.deduplicate_journals(combined)

aggregator.save_to_csv(combined, "multi_field_journals.csv")
```

### Custom Rate Limiting

```python
from journalListAggregator import OpenAlexAPI, RateLimiter

# Create custom rate limiter (5 requests/second)
custom_limiter = RateLimiter(max_requests_per_second=5)

# Initialize API with custom settings
openalex = OpenAlexAPI(email="your-email@example.com")
openalex.rate_limiter = custom_limiter
```

### Filter and Sort Results

```python
aggregator = JournalAggregator(email="your-email@example.com")
df = aggregator.fetch_by_field("physics", limit=1000)

# Filter journals with high citation counts
if 'cited_by_count' in df.columns:
    high_impact = df[df['cited_by_count'] > 10000]

    # Sort by citations
    high_impact = high_impact.sort_values('cited_by_count', ascending=False)

    print(f"Found {len(high_impact)} high-impact journals")
    aggregator.save_to_csv(high_impact, "high_impact_physics.csv")
```

## Error Handling

The module includes comprehensive error handling:

- **Network Errors**: Automatic retry with exponential backoff
- **Rate Limiting**: Built-in rate limiter prevents hitting API limits
- **Invalid Data**: Graceful handling of missing or malformed data
- **Logging**: Detailed logging for debugging and monitoring

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

aggregator = JournalAggregator(email="your-email@example.com")
df = aggregator.fetch_by_field("neuroscience", limit=100)
```

## API Rate Limits

### OpenAlex
- **Without email**: ~100,000 requests/day
- **With email (polite pool)**: Higher limits and priority
- **Max rate**: 10 requests/second

### Crossref
- **Without email**: Limited
- **With email (polite pool)**: Better performance
- **Max rate**: Variable, module uses 10 requests/second

**Recommendation**: Always provide an email address for better performance.

## Best Practices

1. **Use Email**: Provide email address for polite pool access
2. **Start Small**: Test with small limits before fetching large datasets
3. **Deduplicate**: Always deduplicate results to avoid duplicate journals
4. **Save Incrementally**: For large fetches, save intermediate results
5. **Handle Errors**: Check for empty DataFrames before processing

## Troubleshooting

### Empty Results

```python
df = aggregator.fetch_by_field("rare_field", limit=100)

if df.empty:
    print("No journals found. Try a different field name or broader query.")
```

### Slow Performance

- Reduce the `limit` parameter
- Use field-specific queries instead of fetching all journals
- Ensure you're providing an email address
- Check your internet connection

### API Errors

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed API request/response information
```

## Examples

See `example_journal_aggregator.py` for comprehensive examples including:

- Fetching journals by field
- Fetching all journals
- Direct API usage
- Crossref enrichment
- Multiple field aggregation
- Filtering and sorting

Run examples:

```bash
python example_journal_aggregator.py
```

## License

This module is part of the Scholar Extension project.

## Contributing

When contributing, please ensure:

- Code follows existing style conventions
- Logging is used for debugging
- Error handling is comprehensive
- Documentation is updated
- Examples are provided for new features
