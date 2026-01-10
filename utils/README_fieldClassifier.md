# Field Classifier Module Documentation

## Overview

The `fieldClassifier.py` module implements a comprehensive journal field classification system based on the **OECD Fields of Science and Technology** standard. This module provides multiple classification methods to categorize academic journals into 6 major fields and 42 specialized sub-fields.

## Table of Contents

1. [OECD Classification Schema](#oecd-classification-schema)
2. [Installation & Setup](#installation--setup)
3. [Quick Start](#quick-start)
4. [Class Reference](#class-reference)
5. [Classification Methods](#classification-methods)
6. [Usage Examples](#usage-examples)
7. [Performance & Best Practices](#performance--best-practices)
8. [Testing](#testing)

---

## OECD Classification Schema

### Major Fields (6 Categories)

| Code | Field Name |
|------|-----------|
| 1 | Natural Sciences |
| 2 | Engineering and Technology |
| 3 | Medical and Health Sciences |
| 4 | Agricultural Sciences |
| 5 | Social Sciences |
| 6 | Humanities |

### Sub-Fields (42 Categories)

#### 1. Natural Sciences
- **1.1** Mathematics
- **1.2** Computer and information sciences
- **1.3** Physical sciences
- **1.4** Chemical sciences
- **1.5** Earth and related environmental sciences
- **1.6** Biological sciences
- **1.7** Other natural sciences

#### 2. Engineering and Technology
- **2.1** Civil engineering
- **2.2** Electrical, electronic, information engineering
- **2.3** Mechanical engineering
- **2.4** Chemical engineering
- **2.5** Materials engineering
- **2.6** Medical engineering
- **2.7** Environmental engineering
- **2.8** Environmental biotechnology
- **2.9** Industrial biotechnology
- **2.10** Nano-technology
- **2.11** Other engineering

#### 3. Medical and Health Sciences
- **3.1** Basic medicine
- **3.2** Clinical medicine
- **3.3** Health sciences
- **3.4** Medical biotechnology
- **3.5** Other medical sciences

#### 4. Agricultural Sciences
- **4.1** Agriculture, forestry, fisheries
- **4.2** Animal and dairy science
- **4.3** Veterinary science
- **4.4** Agricultural biotechnology
- **4.5** Other agricultural sciences

#### 5. Social Sciences
- **5.1** Psychology
- **5.2** Economics and business
- **5.3** Educational sciences
- **5.4** Sociology
- **5.5** Law
- **5.6** Political science
- **5.7** Social and economic geography
- **5.8** Media and communications
- **5.9** Other social sciences

#### 6. Humanities
- **6.1** History and archaeology
- **6.2** Languages and literature
- **6.3** Philosophy, ethics, religion
- **6.4** Arts
- **6.5** Other humanities

---

## Installation & Setup

### Requirements
- Python 3.6 or higher
- No external dependencies required (uses only standard library)

### Installation
```python
# Simply place fieldClassifier.py in your project directory
from fieldClassifier import FieldClassifier
```

---

## Quick Start

### Basic Classification

```python
from fieldClassifier import FieldClassifier, classify_journal

# Method 1: Using convenience function
results = classify_journal("Journal of Machine Learning Research")

# Method 2: Using the classifier class
classifier = FieldClassifier()
results = classifier.classify_by_name("Nature Physics")

# Display results
for result in results:
    print(f"{result['field_name']} ({result['field_code']})")
    print(f"Confidence: {result['confidence']:.2%}")
```

---

## Class Reference

### FieldClassifier

Main class for journal field classification.

#### Methods

##### `__init__()`
Initialize the classifier with pre-compiled keyword patterns.

```python
classifier = FieldClassifier()
```

##### `classify_by_name(journal_name, top_n=3, min_confidence=0.1)`
Classify journal based on keywords in journal name.

**Parameters:**
- `journal_name` (str): Name/title of the journal
- `top_n` (int): Maximum number of classifications to return (default: 3)
- `min_confidence` (float): Minimum confidence threshold 0-1 (default: 0.1)

**Returns:**
- List of classification dictionaries containing:
  - `field_code`: OECD field code (e.g., '1.2')
  - `field_name`: Full name of the field
  - `major_field_code`: Major field code (e.g., '1')
  - `major_field_name`: Major field name
  - `confidence`: Confidence score (0-1)
  - `matched_keywords`: List of matched keywords

**Example:**
```python
results = classifier.classify_by_name("IEEE Transactions on Neural Networks")
# Returns: Computer and information sciences (1.2) with high confidence
```

##### `classify_by_topics(topics_list, top_n=3, min_confidence=0.1)`
Classify journal based on OpenAlex topics or subject keywords.

**Parameters:**
- `topics_list` (List[str]): List of topic strings or keywords
- `top_n` (int): Maximum results to return (default: 3)
- `min_confidence` (float): Minimum confidence threshold (default: 0.1)

**Returns:**
- List of classification dictionaries (same structure as `classify_by_name`)

**Example:**
```python
topics = ["machine learning", "neural networks", "AI"]
results = classifier.classify_by_topics(topics)
```

##### `classify_by_issn(issn, issn_database)`
Look up field classification from ISSN→field mapping database.

**Parameters:**
- `issn` (str): ISSN identifier (with or without hyphen)
- `issn_database` (Dict[str, List[str]]): Dictionary mapping ISSNs to field codes

**Returns:**
- List of classification dictionaries with confidence 1.0

**Example:**
```python
issn_db = {'0028-0836': ['1.3', '1.6']}  # Nature journal
results = classifier.classify_by_issn('0028-0836', issn_db)
```

##### `classify_multi_method(journal_name=None, topics_list=None, issn=None, issn_database=None, top_n=3)`
Combine multiple classification methods for best results.

**Parameters:**
- `journal_name` (str): Journal name/title (optional)
- `topics_list` (List[str]): List of topics (optional)
- `issn` (str): ISSN identifier (optional)
- `issn_database` (Dict): ISSN mapping database (optional)
- `top_n` (int): Maximum results to return (default: 3)

**Returns:**
- Dictionary containing:
  - `classifications`: Combined and ranked field classifications
  - `methods_used`: List of methods that contributed
  - `total_methods`: Number of methods used

**Example:**
```python
results = classifier.classify_multi_method(
    journal_name="Nature Biotechnology",
    topics_list=["biotechnology", "genetics"],
    issn="1476-4687"
)
```

##### `get_field_hierarchy(field_code)`
Get parent/child relationships for a field code.

**Parameters:**
- `field_code` (str): OECD field code (e.g., '1.2' or '1')

**Returns:**
- Dictionary containing:
  - `field_code`: The input field code
  - `field_name`: Name of the field
  - `level`: 'major' or 'sub'
  - `parent`: Parent field info (if sub-field)
  - `children`: List of child fields (if major field)
  - `siblings`: List of sibling fields (if sub-field)

**Example:**
```python
hierarchy = classifier.get_field_hierarchy('1.2')
print(hierarchy['parent']['field_name'])  # "Natural Sciences"
```

##### `validate_field_code(field_code)`
Validate if a field code exists in OECD schema.

**Parameters:**
- `field_code` (str): Field code to validate

**Returns:**
- `True` if valid, `False` otherwise

**Example:**
```python
classifier.validate_field_code('1.2')  # True
classifier.validate_field_code('99.99')  # False
```

##### `get_all_fields(level='all')`
Get all field codes and names.

**Parameters:**
- `level` (str): 'major', 'sub', or 'all' (default: 'all')

**Returns:**
- Dictionary of field codes and names

**Example:**
```python
major_fields = classifier.get_all_fields(level='major')  # Returns 6 fields
sub_fields = classifier.get_all_fields(level='sub')  # Returns 42 fields
```

##### `search_fields(query)`
Search for fields by name or keyword.

**Parameters:**
- `query` (str): Search query string

**Returns:**
- List of matching fields with codes and names

**Example:**
```python
results = classifier.search_fields("computer")
# Returns: Computer and information sciences (1.2)
```

---

## Classification Methods

### Method Comparison

| Method | Input | Confidence | Use Case |
|--------|-------|-----------|----------|
| **ISSN Lookup** | ISSN code | 1.0 (exact) | When ISSN is available |
| **Topic Classification** | Topic list | 0.0-1.0 | OpenAlex topics, subject keywords |
| **Name Classification** | Journal name | 0.0-1.0 | Journal title analysis |
| **Multi-Method** | All of above | Weighted average | Best overall accuracy |

### Confidence Scoring

Confidence scores range from 0.0 to 1.0:
- **1.0**: Exact match (ISSN database lookup)
- **0.7-1.0**: Strong match (multiple keyword matches)
- **0.4-0.7**: Moderate match (some keyword matches)
- **0.1-0.4**: Weak match (minimal keyword matches)
- **< 0.1**: Filtered out by default

### Multi-Method Weighting

When using `classify_multi_method()`, confidence scores are weighted:
- **ISSN Lookup**: 1.0x weight (highest priority)
- **Topic Classification**: 0.7x weight
- **Name Classification**: 0.5x weight

---

## Usage Examples

### Example 1: Simple Classification

```python
from fieldClassifier import FieldClassifier

classifier = FieldClassifier()

# Classify a computer science journal
results = classifier.classify_by_name("Journal of Machine Learning Research")

for result in results:
    print(f"Field: {result['field_name']}")
    print(f"Code: {result['field_code']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Keywords: {', '.join(result['matched_keywords'])}")
    print()
```

**Output:**
```
Field: Computer and information sciences
Code: 1.2
Confidence: 45.00%
Keywords: machine learning
```

### Example 2: Topic-Based Classification

```python
# Classify based on research topics
topics = [
    "machine learning",
    "neural networks",
    "deep learning",
    "artificial intelligence"
]

results = classifier.classify_by_topics(topics, top_n=2)

for result in results:
    print(f"{result['field_name']} - {result['confidence']:.2%}")
```

**Output:**
```
Computer and information sciences - 85.00%
Electrical, electronic, information engineering - 35.00%
```

### Example 3: ISSN Lookup

```python
# Build ISSN database (example)
issn_database = {
    '0028-0836': ['1.3', '1.6'],  # Nature: Physics & Biology
    '0036-8075': ['1.3', '1.6'],  # Science: Multi-disciplinary
    '1476-4687': ['1.6', '3.4'],  # Nature Biotechnology
}

# Classify by ISSN
results = classifier.classify_by_issn('0028-0836', issn_database)

for result in results:
    print(f"{result['field_name']} ({result['confidence']:.2%})")
```

**Output:**
```
Physical sciences (100.00%)
Biological sciences (100.00%)
```

### Example 4: Multi-Method Classification

```python
# Combine all methods for best accuracy
results = classifier.classify_multi_method(
    journal_name="Nature Genetics",
    topics_list=["genetics", "genomics", "molecular biology"],
    issn="1061-4036",
    issn_database=issn_database,
    top_n=3
)

print(f"Methods used: {', '.join(results['methods_used'])}")
print(f"\nTop classifications:")

for i, result in enumerate(results['classifications'], 1):
    print(f"{i}. {result['field_name']}")
    print(f"   Confidence: {result['aggregated_confidence']:.2%}")
```

### Example 5: Field Hierarchy Navigation

```python
# Get field hierarchy
hierarchy = classifier.get_field_hierarchy('1.2')

print(f"Current Field: {hierarchy['field_name']}")
print(f"Parent: {hierarchy['parent']['field_name']}")
print(f"\nSibling fields:")
for sibling in hierarchy['siblings']:
    print(f"  - {sibling['field_name']} ({sibling['field_code']})")
```

**Output:**
```
Current Field: Computer and information sciences
Parent: Natural Sciences

Sibling fields:
  - Mathematics (1.1)
  - Physical sciences (1.3)
  - Chemical sciences (1.4)
  - Earth and related environmental sciences (1.5)
  - Biological sciences (1.6)
  - Other natural sciences (1.7)
```

### Example 6: Batch Processing

```python
# Classify multiple journals
journals = [
    "Nature",
    "Science",
    "Cell",
    "The Lancet",
    "Physical Review Letters",
    "Journal of the American Chemical Society"
]

for journal_name in journals:
    results = classifier.classify_by_name(journal_name, top_n=1)

    if results:
        result = results[0]
        print(f"{journal_name:50} → {result['field_name']}")
    else:
        print(f"{journal_name:50} → Not classified")
```

### Example 7: Search and Filter

```python
# Search for specific fields
engineering_fields = classifier.search_fields("engineering")

print("Engineering-related fields:")
for field in engineering_fields:
    print(f"  {field['field_code']}: {field['field_name']}")

# Get all sub-fields in a major category
all_natural_sciences = [
    (code, name) for code, name in classifier.SUB_FIELDS.items()
    if code.startswith('1.')
]

print(f"\nNatural Sciences sub-fields: {len(all_natural_sciences)}")
```

---

## Performance & Best Practices

### Performance Characteristics

- **Initialization**: < 10ms (one-time regex compilation)
- **Name Classification**: 1-5ms per journal
- **Topic Classification**: 1-5ms per journal
- **ISSN Lookup**: < 1ms per journal
- **Multi-Method**: 5-15ms per journal

### Best Practices

#### 1. Reuse Classifier Instance
```python
# Good: Create once, use many times
classifier = FieldClassifier()
for journal in journal_list:
    results = classifier.classify_by_name(journal)

# Bad: Creating new instance each time (slower)
for journal in journal_list:
    classifier = FieldClassifier()  # Don't do this!
    results = classifier.classify_by_name(journal)
```

#### 2. Use Multi-Method for Best Accuracy
```python
# Best: Combine all available information
results = classifier.classify_multi_method(
    journal_name=name,
    topics_list=topics,
    issn=issn,
    issn_database=db
)
```

#### 3. Adjust Confidence Threshold
```python
# For high precision (fewer results, more accurate)
results = classifier.classify_by_name(name, min_confidence=0.5)

# For high recall (more results, some false positives)
results = classifier.classify_by_name(name, min_confidence=0.1)
```

#### 4. Limit Results with top_n
```python
# Get only the top match
results = classifier.classify_by_name(name, top_n=1)

# Get top 3 matches
results = classifier.classify_by_name(name, top_n=3)
```

#### 5. Handle Multi-Field Journals
```python
# Some journals span multiple fields
results = classifier.classify_by_name("Nature", top_n=5)

# Check if journal is multidisciplinary
if len(results) >= 3:
    print("Multidisciplinary journal")
```

### Common Patterns

#### Pattern 1: Classification Pipeline
```python
def classify_journal_pipeline(journal_data):
    """Complete journal classification pipeline."""
    classifier = FieldClassifier()

    # Try ISSN first (most accurate)
    if 'issn' in journal_data:
        results = classifier.classify_by_issn(
            journal_data['issn'],
            issn_database
        )
        if results:
            return results

    # Fall back to multi-method
    return classifier.classify_multi_method(
        journal_name=journal_data.get('name'),
        topics_list=journal_data.get('topics')
    )
```

#### Pattern 2: Confidence-Based Decision
```python
def get_primary_field(journal_name):
    """Get primary field with confidence check."""
    classifier = FieldClassifier()
    results = classifier.classify_by_name(journal_name, top_n=1)

    if results and results[0]['confidence'] >= 0.5:
        return results[0]['field_code']
    else:
        return None  # Not confident enough
```

#### Pattern 3: Field Validation
```python
def validate_and_classify(journal_name, expected_field):
    """Validate classification against expected field."""
    classifier = FieldClassifier()
    results = classifier.classify_by_name(journal_name)

    field_codes = [r['field_code'] for r in results]

    # Check if expected field is in results
    if expected_field in field_codes:
        return True, "Match found"

    # Check if in same major field
    expected_major = expected_field.split('.')[0]
    for code in field_codes:
        if code.startswith(expected_major):
            return True, "Same major field"

    return False, "No match"
```

---

## Testing

### Running Tests

```bash
# Run all tests
python test_fieldClassifier.py

# Run specific test class
python -m unittest test_fieldClassifier.TestClassifyByName

# Run with verbose output
python test_fieldClassifier.py -v
```

### Test Coverage

The test suite includes:
- **65 unit tests** covering all major functionality
- Initialization tests (6 tests)
- Name-based classification tests (11 tests)
- Topic-based classification tests (6 tests)
- ISSN-based classification tests (8 tests)
- Field hierarchy tests (6 tests)
- Multi-method classification tests (6 tests)
- Validation and utility tests (9 tests)
- Convenience function tests (3 tests)
- Edge case tests (5 tests)
- Real-world scenario tests (5 tests)

### Test Results

```
==================================================================================
Test Summary:
  Tests run: 65
  Successes: 65
  Failures: 0
  Errors: 0
==================================================================================
```

---

## Keyword Coverage

### Comprehensive Keyword Database

The classifier includes **600+ keywords** across all 42 sub-fields:

- **Natural Sciences**: 150+ keywords
- **Engineering**: 120+ keywords
- **Medical Sciences**: 100+ keywords
- **Agricultural Sciences**: 50+ keywords
- **Social Sciences**: 110+ keywords
- **Humanities**: 70+ keywords

### Adding Custom Keywords

To extend the keyword database:

```python
# Extend the classifier's keywords
classifier = FieldClassifier()

# Add custom keywords to Computer Science (1.2)
custom_keywords = ['quantum computing', 'blockchain', 'IoT']
classifier.FIELD_KEYWORDS['1.2'].extend(custom_keywords)

# Recompile patterns
classifier.keyword_patterns = classifier._compile_keyword_patterns()
```

---

## Integration Examples

### Integration with OpenAlex API

```python
from fieldClassifier import FieldClassifier

def enrich_openalex_journals(openalex_results):
    """Add OECD field classifications to OpenAlex results."""
    classifier = FieldClassifier()

    for journal in openalex_results:
        # Extract topics from OpenAlex
        topics = [topic['display_name'] for topic in journal.get('topics', [])]

        # Classify using topics and name
        classification = classifier.classify_multi_method(
            journal_name=journal['display_name'],
            topics_list=topics
        )

        # Add to journal data
        journal['oecd_fields'] = classification['classifications']

    return openalex_results
```

### Integration with Crossref API

```python
def classify_crossref_journal(crossref_data):
    """Classify journal from Crossref metadata."""
    classifier = FieldClassifier()

    # Extract relevant data
    title = crossref_data.get('title')
    issn = crossref_data.get('ISSN', [None])[0]
    subjects = crossref_data.get('subject', [])

    # Classify
    results = classifier.classify_multi_method(
        journal_name=title,
        topics_list=subjects,
        issn=issn,
        issn_database=issn_db  # Your ISSN database
    )

    return results
```

---

## Troubleshooting

### Issue: Low Confidence Scores

**Solution**: Combine multiple methods or adjust min_confidence threshold

```python
# Use multi-method for better confidence
results = classifier.classify_multi_method(
    journal_name=name,
    topics_list=topics
)
```

### Issue: No Results Returned

**Solution**: Lower the min_confidence threshold or check input data

```python
# Lower threshold
results = classifier.classify_by_name(name, min_confidence=0.05)

# Check if input is valid
if not name or not isinstance(name, str):
    print("Invalid input")
```

### Issue: Too Many Results

**Solution**: Increase min_confidence or reduce top_n

```python
# More restrictive
results = classifier.classify_by_name(
    name,
    top_n=1,
    min_confidence=0.5
)
```

---

## File Locations

All files are located in:
```
/Users/trungnvm/Documents/MACBOOK_DOCUMENTS/0_0.AI_github/2. Extention scholar/scholar_extention_trung/utils/
```

- `fieldClassifier.py` - Main implementation (1000+ lines)
- `test_fieldClassifier.py` - Unit tests (700+ lines)
- `README_fieldClassifier.md` - This documentation

---

## Version & License

- **Version**: 1.0.0
- **Date**: January 10, 2026
- **Author**: Scholar Extension Team
- **Python**: 3.6+

---

## Summary

The Field Classifier module provides:
- ✅ Complete OECD classification (6 major fields, 42 sub-fields)
- ✅ Multiple classification methods (name, topics, ISSN, multi-method)
- ✅ Confidence scoring (0-1 scale)
- ✅ Multi-field support
- ✅ Field hierarchy navigation
- ✅ 600+ keywords across all fields
- ✅ Comprehensive test coverage (65 tests, 100% pass rate)
- ✅ High performance (< 15ms per classification)
- ✅ No external dependencies

**Ready for production use!**
