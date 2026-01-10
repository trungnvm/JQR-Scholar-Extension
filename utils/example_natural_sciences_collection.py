#!/usr/bin/env python3
"""
Example script demonstrating natural sciences data collection workflow.

This is a minimal example that runs a quick test collection with reduced targets
to demonstrate the functionality without long API calls.

Usage:
    python example_natural_sciences_collection.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from collect_natural_sciences_data import NaturalSciencesCollector
from convert_to_js import CSVToJSConverter
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_quick_test():
    """
    Run a quick test collection with minimal targets.
    """
    logger.info("="*80)
    logger.info("QUICK TEST: Natural Sciences Data Collection")
    logger.info("="*80)
    logger.info("\nThis is a minimal test with reduced targets (50 journals per field)")
    logger.info("For full collection, use: python collect_natural_sciences_data.py\n")

    # Initialize collector with reduced targets
    collector = NaturalSciencesCollector(
        email="test@example.com",  # Replace with your email
        sjr_csv_path=None,  # No SJR data for quick test
        output_dir="../data/processed/test"
    )

    # Reduce targets for quick test
    for field_name in collector.FIELDS_CONFIG:
        collector.FIELDS_CONFIG[field_name]['target_count'] = 50
        collector.FIELDS_CONFIG[field_name]['search_terms'] = \
            collector.FIELDS_CONFIG[field_name]['search_terms'][:1]  # Use only first search term

    # Run collection
    try:
        logger.info("\n" + "="*80)
        logger.info("Step 1: Collecting journal data...")
        logger.info("="*80)

        collector.collect_all_fields()

        # Show statistics
        stats = collector.get_statistics()

        logger.info("\n" + "="*80)
        logger.info("COLLECTION COMPLETED - Statistics:")
        logger.info("="*80)

        for field_name, field_stats in stats['fields'].items():
            logger.info(f"\n{field_name.upper()}:")
            logger.info(f"  Collected: {field_stats['count']}")
            logger.info(f"  With ISSN: {field_stats['with_issn']}")
            logger.info(f"  Classified: {field_stats['classified']}")

        logger.info(f"\nCOMBINED: {stats['combined_unique']} unique journals")

        # Convert to JavaScript
        logger.info("\n" + "="*80)
        logger.info("Step 2: Converting to JavaScript...")
        logger.info("="*80)

        converter = CSVToJSConverter(
            input_dir="../data/processed/test",
            output_dir="../data/fields/natural_sciences/test"
        )

        converter.convert_all()

        logger.info("\n" + "="*80)
        logger.info("TEST COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        logger.info("\nGenerated files:")
        logger.info(f"  CSV files: ../data/processed/test/")
        logger.info(f"  JS files: ../data/fields/natural_sciences/test/")
        logger.info("\nTo run full collection:")
        logger.info("  python collect_natural_sciences_data.py --email your@email.com")

    except Exception as e:
        logger.error(f"\nTest failed: {e}", exc_info=True)
        sys.exit(1)


def demonstrate_modules():
    """
    Demonstrate individual module usage.
    """
    logger.info("\n" + "="*80)
    logger.info("MODULE DEMONSTRATION")
    logger.info("="*80)

    # Example 1: Journal Aggregator
    logger.info("\n1. Journal List Aggregator:")
    logger.info("-" * 40)

    from journalListAggregator import JournalAggregator

    aggregator = JournalAggregator(email="test@example.com")
    logger.info("  Fetching 10 physics journals...")

    df = aggregator.fetch_by_field("physics", limit=10)
    logger.info(f"  ✓ Fetched {len(df)} journals")

    if not df.empty:
        logger.info(f"  Sample: {df.iloc[0]['name']}")

    # Example 2: Field Classifier
    logger.info("\n2. Field Classifier:")
    logger.info("-" * 40)

    from fieldClassifier import FieldClassifier

    classifier = FieldClassifier()

    test_journals = [
        "Nature Physics",
        "Journal of the American Chemical Society",
        "Cell Biology International"
    ]

    for journal in test_journals:
        results = classifier.classify_by_name(journal, top_n=1)
        if results:
            result = results[0]
            logger.info(f"  '{journal}'")
            logger.info(f"    → {result['field_name']} ({result['field_code']})")
            logger.info(f"    Confidence: {result['confidence']:.2%}")

    # Example 3: Impact Factor Collector (without SJR data)
    logger.info("\n3. Impact Factor Collector:")
    logger.info("-" * 40)

    from impactFactorCollector import ImpactFactorCollector

    impact_collector = ImpactFactorCollector(email="test@example.com")
    logger.info("  Note: Running without SJR data (will use OpenAlex only)")

    test_issn = "0028-0836"  # Nature
    logger.info(f"  Querying ISSN: {test_issn}")

    if_data = impact_collector.get_impact_factor(test_issn)
    logger.info(f"  ✓ Source: {if_data.get('source')}")

    if if_data.get('if_value'):
        logger.info(f"  ✓ Impact Factor: {if_data.get('if_value')}")
    else:
        logger.info(f"  (No impact factor data available)")


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Example script for natural sciences data collection",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--mode',
        choices=['test', 'demo', 'both'],
        default='both',
        help='Run mode: test (quick collection), demo (module examples), or both'
    )

    args = parser.parse_args()

    try:
        if args.mode in ['demo', 'both']:
            demonstrate_modules()

        if args.mode in ['test', 'both']:
            run_quick_test()

        logger.info("\n✓ Example completed successfully!")

    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nExample failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
