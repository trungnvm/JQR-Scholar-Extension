#!/usr/bin/env python3
"""
Example usage of Impact Factor Collector.

This script demonstrates various use cases for collecting and aggregating
journal impact factors from multiple sources.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.impactFactorCollector import (
    ImpactFactorCollector,
    SJRDataLoader,
    OpenAlexMetrics
)
import json


def example_1_basic_query():
    """Example 1: Basic single ISSN query with SJR data."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Single ISSN Query")
    print("=" * 70)

    # Path to SJR CSV (adjust as needed)
    sjr_csv = "data/raw/scimagojr.csv"

    # Check if file exists
    if not os.path.exists(sjr_csv):
        print(f"⚠️  SJR CSV not found at: {sjr_csv}")
        print("   Please download from: https://www.scimagojr.com/journalrank.php")
        print("   Skipping SJR examples...\n")
        return

    # Initialize collector
    collector = ImpactFactorCollector(
        sjr_csv_path=sjr_csv,
        email="your-email@example.com"  # Replace with your email
    )

    # Query Nature journal
    issn = "0028-0836"
    print(f"\nQuerying ISSN: {issn}")

    if_data = collector.get_impact_factor(issn)

    print("\nResults:")
    print(f"  Source: {if_data['source']}")
    print(f"  Impact Factor: {if_data['if_value']}")
    print(f"  Year: {if_data['year']}")
    print(f"  Quartile: {if_data['quartile']}")
    print(f"  H-index: {if_data['h_index']}")

    if if_data['alternative_metrics']:
        print("\n  Additional Metrics:")
        for key, value in if_data['alternative_metrics'].items():
            if value and key in ['title', 'rank', 'publisher', 'country']:
                print(f"    {key}: {value}")


def example_2_batch_processing():
    """Example 2: Batch process multiple prestigious journals."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Batch Processing Multiple Journals")
    print("=" * 70)

    sjr_csv = "data/raw/scimagojr.csv"

    if not os.path.exists(sjr_csv):
        print(f"⚠️  SJR CSV not found. Skipping this example.\n")
        return

    collector = ImpactFactorCollector(
        sjr_csv_path=sjr_csv,
        email="your-email@example.com"
    )

    # List of top scientific journals
    prestigious_journals = {
        "0028-0836": "Nature",
        "0036-8075": "Science",
        "0140-6736": "The Lancet",
        "1474-547X": "Cell",
        "0027-8424": "PNAS",
        "1097-6256": "Nature Neuroscience",
        "1748-7838": "Cell Stem Cell",
    }

    print(f"\nProcessing {len(prestigious_journals)} journals...\n")

    results = collector.batch_collect(list(prestigious_journals.keys()))

    # Display results in a table format
    print(f"{'ISSN':<15} {'Journal':<25} {'IF':<8} {'Q':<5} {'H-idx':<8} {'Source':<10}")
    print("-" * 80)

    for issn, name in prestigious_journals.items():
        data = results.get(issn, {})
        if_value = data.get('if_value', 'N/A')
        quartile = data.get('quartile', 'N/A')
        h_index = data.get('h_index', 'N/A')
        source = data.get('source', 'none')

        if_str = f"{if_value:.2f}" if isinstance(if_value, (int, float)) else str(if_value)
        h_str = str(h_index) if h_index != 'N/A' else 'N/A'

        print(f"{issn:<15} {name:<25} {if_str:<8} {quartile:<5} {h_str:<8} {source:<10}")

    # Statistics
    print("\n" + "-" * 80)
    sources = {}
    for data in results.values():
        source = data.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1

    print("\nData Sources Summary:")
    for source, count in sources.items():
        print(f"  {source}: {count} journals")


def example_3_openalex_only():
    """Example 3: Use OpenAlex API without SJR data."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Using OpenAlex API Only (No SJR Data)")
    print("=" * 70)

    # Initialize without SJR data
    collector = ImpactFactorCollector(email="your-email@example.com")

    test_journals = [
        "0028-0836",  # Nature
        "0036-8075",  # Science
    ]

    print(f"\nQuerying {len(test_journals)} journals via OpenAlex API...\n")

    for issn in test_journals:
        print(f"ISSN: {issn}")
        if_data = collector.get_impact_factor(issn)

        print(f"  Source: {if_data['source']}")
        print(f"  2yr Mean Citedness: {if_data['if_value']}")
        print(f"  H-index: {if_data['h_index']}")

        alt_metrics = if_data.get('alternative_metrics', {})
        if alt_metrics.get('title'):
            print(f"  Title: {alt_metrics['title']}")
        if alt_metrics.get('works_count'):
            print(f"  Works Count: {alt_metrics['works_count']:,}")
        if alt_metrics.get('cited_by_count'):
            print(f"  Total Citations: {alt_metrics['cited_by_count']:,}")
        print()


def example_4_export_formats():
    """Example 4: Export to different formats."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Export to JavaScript and CSV Formats")
    print("=" * 70)

    sjr_csv = "data/raw/scimagojr.csv"

    if not os.path.exists(sjr_csv):
        print(f"⚠️  SJR CSV not found. Skipping this example.\n")
        return

    collector = ImpactFactorCollector(
        sjr_csv_path=sjr_csv,
        email="your-email@example.com"
    )

    # Sample journals
    issn_list = ["0028-0836", "0036-8075", "0140-6736"]

    print(f"\nCollecting data for {len(issn_list)} journals...")
    results = collector.batch_collect(issn_list)

    # Create output directory
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export to JavaScript
    js_file = output_dir / "impact_factors_example.js"
    print(f"\nExporting to JavaScript: {js_file}")
    collector.export_to_js(results, str(js_file))

    # Export to CSV
    csv_file = output_dir / "impact_factors_example.csv"
    print(f"Exporting to CSV: {csv_file}")
    collector.export_to_csv(results, str(csv_file))

    print("\n✓ Export complete!")

    # Show preview of JavaScript file
    if js_file.exists():
        print(f"\nPreview of {js_file.name}:")
        with open(js_file, 'r') as f:
            lines = f.readlines()[:15]  # First 15 lines
            for line in lines:
                print(f"  {line.rstrip()}")
            if len(f.readlines()) > 15:
                print("  ...")


def example_5_detailed_sjr_metrics():
    """Example 5: Get detailed SJR metrics directly."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Detailed SJR Metrics")
    print("=" * 70)

    sjr_csv = "data/raw/scimagojr.csv"

    if not os.path.exists(sjr_csv):
        print(f"⚠️  SJR CSV not found. Skipping this example.\n")
        return

    # Use SJRDataLoader directly for detailed metrics
    loader = SJRDataLoader()
    if not loader.load_sjr_csv(sjr_csv):
        print("Failed to load SJR data")
        return

    issn = "0028-0836"  # Nature
    print(f"\nDetailed SJR metrics for ISSN: {issn}\n")

    metrics = loader.get_impact_metrics(issn)

    if metrics:
        print(f"  Title: {metrics['title']}")
        print(f"  SJR Score: {metrics['sjr']}")
        print(f"  Best Quartile: {metrics['sjr_best_quartile']}")
        print(f"  H-index: {metrics['h_index']}")
        print(f"  Global Rank: {metrics['rank']}")
        print(f"\n  Publication Metrics:")
        print(f"    Total Documents: {metrics['total_docs']}")
        print(f"    Total Citations: {metrics['total_cites']}")
        print(f"    Citable Documents: {metrics['citable_docs']}")
        print(f"    Cites per Doc (2yr): {metrics['cites_per_doc']}")
        print(f"    References per Doc: {metrics['ref_per_doc']}")
        print(f"\n  Publisher Info:")
        print(f"    Publisher: {metrics['publisher']}")
        print(f"    Country: {metrics['country']}")
        print(f"    Type: {metrics['type']}")
    else:
        print(f"  No data found for ISSN: {issn}")


def example_6_error_handling():
    """Example 6: Demonstrate error handling."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Error Handling and Edge Cases")
    print("=" * 70)

    collector = ImpactFactorCollector()

    test_cases = [
        ("0028-0836", "Valid ISSN (Nature)"),
        ("9999-9999", "Non-existent ISSN"),
        ("invalid", "Invalid ISSN format"),
        ("", "Empty ISSN"),
    ]

    print("\nTesting various ISSN inputs:\n")

    for issn, description in test_cases:
        print(f"Test: {description}")
        print(f"  ISSN: '{issn}'")

        try:
            result = collector.get_impact_factor(issn)
            print(f"  Result: source={result['source']}, if_value={result['if_value']}")
        except Exception as e:
            print(f"  Error: {e}")
        print()


def example_7_compare_sources():
    """Example 7: Compare SJR vs OpenAlex data."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Compare SJR vs OpenAlex Data Sources")
    print("=" * 70)

    sjr_csv = "data/raw/scimagojr.csv"

    if not os.path.exists(sjr_csv):
        print(f"⚠️  SJR CSV not found. Skipping this example.\n")
        return

    # Query with SJR
    collector_sjr = ImpactFactorCollector(sjr_csv_path=sjr_csv)

    # Query with OpenAlex only
    collector_openalex = ImpactFactorCollector(email="your-email@example.com")

    issn = "0028-0836"  # Nature

    print(f"\nComparing data sources for ISSN: {issn}\n")

    # Get SJR data
    sjr_data = collector_sjr.get_impact_factor(issn)
    print("SJR Source:")
    print(f"  Impact Factor (SJR): {sjr_data.get('if_value')}")
    print(f"  Quartile: {sjr_data.get('quartile')}")
    print(f"  H-index: {sjr_data.get('h_index')}")
    print(f"  Source: {sjr_data.get('source')}")

    # Get OpenAlex data
    openalex_data = collector_openalex.get_impact_factor(issn)
    print("\nOpenAlex Source:")
    print(f"  2yr Mean Citedness: {openalex_data.get('if_value')}")
    print(f"  H-index: {openalex_data.get('h_index')}")
    print(f"  Source: {openalex_data.get('source')}")

    print("\nNote: SJR score and OpenAlex 2yr mean citedness are different metrics")
    print("      but both indicate journal impact. They use different methodologies.")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("IMPACT FACTOR COLLECTOR - USAGE EXAMPLES")
    print("=" * 70)

    examples = [
        ("Basic Query", example_1_basic_query),
        ("Batch Processing", example_2_batch_processing),
        ("OpenAlex Only", example_3_openalex_only),
        ("Export Formats", example_4_export_formats),
        ("Detailed SJR Metrics", example_5_detailed_sjr_metrics),
        ("Error Handling", example_6_error_handling),
        ("Compare Sources", example_7_compare_sources),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...")

    for name, example_func in examples:
        try:
            example_func()
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error in example '{name}': {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 70)
    print("Examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
