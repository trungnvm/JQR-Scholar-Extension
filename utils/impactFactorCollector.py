"""
Impact Factor Collector - Aggregate journal impact metrics from multiple sources.

This module provides classes to collect journal impact factors and metrics from:
1. ScimagoJR (SJR) CSV data - local database
2. OpenAlex API - citation metrics and 2-year mean citedness
3. Fallback mechanisms for missing data

The main orchestrator combines data from multiple sources with priority ordering
and exports results in JavaScript format for browser extension usage.
"""

import logging
import time
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SJRDataLoader:
    """Load and parse ScimagoJR CSV data for journal impact metrics."""

    def __init__(self, default_csv_path: Optional[str] = None):
        """
        Initialize SJR data loader.

        Args:
            default_csv_path: Optional path to SJR CSV file
        """
        self.default_csv_path = default_csv_path
        self.sjr_data: Optional[pd.DataFrame] = None
        self.issn_index: Dict[str, int] = {}  # Map ISSN to DataFrame index

    def load_sjr_csv(self, file_path: Optional[str] = None) -> bool:
        """
        Load SJR data from CSV file.

        Args:
            file_path: Path to SJR CSV file. If None, uses default_csv_path

        Returns:
            True if loading successful, False otherwise
        """
        csv_path = file_path or self.default_csv_path

        if not csv_path:
            logger.error("No CSV file path provided")
            return False

        try:
            # SJR CSVs typically use semicolon delimiter
            logger.info(f"Loading SJR data from: {csv_path}")

            # Try different encodings and delimiters
            try:
                self.sjr_data = pd.read_csv(csv_path, sep=';', encoding='utf-8')
            except Exception:
                try:
                    self.sjr_data = pd.read_csv(csv_path, sep=',', encoding='utf-8')
                except Exception:
                    self.sjr_data = pd.read_csv(csv_path, sep=';', encoding='latin-1')

            # Validate required columns
            required_columns = ['Title', 'Issn']
            missing_columns = [col for col in required_columns if col not in self.sjr_data.columns]

            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                logger.info(f"Available columns: {list(self.sjr_data.columns)}")
                return False

            # Build ISSN index for fast lookup
            self._build_issn_index()

            logger.info(f"Successfully loaded {len(self.sjr_data)} journals from SJR data")
            logger.info(f"Columns: {list(self.sjr_data.columns)}")

            return True

        except FileNotFoundError:
            logger.error(f"CSV file not found: {csv_path}")
            return False
        except Exception as e:
            logger.error(f"Error loading SJR CSV: {e}")
            return False

    def _build_issn_index(self):
        """Build index mapping ISSNs to DataFrame rows for fast lookup."""
        self.issn_index = {}

        if self.sjr_data is None:
            return

        for idx, row in self.sjr_data.iterrows():
            issn_raw = row.get('Issn', '')

            if pd.isna(issn_raw) or not issn_raw:
                continue

            # Handle multiple ISSNs (some entries have multiple separated by comma or space)
            issn_list = re.split(r'[,;\s]+', str(issn_raw))

            for issn in issn_list:
                issn = self._normalize_issn(issn)
                if issn:
                    self.issn_index[issn] = idx

        logger.info(f"Built ISSN index with {len(self.issn_index)} entries")

    def _normalize_issn(self, issn: str) -> str:
        """
        Normalize ISSN format (remove hyphens, convert to uppercase).

        Args:
            issn: Raw ISSN string

        Returns:
            Normalized ISSN or empty string if invalid
        """
        if not issn or pd.isna(issn):
            return ''

        # Remove all non-alphanumeric characters
        issn = re.sub(r'[^0-9X]', '', str(issn).upper())

        # Validate length (ISSN should be 8 characters: 7 digits + 1 check digit)
        if len(issn) != 8:
            return ''

        return issn

    def get_impact_metrics(self, issn: str) -> Optional[Dict[str, Any]]:
        """
        Get impact metrics (SJR, H-index, quartile) for a journal by ISSN.

        Args:
            issn: Journal ISSN (can be with or without hyphen)

        Returns:
            Dictionary with metrics or None if not found
        """
        if self.sjr_data is None:
            logger.warning("SJR data not loaded. Call load_sjr_csv() first.")
            return None

        # Normalize ISSN for lookup
        normalized_issn = self._normalize_issn(issn)

        if not normalized_issn:
            logger.debug(f"Invalid ISSN format: {issn}")
            return None

        # Lookup in index
        if normalized_issn not in self.issn_index:
            logger.debug(f"ISSN not found in SJR data: {issn}")
            return None

        idx = self.issn_index[normalized_issn]
        row = self.sjr_data.iloc[idx]

        # Extract metrics with safe handling of missing/invalid values
        metrics = {
            'title': self._safe_get(row, 'Title'),
            'issn': issn,
            'sjr': self._safe_get_float(row, 'SJR'),
            'sjr_best_quartile': self._safe_get(row, 'SJR Best Quartile'),
            'h_index': self._safe_get_int(row, 'H index'),
            'total_docs': self._safe_get_int(row, 'Total Docs. (2023)') or self._safe_get_int(row, 'Total Docs'),
            'total_refs': self._safe_get_int(row, 'Total Refs. (2023)') or self._safe_get_int(row, 'Total Refs'),
            'total_cites': self._safe_get_int(row, 'Total Cites (2023)') or self._safe_get_int(row, 'Total Cites'),
            'citable_docs': self._safe_get_int(row, 'Citable Docs. (2023)') or self._safe_get_int(row, 'Citable Docs'),
            'cites_per_doc': self._safe_get_float(row, 'Cites / Doc. (2years)'),
            'ref_per_doc': self._safe_get_float(row, 'Ref. / Doc.'),
            'rank': self._safe_get_int(row, 'Rank'),
            'type': self._safe_get(row, 'Type'),
            'country': self._safe_get(row, 'Country'),
            'publisher': self._safe_get(row, 'Publisher'),
            'year': self._extract_year(row)
        }

        return metrics

    def _safe_get(self, row: pd.Series, column: str, default: str = '') -> str:
        """Safely get string value from DataFrame row."""
        if column not in row.index:
            return default

        value = row[column]
        if pd.isna(value):
            return default

        return str(value).strip()

    def _safe_get_int(self, row: pd.Series, column: str, default: Optional[int] = None) -> Optional[int]:
        """Safely get integer value from DataFrame row."""
        if column not in row.index:
            return default

        value = row[column]
        if pd.isna(value):
            return default

        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def _safe_get_float(self, row: pd.Series, column: str, default: Optional[float] = None) -> Optional[float]:
        """Safely get float value from DataFrame row."""
        if column not in row.index:
            return default

        value = row[column]
        if pd.isna(value):
            return default

        # Handle comma as decimal separator (common in European CSVs)
        if isinstance(value, str):
            value = value.replace(',', '.')

        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def _extract_year(self, row: pd.Series) -> Optional[int]:
        """Extract year from column names or values."""
        # Try to find year in column names
        for col in row.index:
            year_match = re.search(r'20\d{2}', str(col))
            if year_match:
                return int(year_match.group())

        # Default to current year or None
        return None


class OpenAlexMetrics:
    """Fetch citation metrics from OpenAlex API."""

    BASE_URL = "https://api.openalex.org"

    def __init__(self, email: Optional[str] = None):
        """
        Initialize OpenAlex metrics client.

        Args:
            email: Optional email for polite pool (faster rate limits)
        """
        self.email = email
        self.session = self._create_session()
        self.rate_limit_delay = 0.1  # 10 requests per second max

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set headers
        headers = {
            'User-Agent': 'ImpactFactorCollector/1.0'
        }
        if self.email:
            headers['User-Agent'] += f' (mailto:{self.email})'

        session.headers.update(headers)

        return session

    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """
        Make a rate-limited API request.

        Args:
            url: API endpoint URL
            params: Query parameters

        Returns:
            JSON response or None on failure
        """
        time.sleep(self.rate_limit_delay)

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAlex request failed: {e}")
            return None

    def get_2yr_mean_citedness(self, issn: str) -> Optional[float]:
        """
        Get 2-year mean citedness (proxy for Impact Factor) from OpenAlex.

        Args:
            issn: Journal ISSN

        Returns:
            2-year mean citedness value or None
        """
        metrics = self.get_citation_metrics(issn)

        if not metrics:
            return None

        return metrics.get('cited_by_count_2yr_mean')

    def get_citation_metrics(self, issn: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive citation metrics for a journal by ISSN.

        Args:
            issn: Journal ISSN

        Returns:
            Dictionary with citation metrics or None
        """
        # First, find the venue by ISSN
        url = f"{self.BASE_URL}/venues"

        params = {
            'filter': f'issn:{issn}'
        }

        if self.email:
            params['mailto'] = self.email

        data = self._make_request(url, params)

        if not data or 'results' not in data or not data['results']:
            logger.debug(f"No OpenAlex venue found for ISSN: {issn}")
            return None

        # Get the first matching venue
        venue = data['results'][0]

        # Extract citation metrics
        metrics = {
            'id': venue.get('id'),
            'display_name': venue.get('display_name'),
            'issn': issn,
            'works_count': venue.get('works_count', 0),
            'cited_by_count': venue.get('cited_by_count', 0),
            'cited_by_count_2yr_mean': None,
            'h_index': None,
            'i10_index': None,
            'is_oa': venue.get('is_oa', False),
            'is_in_doaj': venue.get('is_in_doaj', False),
            'homepage_url': venue.get('homepage_url'),
            'publisher': venue.get('publisher')
        }

        # Try to get summary stats which may include 2yr mean citedness
        summary_stats = venue.get('summary_stats', {})
        if summary_stats:
            # 2-year mean citedness is a proxy for Impact Factor
            metrics['cited_by_count_2yr_mean'] = summary_stats.get('2yr_mean_citedness')
            metrics['h_index'] = summary_stats.get('h_index')
            metrics['i10_index'] = summary_stats.get('i10_index')

        return metrics

    def batch_get_metrics(self, issn_list: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Batch fetch metrics for multiple ISSNs.

        Args:
            issn_list: List of ISSNs

        Returns:
            Dictionary mapping ISSN to metrics
        """
        logger.info(f"Batch fetching OpenAlex metrics for {len(issn_list)} journals")

        results = {}

        for i, issn in enumerate(issn_list, 1):
            if i % 50 == 0:
                logger.info(f"Processed {i}/{len(issn_list)} journals")

            metrics = self.get_citation_metrics(issn)
            if metrics:
                results[issn] = metrics

        logger.info(f"Successfully fetched metrics for {len(results)} journals")
        return results


class ImpactFactorCollector:
    """Main orchestrator for collecting impact factors from multiple sources."""

    def __init__(self, sjr_csv_path: Optional[str] = None, email: Optional[str] = None):
        """
        Initialize Impact Factor Collector.

        Args:
            sjr_csv_path: Path to SJR CSV file
            email: Email for OpenAlex polite pool
        """
        self.sjr_loader = SJRDataLoader(default_csv_path=sjr_csv_path)
        self.openalex = OpenAlexMetrics(email=email)
        self.email = email

        # Try to load SJR data if path provided
        if sjr_csv_path:
            self.sjr_loader.load_sjr_csv(sjr_csv_path)

    def get_impact_factor(self, issn: str) -> Dict[str, Any]:
        """
        Get impact factor from multiple sources with priority ordering.

        Priority order:
        1. SJR data (most comprehensive, includes quartile)
        2. OpenAlex (2-year mean citedness as IF proxy)
        3. Fallback (empty/null values)

        Args:
            issn: Journal ISSN

        Returns:
            Dictionary with impact factor data:
            {
                'if_value': float or None,
                'year': int or None,
                'source': str ('sjr', 'openalex', 'none'),
                'quartile': str or None,
                'h_index': int or None,
                'alternative_metrics': dict with additional data
            }
        """
        result = {
            'if_value': None,
            'year': None,
            'source': 'none',
            'quartile': None,
            'h_index': None,
            'alternative_metrics': {}
        }

        # Priority 1: Try SJR data
        sjr_metrics = self.sjr_loader.get_impact_metrics(issn)

        if sjr_metrics and sjr_metrics.get('sjr'):
            result['if_value'] = sjr_metrics.get('sjr')
            result['year'] = sjr_metrics.get('year')
            result['source'] = 'sjr'
            result['quartile'] = sjr_metrics.get('sjr_best_quartile')
            result['h_index'] = sjr_metrics.get('h_index')
            result['alternative_metrics'] = {
                'title': sjr_metrics.get('title'),
                'rank': sjr_metrics.get('rank'),
                'total_docs': sjr_metrics.get('total_docs'),
                'total_cites': sjr_metrics.get('total_cites'),
                'cites_per_doc': sjr_metrics.get('cites_per_doc'),
                'country': sjr_metrics.get('country'),
                'publisher': sjr_metrics.get('publisher'),
                'type': sjr_metrics.get('type')
            }

            logger.info(f"Found SJR data for {issn}: SJR={result['if_value']}, Q={result['quartile']}")
            return result

        # Priority 2: Try OpenAlex
        logger.debug(f"SJR data not available for {issn}, trying OpenAlex...")
        openalex_metrics = self.openalex.get_citation_metrics(issn)

        if openalex_metrics:
            # Use 2-year mean citedness as IF proxy
            if_value = openalex_metrics.get('cited_by_count_2yr_mean')

            if if_value is not None:
                result['if_value'] = if_value
                result['year'] = None  # OpenAlex doesn't provide specific year
                result['source'] = 'openalex'
                result['h_index'] = openalex_metrics.get('h_index')
                result['alternative_metrics'] = {
                    'title': openalex_metrics.get('display_name'),
                    'works_count': openalex_metrics.get('works_count'),
                    'cited_by_count': openalex_metrics.get('cited_by_count'),
                    'is_oa': openalex_metrics.get('is_oa'),
                    'is_in_doaj': openalex_metrics.get('is_in_doaj'),
                    'publisher': openalex_metrics.get('publisher')
                }

                logger.info(f"Found OpenAlex data for {issn}: 2yr_mean={if_value}")
                return result

        # Priority 3: Fallback (no data found)
        logger.warning(f"No impact factor data found for ISSN: {issn}")
        return result

    def batch_collect(self, issn_list: List[str], use_cache: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Efficiently batch process multiple ISSNs.

        Args:
            issn_list: List of ISSNs to process
            use_cache: Whether to use cached results (not implemented yet)

        Returns:
            Dictionary mapping ISSN to impact factor data
        """
        logger.info(f"Batch collecting impact factors for {len(issn_list)} journals")

        results = {}

        for i, issn in enumerate(issn_list, 1):
            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(issn_list)} journals")

            try:
                if_data = self.get_impact_factor(issn)
                results[issn] = if_data
            except Exception as e:
                logger.error(f"Error processing ISSN {issn}: {e}")
                results[issn] = {
                    'if_value': None,
                    'year': None,
                    'source': 'error',
                    'quartile': None,
                    'h_index': None,
                    'alternative_metrics': {'error': str(e)}
                }

        logger.info(f"Batch collection complete. Processed {len(results)} journals")

        # Summary statistics
        sources = {}
        for data in results.values():
            source = data.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1

        logger.info(f"Data sources breakdown: {sources}")

        return results

    def export_to_js(self, data_dict: Dict[str, Dict[str, Any]], output_file: str):
        """
        Export impact factor data to JavaScript format for browser extension.

        Args:
            data_dict: Dictionary mapping ISSN to impact factor data
            output_file: Path to output JavaScript file
        """
        logger.info(f"Exporting {len(data_dict)} journals to JavaScript format")

        # Convert data to simplified JavaScript object format
        js_data = {}

        for issn, data in data_dict.items():
            # Only include journals with valid IF data
            if data.get('if_value') is None:
                continue

            js_data[issn] = {
                'value': data.get('if_value'),
                'year': data.get('year'),
                'source': data.get('source'),
                'quartile': data.get('quartile'),
                'h_index': data.get('h_index')
            }

            # Add title if available
            alt_metrics = data.get('alternative_metrics', {})
            if alt_metrics.get('title'):
                js_data[issn]['title'] = alt_metrics['title']

        # Generate JavaScript file
        js_content = "// Auto-generated Impact Factor data\n"
        js_content += f"// Generated on: {pd.Timestamp.now()}\n"
        js_content += f"// Total journals: {len(js_data)}\n\n"
        js_content += "if (typeof sfc === 'undefined') {\n"
        js_content += "  var sfc = {};\n"
        js_content += "}\n\n"
        js_content += "sfc.impactFactors = "
        js_content += json.dumps(js_data, indent=2, ensure_ascii=False)
        js_content += ";\n"

        # Write to file
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(js_content)

            logger.info(f"Successfully exported {len(js_data)} journals to {output_file}")

        except Exception as e:
            logger.error(f"Error exporting to JavaScript: {e}")
            raise

    def export_to_csv(self, data_dict: Dict[str, Dict[str, Any]], output_file: str):
        """
        Export impact factor data to CSV format.

        Args:
            data_dict: Dictionary mapping ISSN to impact factor data
            output_file: Path to output CSV file
        """
        logger.info(f"Exporting {len(data_dict)} journals to CSV format")

        rows = []
        for issn, data in data_dict.items():
            row = {
                'issn': issn,
                'if_value': data.get('if_value'),
                'year': data.get('year'),
                'source': data.get('source'),
                'quartile': data.get('quartile'),
                'h_index': data.get('h_index')
            }

            # Flatten alternative metrics
            alt_metrics = data.get('alternative_metrics', {})
            for key, value in alt_metrics.items():
                row[f'alt_{key}'] = value

            rows.append(row)

        df = pd.DataFrame(rows)

        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Successfully exported to {output_file}")

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Basic usage with SJR data
    print("=" * 60)
    print("Example 1: Load SJR data and query impact factors")
    print("=" * 60)

    # Initialize collector with SJR CSV path
    sjr_csv = "scholar_extention_trung/data/raw/scimagojr.csv"
    collector = ImpactFactorCollector(
        sjr_csv_path=sjr_csv,
        email="your-email@example.com"
    )

    # Query single ISSN
    test_issn = "0028-0836"  # Nature journal
    if_data = collector.get_impact_factor(test_issn)
    print(f"\nImpact factor data for {test_issn}:")
    print(json.dumps(if_data, indent=2))

    # Example 2: Batch collection
    print("\n" + "=" * 60)
    print("Example 2: Batch collect multiple ISSNs")
    print("=" * 60)

    test_issns = [
        "0028-0836",  # Nature
        "0036-8075",  # Science
        "0140-6736",  # The Lancet
    ]

    batch_results = collector.batch_collect(test_issns)
    print(f"\nCollected data for {len(batch_results)} journals")

    # Example 3: Export to JavaScript
    print("\n" + "=" * 60)
    print("Example 3: Export to JavaScript format")
    print("=" * 60)

    output_js = "scholar_extention_trung/data/processed/impact_factors.js"
    collector.export_to_js(batch_results, output_js)
    print(f"Exported to: {output_js}")

    # Example 4: Export to CSV
    print("\n" + "=" * 60)
    print("Example 4: Export to CSV format")
    print("=" * 60)

    output_csv = "scholar_extention_trung/data/processed/impact_factors.csv"
    collector.export_to_csv(batch_results, output_csv)
    print(f"Exported to: {output_csv}")

    # Example 5: Using only OpenAlex (without SJR data)
    print("\n" + "=" * 60)
    print("Example 5: Query using OpenAlex only")
    print("=" * 60)

    openalex_collector = ImpactFactorCollector(email="your-email@example.com")
    openalex_data = openalex_collector.get_impact_factor("0028-0836")
    print(f"\nOpenAlex data:")
    print(json.dumps(openalex_data, indent=2))
