"""
CSV to JavaScript Converter for Natural Sciences Data

This script converts processed CSV journal data to JavaScript format compatible
with the browser extension. It reads CSV files from data/processed/ and generates
JavaScript files in the sfc (Scholar Field Classifier) format.

Output format:
  sfc.physics = { "ISSN": { name: "...", if: ..., ... }, ... }
  sfc.chemistry = { ... }
  etc.

Author: Scholar Extension Team
Date: January 10, 2026
"""

import logging
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CSVToJSConverter:
    """
    Converter for transforming CSV journal data to JavaScript format
    compatible with the browser extension.
    """

    # Field mappings
    FIELD_MAPPINGS = {
        'physics': 'physics',
        'chemistry': 'chemistry',
        'biology': 'biology',
        'mathematics': 'mathematics'
    }

    def __init__(self,
                 input_dir: Optional[str] = None,
                 output_dir: Optional[str] = None):
        """
        Initialize the CSV to JS converter.

        Args:
            input_dir: Directory containing CSV files (default: ../data/processed/)
            output_dir: Directory for output JS files (default: ../data/fields/natural_sciences/)
        """
        # Set default directories
        if input_dir:
            self.input_dir = Path(input_dir)
        else:
            project_root = Path(__file__).parent.parent
            self.input_dir = project_root / 'data' / 'processed'

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            project_root = Path(__file__).parent.parent
            self.output_dir = project_root / 'data' / 'fields' / 'natural_sciences'

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"CSV to JS Converter initialized")
        logger.info(f"  Input directory: {self.input_dir}")
        logger.info(f"  Output directory: {self.output_dir}")

    def read_csv(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Read CSV file from input directory.

        Args:
            filename: Name of the CSV file

        Returns:
            DataFrame or None if file doesn't exist
        """
        file_path = self.input_dir / filename

        if not file_path.exists():
            logger.warning(f"CSV file not found: {file_path}")
            return None

        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            logger.info(f"Read {len(df)} journals from {filename}")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV file {filename}: {e}")
            return None

    def convert_df_to_js_object(self, df: pd.DataFrame, field_name: str) -> Dict:
        """
        Convert DataFrame to JavaScript object format.

        Args:
            df: DataFrame with journal data
            field_name: Name of the field (for logging)

        Returns:
            Dictionary in JavaScript-compatible format
        """
        if df.empty:
            logger.warning(f"Empty DataFrame for {field_name}")
            return {}

        js_object = {}
        processed_count = 0
        skipped_count = 0

        for idx, row in df.iterrows():
            issn = row.get('issn', '')

            # Skip if no ISSN
            if not issn or pd.isna(issn):
                skipped_count += 1
                continue

            # Handle multiple ISSNs (take the first one as primary key)
            issn_list = [i.strip() for i in str(issn).split(',') if i.strip()]

            if not issn_list:
                skipped_count += 1
                continue

            primary_issn = issn_list[0]

            # Build journal entry
            journal_entry = {
                'name': self._safe_string(row.get('name', '')),
                'field': self._safe_string(row.get('primary_field', field_name)),
            }

            # Add optional fields if available
            if 'publisher' in row and pd.notna(row['publisher']):
                journal_entry['publisher'] = self._safe_string(row['publisher'])

            if 'url' in row and pd.notna(row['url']):
                journal_entry['url'] = self._safe_string(row['url'])

            # Add impact factor data if available
            if 'impact_factor' in row and pd.notna(row['impact_factor']):
                journal_entry['if'] = self._safe_float(row['impact_factor'])

            if 'if_year' in row and pd.notna(row['if_year']):
                journal_entry['if_year'] = self._safe_int(row['if_year'])

            if 'quartile' in row and pd.notna(row['quartile']):
                journal_entry['quartile'] = self._safe_string(row['quartile'])

            if 'h_index' in row and pd.notna(row['h_index']):
                journal_entry['h_index'] = self._safe_int(row['h_index'])

            # Add classification data if available
            if 'classified_field_code' in row and pd.notna(row['classified_field_code']):
                journal_entry['oecd_code'] = self._safe_string(row['classified_field_code'])

            if 'classified_field_name' in row and pd.notna(row['classified_field_name']):
                journal_entry['oecd_field'] = self._safe_string(row['classified_field_name'])

            if 'classification_confidence' in row and pd.notna(row['classification_confidence']):
                journal_entry['confidence'] = self._safe_float(row['classification_confidence'])

            # Add citation metrics if available
            if 'works_count' in row and pd.notna(row['works_count']):
                journal_entry['works'] = self._safe_int(row['works_count'])

            if 'cited_by_count' in row and pd.notna(row['cited_by_count']):
                journal_entry['citations'] = self._safe_int(row['cited_by_count'])

            # Store using primary ISSN as key
            js_object[primary_issn] = journal_entry
            processed_count += 1

            # Also add entries for alternate ISSNs (if multiple)
            if len(issn_list) > 1:
                for alt_issn in issn_list[1:]:
                    js_object[alt_issn] = journal_entry

        logger.info(f"[{field_name}] Converted {processed_count} journals (skipped {skipped_count})")

        return js_object

    def _safe_string(self, value) -> str:
        """Safely convert value to string."""
        if pd.isna(value):
            return ''
        return str(value).strip()

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float."""
        if pd.isna(value):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to integer."""
        if pd.isna(value):
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None

    def export_to_js_file(self, js_object: Dict, field_name: str, filename: str):
        """
        Export JavaScript object to .js file in sfc format.

        Args:
            js_object: Dictionary to export
            field_name: Name of the field (e.g., 'physics')
            filename: Output filename
        """
        output_path = self.output_dir / filename

        # Generate JavaScript content
        js_content = self._generate_js_header(field_name, len(js_object))

        # Add sfc namespace initialization
        js_content += "if (typeof sfc === 'undefined') {\n"
        js_content += "  var sfc = {};\n"
        js_content += "}\n\n"

        # Add field data
        js_content += f"// {field_name.capitalize()} journals data\n"
        js_content += f"sfc.{field_name} = "
        js_content += json.dumps(js_object, indent=2, ensure_ascii=False)
        js_content += ";\n\n"

        # Add helper metadata
        js_content += f"// Metadata\n"
        js_content += f"sfc.{field_name}_meta = {{\n"
        js_content += f"  count: {len(js_object)},\n"
        js_content += f"  field: '{field_name}',\n"
        js_content += f"  generated: '{datetime.now().isoformat()}',\n"
        js_content += f"  version: '1.0'\n"
        js_content += "};\n"

        # Write to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(js_content)

            logger.info(f"Exported {len(js_object)} journals to: {output_path}")
        except Exception as e:
            logger.error(f"Error writing JavaScript file: {e}")
            raise

    def _generate_js_header(self, field_name: str, count: int) -> str:
        """Generate JavaScript file header."""
        header = "/**\n"
        header += f" * Scholar Field Classifier - {field_name.capitalize()} Journals Database\n"
        header += f" * \n"
        header += f" * Auto-generated from natural sciences data collection\n"
        header += f" * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += f" * Total journals: {count}\n"
        header += f" * Field: {field_name}\n"
        header += f" * \n"
        header += f" * Format: sfc.{field_name} = {{ 'ISSN': {{ name, if, quartile, ... }}, ... }}\n"
        header += " */\n\n"
        return header

    def convert_field(self, field_name: str) -> bool:
        """
        Convert a single field's CSV to JavaScript.

        Args:
            field_name: Name of the field (e.g., 'physics')

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Converting {field_name.upper()} to JavaScript")
        logger.info(f"{'='*80}")

        # Read CSV
        csv_filename = f"{field_name}_journals.csv"
        df = self.read_csv(csv_filename)

        if df is None or df.empty:
            logger.warning(f"No data to convert for {field_name}")
            return False

        # Convert to JavaScript object
        js_object = self.convert_df_to_js_object(df, field_name)

        if not js_object:
            logger.warning(f"No valid journals to export for {field_name}")
            return False

        # Export to file
        output_filename = f"sfc.{field_name}.js"
        self.export_to_js_file(js_object, field_name, output_filename)

        logger.info(f"✓ Successfully converted {field_name}")
        return True

    def convert_combined(self) -> bool:
        """
        Convert the combined natural sciences CSV to JavaScript.

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Converting COMBINED natural sciences to JavaScript")
        logger.info(f"{'='*80}")

        # Read combined CSV
        df = self.read_csv("natural_sciences_combined.csv")

        if df is None or df.empty:
            logger.warning("No combined data to convert")
            return False

        # Group by field and create separate objects
        all_fields_data = {}

        for field_name in self.FIELD_MAPPINGS.keys():
            # Filter by primary field
            field_df = df[df['primary_field'] == field_name] if 'primary_field' in df.columns else pd.DataFrame()

            if not field_df.empty:
                js_object = self.convert_df_to_js_object(field_df, field_name)
                if js_object:
                    all_fields_data[field_name] = js_object

        # Create a single combined JavaScript file
        if all_fields_data:
            self._export_combined_js_file(all_fields_data)
            logger.info(f"✓ Successfully converted combined data")
            return True

        return False

    def _export_combined_js_file(self, all_fields_data: Dict[str, Dict]):
        """
        Export all fields to a single combined JavaScript file.

        Args:
            all_fields_data: Dictionary mapping field names to journal data
        """
        output_path = self.output_dir / "sfc.natural_sciences.js"

        total_count = sum(len(data) for data in all_fields_data.values())

        # Generate JavaScript content
        js_content = "/**\n"
        js_content += " * Scholar Field Classifier - Natural Sciences Combined Database\n"
        js_content += " * \n"
        js_content += f" * Auto-generated from natural sciences data collection\n"
        js_content += f" * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        js_content += f" * Total journals: {total_count}\n"
        js_content += f" * Fields: {', '.join(all_fields_data.keys())}\n"
        js_content += " */\n\n"

        # Add sfc namespace initialization
        js_content += "if (typeof sfc === 'undefined') {\n"
        js_content += "  var sfc = {};\n"
        js_content += "}\n\n"

        # Add each field's data
        for field_name, js_object in all_fields_data.items():
            js_content += f"// {field_name.capitalize()} journals ({len(js_object)} entries)\n"
            js_content += f"sfc.{field_name} = "
            js_content += json.dumps(js_object, indent=2, ensure_ascii=False)
            js_content += ";\n\n"

        # Add combined metadata
        js_content += "// Combined metadata\n"
        js_content += "sfc.natural_sciences_meta = {\n"
        js_content += f"  total_count: {total_count},\n"
        js_content += "  fields: {\n"

        for field_name, js_object in all_fields_data.items():
            js_content += f"    {field_name}: {len(js_object)},\n"

        js_content += "  },\n"
        js_content += f"  generated: '{datetime.now().isoformat()}',\n"
        js_content += "  version: '1.0'\n"
        js_content += "};\n"

        # Write to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(js_content)

            logger.info(f"Exported combined data ({total_count} journals) to: {output_path}")
        except Exception as e:
            logger.error(f"Error writing combined JavaScript file: {e}")
            raise

    def convert_all(self):
        """
        Convert all field CSVs and combined CSV to JavaScript.
        """
        logger.info("\n" + "="*80)
        logger.info("CSV TO JAVASCRIPT CONVERSION - STARTED")
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)

        success_count = 0
        total_count = len(self.FIELD_MAPPINGS)

        # Convert individual fields
        for field_name in self.FIELD_MAPPINGS.keys():
            if self.convert_field(field_name):
                success_count += 1

        # Convert combined file
        if self.convert_combined():
            logger.info("\n✓ Combined file converted successfully")

        # Summary
        logger.info("\n" + "="*80)
        logger.info("CSV TO JAVASCRIPT CONVERSION - COMPLETED")
        logger.info("="*80)
        logger.info(f"Successfully converted: {success_count}/{total_count} individual fields")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("="*80)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Convert Natural Sciences CSV data to JavaScript format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert with default directories
  python convert_to_js.py

  # Custom input/output directories
  python convert_to_js.py \\
    --input-dir /path/to/csv \\
    --output-dir /path/to/js

  # Convert only specific fields
  python convert_to_js.py --fields physics chemistry
        """
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        default=None,
        help='Input directory containing CSV files (default: ../data/processed/)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory for JavaScript files (default: ../data/fields/natural_sciences/)'
    )

    parser.add_argument(
        '--fields',
        nargs='+',
        choices=['physics', 'chemistry', 'biology', 'mathematics', 'all'],
        default=['all'],
        help='Specific fields to convert (default: all)'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Initialize converter
    logger.info("Initializing CSV to JavaScript Converter...")
    converter = CSVToJSConverter(
        input_dir=args.input_dir,
        output_dir=args.output_dir
    )

    # Convert based on arguments
    try:
        if 'all' in args.fields:
            # Convert all fields
            converter.convert_all()
        else:
            # Convert specific fields
            for field_name in args.fields:
                converter.convert_field(field_name)

            # Also try to convert combined if all fields were selected
            if len(args.fields) == len(converter.FIELD_MAPPINGS):
                converter.convert_combined()

        logger.info("\n✓ Conversion completed successfully!")

    except Exception as e:
        logger.error(f"\n✗ Conversion failed with error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
