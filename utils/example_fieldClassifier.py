"""
Field Classifier - Practical Usage Examples

This file demonstrates real-world usage scenarios for the OECD Field Classifier,
including integration with journal databases, batch processing, and advanced
classification techniques.

Author: Scholar Extension Team
Date: January 10, 2026
"""

from fieldClassifier import FieldClassifier, classify_journal, get_field_info
import json


# ============================================================================
# Example 1: Basic Journal Classification
# ============================================================================

def example_1_basic_classification():
    """Example 1: Basic classification of well-known journals."""
    print("=" * 80)
    print("Example 1: Basic Journal Classification")
    print("=" * 80)

    classifier = FieldClassifier()

    # Test journals from different fields
    test_journals = [
        "Nature",
        "Science",
        "The Lancet",
        "Physical Review Letters",
        "Journal of Machine Learning Research",
        "Agricultural Economics",
        "American Economic Review",
        "Journal of Philosophy"
    ]

    print("\nClassifying well-known journals:\n")

    for journal_name in test_journals:
        results = classifier.classify_by_name(journal_name, top_n=2)

        print(f"Journal: {journal_name}")
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['field_name']} ({result['field_code']})")
                print(f"     Confidence: {result['confidence']:.2%}")
        else:
            print("  No classification found (may be multidisciplinary)")
        print()


# ============================================================================
# Example 2: Topic-Based Classification with OpenAlex Integration
# ============================================================================

def example_2_openalex_integration():
    """Example 2: Classify using OpenAlex-style topics."""
    print("=" * 80)
    print("Example 2: OpenAlex Topic Integration")
    print("=" * 80)

    classifier = FieldClassifier()

    # Simulated OpenAlex journal data
    openalex_journals = [
        {
            "name": "Nature Machine Intelligence",
            "topics": [
                "Machine learning",
                "Artificial intelligence",
                "Neural networks",
                "Deep learning"
            ]
        },
        {
            "name": "Cell Stem Cell",
            "topics": [
                "Stem cells",
                "Regenerative medicine",
                "Cell biology",
                "Developmental biology"
            ]
        },
        {
            "name": "Energy & Environmental Science",
            "topics": [
                "Renewable energy",
                "Environmental science",
                "Climate change",
                "Sustainability"
            ]
        }
    ]

    print("\nClassifying journals with topic information:\n")

    for journal in openalex_journals:
        results = classifier.classify_multi_method(
            journal_name=journal['name'],
            topics_list=journal['topics'],
            top_n=2
        )

        print(f"Journal: {journal['name']}")
        print(f"Topics: {', '.join(journal['topics'][:3])}...")
        print(f"Methods used: {', '.join(results['methods_used'])}")
        print("Classifications:")

        for i, result in enumerate(results['classifications'], 1):
            print(f"  {i}. {result['field_name']}")
            print(f"     Code: {result['field_code']}")
            print(f"     Confidence: {result['aggregated_confidence']:.2%}")
        print()


# ============================================================================
# Example 3: ISSN Database Lookup
# ============================================================================

def example_3_issn_lookup():
    """Example 3: Using ISSN database for exact classification."""
    print("=" * 80)
    print("Example 3: ISSN Database Lookup")
    print("=" * 80)

    classifier = FieldClassifier()

    # Sample ISSN database (in real use, load from file/database)
    issn_database = {
        '0028-0836': ['1.3', '1.6'],  # Nature: Physics & Biology
        '0036-8075': ['1.3', '1.6'],  # Science: Multidisciplinary
        '0140-6736': ['3.2'],          # The Lancet: Clinical Medicine
        '1476-4687': ['1.6', '3.4'],   # Nature Biotechnology
        '2041-1723': ['1.3', '1.6'],   # Nature Communications
        '0092-8674': ['1.6'],          # Cell: Biology
    }

    print("\nLooking up journals by ISSN:\n")

    for issn, field_codes in issn_database.items():
        results = classifier.classify_by_issn(issn, issn_database)

        print(f"ISSN: {issn}")
        print(f"Expected fields: {field_codes}")
        print("Found classifications:")

        for result in results:
            print(f"  - {result['field_name']} ({result['field_code']})")
            print(f"    Confidence: {result['confidence']:.2%}")
        print()


# ============================================================================
# Example 4: Batch Processing with Progress Tracking
# ============================================================================

def example_4_batch_processing():
    """Example 4: Process large journal list efficiently."""
    print("=" * 80)
    print("Example 4: Batch Processing")
    print("=" * 80)

    classifier = FieldClassifier()

    # Simulated large journal dataset
    journal_dataset = [
        {"id": 1, "name": "IEEE Transactions on Pattern Analysis"},
        {"id": 2, "name": "Journal of Biological Chemistry"},
        {"id": 3, "name": "Agricultural and Forest Meteorology"},
        {"id": 4, "name": "Journal of Economic Literature"},
        {"id": 5, "name": "Historical Studies in the Natural Sciences"},
        {"id": 6, "name": "Mechanical Systems and Signal Processing"},
        {"id": 7, "name": "Veterinary Pathology"},
        {"id": 8, "name": "Philosophy of Science"},
        {"id": 9, "name": "Energy Policy"},
        {"id": 10, "name": "Clinical Microbiology Reviews"},
    ]

    print(f"\nProcessing {len(journal_dataset)} journals...\n")

    # Store results
    classified_journals = []

    for journal in journal_dataset:
        results = classifier.classify_by_name(journal['name'], top_n=1)

        if results:
            primary_field = results[0]
            journal['oecd_field'] = primary_field['field_code']
            journal['oecd_field_name'] = primary_field['field_name']
            journal['confidence'] = primary_field['confidence']
        else:
            journal['oecd_field'] = None
            journal['oecd_field_name'] = 'Unclassified'
            journal['confidence'] = 0.0

        classified_journals.append(journal)

        # Progress indicator
        print(f"[{journal['id']:2d}/10] {journal['name']:50} → "
              f"{journal['oecd_field_name']}")

    # Summary statistics
    print("\n" + "-" * 80)
    print("Summary Statistics:")
    print("-" * 80)

    classified_count = sum(1 for j in classified_journals if j['oecd_field'])
    avg_confidence = sum(j['confidence'] for j in classified_journals) / len(classified_journals)

    print(f"Total journals: {len(classified_journals)}")
    print(f"Successfully classified: {classified_count}")
    print(f"Unclassified: {len(classified_journals) - classified_count}")
    print(f"Average confidence: {avg_confidence:.2%}")


# ============================================================================
# Example 5: Field Hierarchy Navigation
# ============================================================================

def example_5_field_hierarchy():
    """Example 5: Navigate OECD field hierarchy."""
    print("=" * 80)
    print("Example 5: Field Hierarchy Navigation")
    print("=" * 80)

    classifier = FieldClassifier()

    print("\nExploring Natural Sciences (Field 1):\n")

    # Get major field
    major_field = classifier.get_field_hierarchy('1')

    print(f"Major Field: {major_field['field_name']}")
    print(f"Sub-fields ({len(major_field['children'])}):")

    for child in major_field['children']:
        print(f"  {child['field_code']}: {child['field_name']}")

    print("\n" + "-" * 80)
    print("\nExploring Computer Science (Field 1.2):\n")

    # Get sub-field details
    sub_field = classifier.get_field_hierarchy('1.2')

    print(f"Sub-field: {sub_field['field_name']}")
    print(f"Code: {sub_field['field_code']}")
    print(f"Parent: {sub_field['parent']['field_name']}")
    print(f"\nSibling fields ({len(sub_field['siblings'])}):")

    for sibling in sub_field['siblings']:
        print(f"  {sibling['field_code']}: {sibling['field_name']}")


# ============================================================================
# Example 6: Multi-Method Classification with Confidence Comparison
# ============================================================================

def example_6_confidence_comparison():
    """Example 6: Compare confidence across different methods."""
    print("=" * 80)
    print("Example 6: Multi-Method Confidence Comparison")
    print("=" * 80)

    classifier = FieldClassifier()

    # Test journal
    journal_name = "Nature Biotechnology"
    topics = ["biotechnology", "genetics", "molecular biology"]
    issn = "1546-1696"

    issn_db = {
        "1546-1696": ['1.6', '3.4']  # Biology & Medical Biotechnology
    }

    print(f"\nJournal: {journal_name}\n")

    # Method 1: Name only
    print("Method 1: Name-based classification")
    name_results = classifier.classify_by_name(journal_name, top_n=2)
    for result in name_results:
        print(f"  {result['field_name']}: {result['confidence']:.2%}")

    # Method 2: Topics only
    print("\nMethod 2: Topic-based classification")
    topic_results = classifier.classify_by_topics(topics, top_n=2)
    for result in topic_results:
        print(f"  {result['field_name']}: {result['confidence']:.2%}")

    # Method 3: ISSN only
    print("\nMethod 3: ISSN lookup")
    issn_results = classifier.classify_by_issn(issn, issn_db)
    for result in issn_results:
        print(f"  {result['field_name']}: {result['confidence']:.2%}")

    # Method 4: Combined
    print("\nMethod 4: Multi-method (combined)")
    multi_results = classifier.classify_multi_method(
        journal_name=journal_name,
        topics_list=topics,
        issn=issn,
        issn_database=issn_db,
        top_n=3
    )

    print(f"Methods used: {', '.join(multi_results['methods_used'])}")
    for result in multi_results['classifications']:
        print(f"  {result['field_name']}: {result['aggregated_confidence']:.2%}")


# ============================================================================
# Example 7: Field Search and Filtering
# ============================================================================

def example_7_search_and_filter():
    """Example 7: Search for specific fields and filter results."""
    print("=" * 80)
    print("Example 7: Field Search and Filtering")
    print("=" * 80)

    classifier = FieldClassifier()

    # Search for engineering fields
    print("\nSearch query: 'engineering'\n")
    engineering_fields = classifier.search_fields("engineering")

    for field in engineering_fields:
        print(f"  {field['field_code']}: {field['field_name']} [{field['level']}]")

    # Search for medical fields
    print("\n" + "-" * 80)
    print("\nSearch query: 'medical'\n")
    medical_fields = classifier.search_fields("medical")

    for field in medical_fields:
        print(f"  {field['field_code']}: {field['field_name']} [{field['level']}]")

    # Get all fields in a major category
    print("\n" + "-" * 80)
    print("\nAll Medical and Health Sciences (Field 3):\n")

    medical_hierarchy = classifier.get_field_hierarchy('3')
    for child in medical_hierarchy['children']:
        print(f"  {child['field_code']}: {child['field_name']}")


# ============================================================================
# Example 8: Export Classifications to JSON
# ============================================================================

def example_8_export_to_json():
    """Example 8: Export classification results to JSON format."""
    print("=" * 80)
    print("Example 8: Export Classifications to JSON")
    print("=" * 80)

    classifier = FieldClassifier()

    # Classify multiple journals
    journals = [
        "Nature",
        "Cell",
        "The Lancet",
        "IEEE Transactions on Computers"
    ]

    export_data = []

    for journal_name in journals:
        results = classifier.classify_by_name(journal_name, top_n=2)

        journal_data = {
            "journal_name": journal_name,
            "classifications": [
                {
                    "field_code": r['field_code'],
                    "field_name": r['field_name'],
                    "major_field": r['major_field_name'],
                    "confidence": r['confidence']
                }
                for r in results
            ]
        }

        export_data.append(journal_data)

    # Convert to JSON
    json_output = json.dumps(export_data, indent=2)

    print("\nJSON Export:\n")
    print(json_output)


# ============================================================================
# Example 9: Statistical Analysis of Classifications
# ============================================================================

def example_9_statistical_analysis():
    """Example 9: Analyze classification distribution across fields."""
    print("=" * 80)
    print("Example 9: Statistical Analysis")
    print("=" * 80)

    classifier = FieldClassifier()

    # Large sample of journals
    journals = [
        "Nature", "Science", "Cell", "The Lancet", "JAMA",
        "Physical Review Letters", "Journal of Chemical Physics",
        "IEEE Transactions on Pattern Analysis", "ACM Computing Surveys",
        "Agricultural Economics", "Animal Science Journal",
        "American Economic Review", "Journal of Finance",
        "Philosophy of Science", "Journal of the History of Ideas"
    ]

    # Classify all journals
    field_counts = {}
    major_field_counts = {}

    print("\nClassifying sample journals...\n")

    for journal_name in journals:
        results = classifier.classify_by_name(journal_name, top_n=1)

        if results:
            field_code = results[0]['field_code']
            major_code = results[0]['major_field_code']

            # Count sub-fields
            field_counts[field_code] = field_counts.get(field_code, 0) + 1

            # Count major fields
            major_field_counts[major_code] = major_field_counts.get(major_code, 0) + 1

    # Display statistics
    print("Distribution by Major Field:")
    print("-" * 80)

    for code in sorted(major_field_counts.keys()):
        count = major_field_counts[code]
        percentage = (count / len(journals)) * 100
        field_name = classifier.MAJOR_FIELDS[code]
        bar = "█" * int(percentage / 5)  # Scale for display

        print(f"{code}. {field_name:35} {count:2d} ({percentage:5.1f}%) {bar}")

    print(f"\nTotal journals analyzed: {len(journals)}")
    print(f"Successfully classified: {sum(field_counts.values())}")


# ============================================================================
# Example 10: Building an ISSN Database
# ============================================================================

def example_10_build_issn_database():
    """Example 10: Create and populate an ISSN classification database."""
    print("=" * 80)
    print("Example 10: Building ISSN Database")
    print("=" * 80)

    classifier = FieldClassifier()

    # Sample journals with known fields
    known_journals = [
        {
            "name": "Nature",
            "issn": "0028-0836",
            "topics": ["multidisciplinary science"]
        },
        {
            "name": "Cell",
            "issn": "0092-8674",
            "topics": ["cell biology", "molecular biology"]
        },
        {
            "name": "The Lancet",
            "issn": "0140-6736",
            "topics": ["clinical medicine", "public health"]
        }
    ]

    # Build database
    issn_database = {}

    print("\nBuilding ISSN → Field mapping database:\n")

    for journal in known_journals:
        # Classify using available information
        results = classifier.classify_multi_method(
            journal_name=journal['name'],
            topics_list=journal['topics'],
            top_n=3
        )

        # Extract field codes with high confidence
        field_codes = [
            r['field_code']
            for r in results['classifications']
            if r['aggregated_confidence'] >= 0.5
        ]

        if field_codes:
            issn_database[journal['issn']] = field_codes
            print(f"ISSN {journal['issn']} ({journal['name']})")
            print(f"  Fields: {', '.join(field_codes)}")
            field_names = [classifier.SUB_FIELDS[code] for code in field_codes]
            print(f"  Names: {', '.join(field_names)}")
            print()

    # Export database
    print("\n" + "-" * 80)
    print("Database Export (JSON):")
    print("-" * 80)
    print(json.dumps(issn_database, indent=2))


# ============================================================================
# Main Execution
# ============================================================================

def run_all_examples():
    """Run all example functions."""
    examples = [
        example_1_basic_classification,
        example_2_openalex_integration,
        example_3_issn_lookup,
        example_4_batch_processing,
        example_5_field_hierarchy,
        example_6_confidence_comparison,
        example_7_search_and_filter,
        example_8_export_to_json,
        example_9_statistical_analysis,
        example_10_build_issn_database
    ]

    for i, example_func in enumerate(examples, 1):
        example_func()
        if i < len(examples):
            print("\n" * 2)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "OECD Field Classifier Examples" + " " * 28 + "║")
    print("║" + " " * 25 + "Practical Usage Guide" + " " * 33 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    run_all_examples()

    print("\n")
    print("=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)
