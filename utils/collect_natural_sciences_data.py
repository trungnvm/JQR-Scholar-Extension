"""
Natural Sciences Data Collection Orchestrator

This script orchestrates the collection of journal data for natural sciences fields
(Physics, Chemistry, Biology/Life Sciences, Mathematics) using the implemented modules:
- journalListAggregator: Fetch journals from OpenAlex
- fieldClassifier: Classify journals by field
- impactFactorCollector: Enrich with impact factors from SJR data

The script fetches, classifies, enriches, deduplicates, and exports journal data
to organized CSV files for further processing.

Author: Scholar Extension Team
Date: January 10, 2026
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
import pandas as pd
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from journalListAggregator import JournalAggregator, OpenAlexAPI
from fieldClassifier import FieldClassifier
from impactFactorCollector import ImpactFactorCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('natural_sciences_collection.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class NaturalSciencesCollector:
    """
    Orchestrator for collecting natural sciences journal data.

    Handles:
    - Fetching journals from OpenAlex for specific fields
    - Classification using fieldClassifier
    - Enrichment with impact factors from SJR data
    - Deduplication and export to CSV
    """

    # Field definitions with OpenAlex search terms and targets
    FIELDS_CONFIG = {
        'physics': {
            'search_terms': ['physics', 'physical sciences', 'quantum', 'astrophysics', 'cosmology'],
            'target_count': 1000,
            'oecd_codes': ['1.3'],  # Physical sciences
            'description': 'Physics and Physical Sciences journals'
        },
        'chemistry': {
            'search_terms': ['chemistry', 'chemical sciences', 'biochemistry', 'analytical chemistry'],
            'target_count': 800,
            'oecd_codes': ['1.4'],  # Chemical sciences
            'description': 'Chemistry and Chemical Sciences journals'
        },
        'biology': {
            'search_terms': ['biology', 'life sciences', 'molecular biology', 'cell biology',
                           'ecology', 'genetics', 'microbiology', 'zoology', 'botany'],
            'target_count': 1200,
            'oecd_codes': ['1.6'],  # Biological sciences
            'description': 'Biology and Life Sciences journals'
        },
        'mathematics': {
            'search_terms': ['mathematics', 'mathematical', 'statistics', 'applied mathematics'],
            'target_count': 600,
            'oecd_codes': ['1.1'],  # Mathematics
            'description': 'Mathematics and Statistics journals'
        }
    }

    def __init__(self,
                 email: Optional[str] = None,
                 sjr_csv_path: Optional[str] = None,
                 output_dir: Optional[str] = None):
        """
        Initialize the Natural Sciences Collector.

        Args:
            email: Email for API polite pools (OpenAlex, Crossref)
            sjr_csv_path: Path to SJR CSV file for impact factors
            output_dir: Directory for output CSV files
        """
        self.email = email
        self.sjr_csv_path = sjr_csv_path

        # Set default output directory
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Default to data/processed/ in project root
            project_root = Path(__file__).parent.parent
            self.output_dir = project_root / 'data' / 'processed'

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        logger.info("Initializing Natural Sciences Collector components...")
        self.aggregator = JournalAggregator(email=email)
        self.classifier = FieldClassifier()
        self.impact_collector = None

        # Try to initialize impact collector if SJR path provided
        if sjr_csv_path:
            try:
                self.impact_collector = ImpactFactorCollector(
                    sjr_csv_path=sjr_csv_path,
                    email=email
                )
                logger.info(f"Impact factor collector initialized with SJR data: {sjr_csv_path}")
            except Exception as e:
                logger.warning(f"Could not initialize impact collector: {e}")
                logger.warning("Proceeding without impact factor enrichment")
        else:
            logger.info("No SJR CSV path provided. Skipping impact factor enrichment.")

        # Storage for collected data
        self.field_data: Dict[str, pd.DataFrame] = {}
        self.all_journals: pd.DataFrame = pd.DataFrame()

        logger.info(f"Natural Sciences Collector initialized. Output directory: {self.output_dir}")

    def fetch_field_journals(self, field_name: str, config: Dict) -> pd.DataFrame:
        """
        Fetch journals for a specific field using multiple search terms.

        Args:
            field_name: Name of the field (e.g., 'physics')
            config: Field configuration dictionary

        Returns:
            DataFrame with collected journals
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Fetching journals for: {field_name.upper()}")
        logger.info(f"Description: {config['description']}")
        logger.info(f"Target count: {config['target_count']}")
        logger.info(f"Search terms: {', '.join(config['search_terms'])}")
        logger.info(f"{'='*80}")

        all_journals = []
        seen_issns: Set[str] = set()

        # Fetch journals for each search term
        for search_term in config['search_terms']:
            logger.info(f"\n[{field_name}] Searching for: '{search_term}'")

            try:
                # Calculate limit per search term
                limit_per_term = config['target_count'] // len(config['search_terms']) + 100

                # Fetch from OpenAlex
                df = self.aggregator.fetch_by_field(
                    field_name=search_term,
                    limit=limit_per_term,
                    enrich_with_crossref=False
                )

                if df.empty:
                    logger.warning(f"No journals found for '{search_term}'")
                    continue

                # Add field tag
                df['primary_field'] = field_name
                df['search_term'] = search_term

                # Filter out duplicates based on ISSN
                new_journals = []
                for _, row in df.iterrows():
                    issn = row.get('issn', '')
                    if issn and issn not in seen_issns:
                        seen_issns.add(issn)
                        new_journals.append(row)

                if new_journals:
                    all_journals.extend(new_journals)
                    logger.info(f"  Added {len(new_journals)} new unique journals (Total: {len(all_journals)})")
                else:
                    logger.info(f"  No new unique journals found")

                # Progress update
                if len(all_journals) >= config['target_count']:
                    logger.info(f"  Target count ({config['target_count']}) reached!")
                    break

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error fetching journals for '{search_term}': {e}")
                continue

        if not all_journals:
            logger.warning(f"No journals collected for {field_name}")
            return pd.DataFrame()

        # Convert to DataFrame
        result_df = pd.DataFrame(all_journals)

        logger.info(f"\n[{field_name}] Collection Summary:")
        logger.info(f"  Total unique journals: {len(result_df)}")
        logger.info(f"  Target: {config['target_count']}")
        logger.info(f"  Achievement: {len(result_df)/config['target_count']*100:.1f}%")

        return result_df

    def classify_journals(self, df: pd.DataFrame, field_name: str) -> pd.DataFrame:
        """
        Classify journals using the field classifier.

        Args:
            df: DataFrame with journal data
            field_name: Primary field name

        Returns:
            DataFrame with classification results added
        """
        if df.empty:
            return df

        logger.info(f"\n[{field_name}] Classifying {len(df)} journals...")

        classified_records = []

        for idx, row in df.iterrows():
            journal_name = row.get('name', '')
            topics = row.get('topics', '')

            # Convert topics string to list
            topics_list = []
            if topics and isinstance(topics, str):
                topics_list = [t.strip() for t in topics.split(',') if t.strip()]

            # Classify using multi-method
            classification_result = self.classifier.classify_multi_method(
                journal_name=journal_name,
                topics_list=topics_list if topics_list else None,
                top_n=3
            )

            # Extract top classification
            classifications = classification_result.get('classifications', [])

            if classifications:
                top_class = classifications[0]
                row['classified_field_code'] = top_class.get('field_code', '')
                row['classified_field_name'] = top_class.get('field_name', '')
                row['classification_confidence'] = top_class.get('confidence', 0.0)
                row['classification_methods'] = ','.join(classification_result.get('methods_used', []))
            else:
                row['classified_field_code'] = ''
                row['classified_field_name'] = ''
                row['classification_confidence'] = 0.0
                row['classification_methods'] = ''

            classified_records.append(row)

            # Progress logging
            if (idx + 1) % 100 == 0:
                logger.info(f"  Classified {idx + 1}/{len(df)} journals...")

        result_df = pd.DataFrame(classified_records)

        # Classification summary
        classified_count = len(result_df[result_df['classified_field_code'] != ''])
        logger.info(f"\n[{field_name}] Classification Summary:")
        logger.info(f"  Successfully classified: {classified_count}/{len(result_df)}")
        logger.info(f"  Success rate: {classified_count/len(result_df)*100:.1f}%")

        return result_df

    def enrich_with_impact_factors(self, df: pd.DataFrame, field_name: str) -> pd.DataFrame:
        """
        Enrich journal data with impact factors from SJR data.

        Args:
            df: DataFrame with journal data
            field_name: Field name for logging

        Returns:
            DataFrame with impact factor data added
        """
        if df.empty or not self.impact_collector:
            return df

        logger.info(f"\n[{field_name}] Enriching with impact factors...")

        enriched_records = []
        success_count = 0

        for idx, row in df.iterrows():
            issn = row.get('issn', '')

            if issn:
                # Split multiple ISSNs and try each one
                issn_list = [i.strip() for i in str(issn).split(',') if i.strip()]

                if_data = None
                for issn_variant in issn_list:
                    try:
                        if_data = self.impact_collector.get_impact_factor(issn_variant)
                        if if_data and if_data.get('if_value'):
                            break
                    except Exception as e:
                        logger.debug(f"Error getting IF for {issn_variant}: {e}")
                        continue

                if if_data:
                    row['impact_factor'] = if_data.get('if_value')
                    row['if_year'] = if_data.get('year')
                    row['if_source'] = if_data.get('source')
                    row['quartile'] = if_data.get('quartile')
                    row['h_index'] = if_data.get('h_index')

                    if if_data.get('if_value'):
                        success_count += 1
                else:
                    row['impact_factor'] = None
                    row['if_year'] = None
                    row['if_source'] = 'none'
                    row['quartile'] = None
                    row['h_index'] = None
            else:
                row['impact_factor'] = None
                row['if_year'] = None
                row['if_source'] = 'none'
                row['quartile'] = None
                row['h_index'] = None

            enriched_records.append(row)

            # Progress logging
            if (idx + 1) % 100 == 0:
                logger.info(f"  Enriched {idx + 1}/{len(df)} journals...")

        result_df = pd.DataFrame(enriched_records)

        logger.info(f"\n[{field_name}] Impact Factor Enrichment Summary:")
        logger.info(f"  Journals with IF data: {success_count}/{len(result_df)}")
        logger.info(f"  Success rate: {success_count/len(result_df)*100:.1f}%")

        return result_df

    def deduplicate_across_fields(self, all_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Deduplicate journals that appear in multiple fields.

        Args:
            all_data: Dictionary mapping field names to DataFrames

        Returns:
            Combined and deduplicated DataFrame
        """
        logger.info("\n" + "="*80)
        logger.info("Deduplicating journals across all fields...")
        logger.info("="*80)

        # Combine all dataframes
        all_dfs = []
        for field_name, df in all_data.items():
            if not df.empty:
                df['primary_field'] = field_name
                all_dfs.append(df)

        if not all_dfs:
            logger.warning("No data to deduplicate")
            return pd.DataFrame()

        combined = pd.concat(all_dfs, ignore_index=True)
        logger.info(f"Total journals before deduplication: {len(combined)}")

        # Deduplicate using journalListAggregator's method
        deduplicated = self.aggregator.deduplicate_journals(combined)

        logger.info(f"Total journals after deduplication: {len(deduplicated)}")
        logger.info(f"Removed {len(combined) - len(deduplicated)} duplicates")

        return deduplicated

    def export_to_csv(self, df: pd.DataFrame, filename: str):
        """
        Export DataFrame to CSV file.

        Args:
            df: DataFrame to export
            filename: Output filename
        """
        if df.empty:
            logger.warning(f"Cannot export empty DataFrame to {filename}")
            return

        output_path = self.output_dir / filename

        try:
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"Exported {len(df)} journals to: {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise

    def collect_all_fields(self):
        """
        Main orchestration method: collect data for all natural sciences fields.
        """
        logger.info("\n" + "="*80)
        logger.info("NATURAL SCIENCES DATA COLLECTION - STARTED")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)

        start_time = time.time()

        # Step 1: Fetch journals for each field
        for field_name, config in self.FIELDS_CONFIG.items():
            logger.info(f"\n{'*'*80}")
            logger.info(f"STEP 1: Fetching journals for {field_name.upper()}")
            logger.info(f"{'*'*80}")

            df = self.fetch_field_journals(field_name, config)

            if not df.empty:
                self.field_data[field_name] = df
                logger.info(f"✓ Successfully collected {len(df)} journals for {field_name}")
            else:
                logger.warning(f"✗ No journals collected for {field_name}")

        # Step 2: Classify journals
        for field_name, df in self.field_data.items():
            logger.info(f"\n{'*'*80}")
            logger.info(f"STEP 2: Classifying {field_name.upper()} journals")
            logger.info(f"{'*'*80}")

            classified_df = self.classify_journals(df, field_name)
            self.field_data[field_name] = classified_df

        # Step 3: Enrich with impact factors
        if self.impact_collector:
            for field_name, df in self.field_data.items():
                logger.info(f"\n{'*'*80}")
                logger.info(f"STEP 3: Enriching {field_name.upper()} with impact factors")
                logger.info(f"{'*'*80}")

                enriched_df = self.enrich_with_impact_factors(df, field_name)
                self.field_data[field_name] = enriched_df
        else:
            logger.info("\nSkipping impact factor enrichment (no SJR data)")

        # Step 4: Export individual field files
        logger.info(f"\n{'*'*80}")
        logger.info("STEP 4: Exporting individual field files")
        logger.info(f"{'*'*80}")

        for field_name, df in self.field_data.items():
            if not df.empty:
                filename = f"{field_name}_journals.csv"
                self.export_to_csv(df, filename)

        # Step 5: Deduplicate and create combined file
        logger.info(f"\n{'*'*80}")
        logger.info("STEP 5: Creating combined natural sciences file")
        logger.info(f"{'*'*80}")

        combined_df = self.deduplicate_across_fields(self.field_data)
        if not combined_df.empty:
            self.all_journals = combined_df
            self.export_to_csv(combined_df, "natural_sciences_combined.csv")

        # Final summary
        elapsed_time = time.time() - start_time

        logger.info("\n" + "="*80)
        logger.info("NATURAL SCIENCES DATA COLLECTION - COMPLETED")
        logger.info("="*80)
        logger.info(f"Total execution time: {elapsed_time/60:.2f} minutes")
        logger.info(f"\nCollection Summary:")

        total_journals = 0
        for field_name, df in self.field_data.items():
            count = len(df)
            total_journals += count
            target = self.FIELDS_CONFIG[field_name]['target_count']
            logger.info(f"  {field_name.capitalize():15s}: {count:4d} journals (target: {target})")

        logger.info(f"\n  Total individual: {total_journals}")
        logger.info(f"  Combined unique:  {len(self.all_journals)}")
        logger.info(f"\nOutput directory: {self.output_dir}")
        logger.info("="*80)

    def get_statistics(self) -> Dict:
        """
        Get collection statistics.

        Returns:
            Dictionary with statistics
        """
        stats = {
            'total_fields': len(self.field_data),
            'fields': {}
        }

        for field_name, df in self.field_data.items():
            stats['fields'][field_name] = {
                'count': len(df),
                'target': self.FIELDS_CONFIG[field_name]['target_count'],
                'achievement_rate': len(df) / self.FIELDS_CONFIG[field_name]['target_count'] * 100,
                'with_issn': len(df[df['issn'].notna() & (df['issn'] != '')]),
                'classified': len(df[df['classified_field_code'] != '']) if 'classified_field_code' in df.columns else 0,
                'with_if': len(df[df['impact_factor'].notna()]) if 'impact_factor' in df.columns else 0
            }

        stats['combined_unique'] = len(self.all_journals)

        return stats


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Natural Sciences Journal Data Collection Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic collection (without impact factors)
  python collect_natural_sciences_data.py

  # With email for API polite pool
  python collect_natural_sciences_data.py --email your-email@example.com

  # With SJR data for impact factors
  python collect_natural_sciences_data.py \\
    --sjr-csv ../data/raw/scimagojr.csv \\
    --email your-email@example.com

  # Custom output directory
  python collect_natural_sciences_data.py \\
    --output-dir /path/to/output \\
    --email your-email@example.com
        """
    )

    parser.add_argument(
        '--email',
        type=str,
        default=None,
        help='Email address for API polite pools (OpenAlex, Crossref)'
    )

    parser.add_argument(
        '--sjr-csv',
        type=str,
        default=None,
        help='Path to SJR CSV file for impact factor enrichment'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for CSV files (default: ../data/processed/)'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit total journals per field (for testing)'
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Initialize collector
    logger.info("Initializing Natural Sciences Collector...")
    collector = NaturalSciencesCollector(
        email=args.email,
        sjr_csv_path=args.sjr_csv,
        output_dir=args.output_dir
    )

    # Apply limit to config if provided
    if args.limit:
        logger.info(f"Applying limit of {args.limit} journals per field")
        for field in collector.FIELDS_CONFIG:
            collector.FIELDS_CONFIG[field]['target_count'] = args.limit

    # Run collection
    try:
        collector.collect_all_fields()

        # Print statistics
        stats = collector.get_statistics()

        print("\n" + "="*80)
        print("COLLECTION STATISTICS")
        print("="*80)

        for field_name, field_stats in stats['fields'].items():
            print(f"\n{field_name.upper()}:")
            print(f"  Collected: {field_stats['count']}")
            print(f"  Target: {field_stats['target']}")
            print(f"  Achievement: {field_stats['achievement_rate']:.1f}%")
            print(f"  With ISSN: {field_stats['with_issn']}")
            print(f"  Classified: {field_stats['classified']}")
            print(f"  With IF: {field_stats['with_if']}")

        print(f"\nCOMBINED (deduplicated): {stats['combined_unique']} journals")
        print("="*80)

        logger.info("\n✓ Collection completed successfully!")

    except Exception as e:
        logger.error(f"\n✗ Collection failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
