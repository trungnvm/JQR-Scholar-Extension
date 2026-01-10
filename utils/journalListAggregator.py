"""
Journal List Aggregator - Fetch and aggregate journal data from multiple sources.

This module provides classes to fetch journal metadata from OpenAlex and Crossref APIs,
aggregate the data, and manage deduplication and storage.
"""

import logging
import time
from typing import List, Dict, Optional, Set
from datetime import datetime
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter to respect API rate limits."""

    def __init__(self, max_requests_per_second: int = 10):
        """
        Initialize rate limiter.

        Args:
            max_requests_per_second: Maximum number of requests allowed per second
        """
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0

    def wait(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_interval:
            sleep_time = self.min_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()


class OpenAlexAPI:
    """Fetch journals from OpenAlex API (https://api.openalex.org/venues)."""

    BASE_URL = "https://api.openalex.org"

    def __init__(self, email: Optional[str] = None):
        """
        Initialize OpenAlex API client.

        Args:
            email: Optional email for polite pool (faster rate limits)
        """
        self.email = email
        self.rate_limiter = RateLimiter(max_requests_per_second=10)
        self.session = self._create_session()

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
            'User-Agent': 'JournalAggregator/1.0'
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
        self.rate_limiter.wait()

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def fetch_journals_by_field(self, field_name: str, limit: int = 1000) -> pd.DataFrame:
        """
        Fetch journals for a specific field from OpenAlex.

        Args:
            field_name: Name of the field/topic to filter journals
            limit: Maximum number of journals to fetch

        Returns:
            DataFrame with journal information
        """
        logger.info(f"Fetching journals for field: {field_name}")

        journals = []
        cursor = "*"
        per_page = 200  # OpenAlex max per page

        url = f"{self.BASE_URL}/venues"

        while len(journals) < limit and cursor:
            params = {
                'filter': f'display_name.search:{field_name}',
                'per-page': per_page,
                'cursor': cursor
            }

            if self.email:
                params['mailto'] = self.email

            data = self._make_request(url, params)

            if not data or 'results' not in data:
                logger.warning("No results returned, stopping pagination")
                break

            results = data['results']
            if not results:
                break

            for venue in results:
                journal_data = self._extract_journal_data(venue, field_name)
                if journal_data:
                    journals.append(journal_data)

            logger.info(f"Fetched {len(journals)} journals so far...")

            # Get next cursor
            cursor = data.get('meta', {}).get('next_cursor')

            if not cursor or len(journals) >= limit:
                break

        logger.info(f"Total journals fetched for {field_name}: {len(journals)}")
        return pd.DataFrame(journals)

    def fetch_all_journals(self, limit: int = 10000) -> pd.DataFrame:
        """
        Fetch comprehensive journal list from OpenAlex.

        Args:
            limit: Maximum number of journals to fetch

        Returns:
            DataFrame with journal information
        """
        logger.info(f"Fetching all journals (limit: {limit})")

        journals = []
        cursor = "*"
        per_page = 200

        url = f"{self.BASE_URL}/venues"

        while len(journals) < limit and cursor:
            params = {
                'per-page': per_page,
                'cursor': cursor
            }

            if self.email:
                params['mailto'] = self.email

            data = self._make_request(url, params)

            if not data or 'results' not in data:
                logger.warning("No results returned, stopping pagination")
                break

            results = data['results']
            if not results:
                break

            for venue in results:
                journal_data = self._extract_journal_data(venue)
                if journal_data:
                    journals.append(journal_data)

            logger.info(f"Fetched {len(journals)} journals so far...")

            # Get next cursor
            cursor = data.get('meta', {}).get('next_cursor')

            if not cursor or len(journals) >= limit:
                break

        logger.info(f"Total journals fetched: {len(journals)}")
        return pd.DataFrame(journals)

    def _extract_journal_data(self, venue: Dict, field_name: str = None) -> Optional[Dict]:
        """
        Extract relevant journal data from OpenAlex venue object.

        Args:
            venue: OpenAlex venue object
            field_name: Optional field name to tag the journal

        Returns:
            Dictionary with extracted journal data
        """
        try:
            # Extract ISSNs
            issn_list = venue.get('issn', []) or venue.get('issn_l', [])
            if isinstance(issn_list, str):
                issn_list = [issn_list]
            elif not issn_list:
                issn_list = []

            # Extract topics
            topics = []
            if venue.get('topics'):
                topics = [topic.get('display_name', '') for topic in venue.get('topics', [])]

            # Build journal data
            journal_data = {
                'name': venue.get('display_name', ''),
                'issn': ','.join(issn_list) if issn_list else '',
                'field': field_name or ','.join(topics[:3]) if topics else '',
                'source': 'OpenAlex',
                'url': venue.get('homepage_url', ''),
                'publisher': venue.get('publisher', ''),
                'works_count': venue.get('works_count', 0),
                'cited_by_count': venue.get('cited_by_count', 0),
                'topics': ','.join(topics) if topics else ''
            }

            return journal_data
        except Exception as e:
            logger.error(f"Error extracting journal data: {e}")
            return None


class CrossrefAPI:
    """Fetch journals from Crossref API."""

    BASE_URL = "https://api.crossref.org"

    def __init__(self, email: Optional[str] = None):
        """
        Initialize Crossref API client.

        Args:
            email: Optional email for polite pool
        """
        self.email = email
        self.rate_limiter = RateLimiter(max_requests_per_second=10)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        headers = {
            'User-Agent': 'JournalAggregator/1.0'
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
        self.rate_limiter.wait()

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def fetch_journal_by_issn(self, issn: str) -> Optional[Dict]:
        """
        Get journal metadata by ISSN.

        Args:
            issn: Journal ISSN

        Returns:
            Dictionary with journal metadata or None
        """
        if not issn or not issn.strip():
            return None

        url = f"{self.BASE_URL}/journals/{issn}"

        data = self._make_request(url)

        if not data or 'message' not in data:
            return None

        return self._extract_journal_data(data['message'])

    def enrich_journal_data(self, issn_list: List[str]) -> pd.DataFrame:
        """
        Batch enrich journal data for multiple ISSNs.

        Args:
            issn_list: List of ISSNs to enrich

        Returns:
            DataFrame with enriched journal data
        """
        logger.info(f"Enriching {len(issn_list)} journals from Crossref")

        enriched_journals = []

        for i, issn in enumerate(issn_list, 1):
            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(issn_list)} journals")

            journal_data = self.fetch_journal_by_issn(issn)
            if journal_data:
                enriched_journals.append(journal_data)

        logger.info(f"Successfully enriched {len(enriched_journals)} journals")
        return pd.DataFrame(enriched_journals)

    def _extract_journal_data(self, message: Dict) -> Optional[Dict]:
        """
        Extract relevant journal data from Crossref message.

        Args:
            message: Crossref message object

        Returns:
            Dictionary with extracted journal data
        """
        try:
            # Extract ISSNs
            issn_list = message.get('ISSN', [])

            # Extract subjects
            subjects = message.get('subjects', [])
            if subjects and isinstance(subjects[0], dict):
                subjects = [s.get('name', '') for s in subjects]

            journal_data = {
                'name': message.get('title', ''),
                'issn': ','.join(issn_list) if issn_list else '',
                'field': ','.join(subjects) if subjects else '',
                'source': 'Crossref',
                'url': message.get('URL', ''),
                'publisher': message.get('publisher', ''),
                'subjects': ','.join(subjects) if subjects else ''
            }

            return journal_data
        except Exception as e:
            logger.error(f"Error extracting journal data: {e}")
            return None


class JournalAggregator:
    """Main orchestrator for fetching and aggregating journal data."""

    def __init__(self, email: Optional[str] = None):
        """
        Initialize Journal Aggregator.

        Args:
            email: Optional email for API polite pools
        """
        self.openalex = OpenAlexAPI(email=email)
        self.crossref = CrossrefAPI(email=email)
        self.email = email

    def fetch_by_field(self, field_name: str, limit: int = 1000,
                       enrich_with_crossref: bool = False) -> pd.DataFrame:
        """
        Get journals for a specific field.

        Args:
            field_name: Name of the field/topic
            limit: Maximum number of journals to fetch
            enrich_with_crossref: Whether to enrich data with Crossref

        Returns:
            DataFrame with journal information
        """
        logger.info(f"Fetching journals for field: {field_name}")

        # Fetch from OpenAlex
        df = self.openalex.fetch_journals_by_field(field_name, limit=limit)

        if df.empty:
            logger.warning(f"No journals found for field: {field_name}")
            return df

        # Optionally enrich with Crossref
        if enrich_with_crossref:
            logger.info("Enriching with Crossref data...")
            issn_list = self._extract_issns_from_df(df)
            if issn_list:
                crossref_df = self.crossref.enrich_journal_data(issn_list)
                if not crossref_df.empty:
                    df = self._merge_dataframes(df, crossref_df)

        # Deduplicate
        df = self.deduplicate_journals(df)

        return df

    def fetch_all_journals(self, limit: int = 10000) -> pd.DataFrame:
        """
        Fetch comprehensive journal list.

        Args:
            limit: Maximum number of journals to fetch

        Returns:
            DataFrame with journal information
        """
        logger.info("Fetching all journals")

        df = self.openalex.fetch_all_journals(limit=limit)

        if df.empty:
            logger.warning("No journals found")
            return df

        # Deduplicate
        df = self.deduplicate_journals(df)

        return df

    def deduplicate_journals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge duplicate journals by ISSN.

        Args:
            df: DataFrame with journal data

        Returns:
            Deduplicated DataFrame
        """
        if df.empty:
            return df

        logger.info(f"Deduplicating {len(df)} journals")

        # Remove rows with empty ISSN
        df_with_issn = df[df['issn'].notna() & (df['issn'] != '')].copy()
        df_without_issn = df[df['issn'].isna() | (df['issn'] == '')].copy()

        if df_with_issn.empty:
            logger.info("No journals with ISSN to deduplicate")
            return df

        # Split multiple ISSNs and create a primary ISSN
        def get_primary_issn(issn_str):
            if pd.isna(issn_str) or issn_str == '':
                return ''
            issns = str(issn_str).split(',')
            return issns[0].strip()

        df_with_issn['primary_issn'] = df_with_issn['issn'].apply(get_primary_issn)

        # Group by primary ISSN and aggregate
        def aggregate_fields(series):
            # Join non-empty unique values
            values = [str(v).strip() for v in series if pd.notna(v) and str(v).strip()]
            unique_values = list(dict.fromkeys(values))  # Preserve order
            return ','.join(unique_values) if unique_values else ''

        def first_non_empty(series):
            for v in series:
                if pd.notna(v) and str(v).strip():
                    return v
            return ''

        agg_dict = {
            'name': first_non_empty,
            'issn': first_non_empty,
            'field': aggregate_fields,
            'source': aggregate_fields,
            'url': first_non_empty,
        }

        # Add optional columns if they exist
        for col in ['publisher', 'works_count', 'cited_by_count', 'topics', 'subjects']:
            if col in df_with_issn.columns:
                if col in ['works_count', 'cited_by_count']:
                    agg_dict[col] = 'max'
                else:
                    agg_dict[col] = aggregate_fields

        df_deduplicated = df_with_issn.groupby('primary_issn', as_index=False).agg(agg_dict)
        df_deduplicated.drop(columns=['primary_issn'], inplace=True, errors='ignore')

        # Combine with journals without ISSN
        result = pd.concat([df_deduplicated, df_without_issn], ignore_index=True)

        logger.info(f"Deduplicated to {len(result)} journals (removed {len(df) - len(result)} duplicates)")

        return result

    def save_to_csv(self, df: pd.DataFrame, filename: str,
                    include_timestamp: bool = True):
        """
        Save results to CSV file.

        Args:
            df: DataFrame to save
            filename: Output filename
            include_timestamp: Whether to include timestamp in filename
        """
        if df.empty:
            logger.warning("DataFrame is empty, nothing to save")
            return

        if include_timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = filename.rsplit('.', 1)[0]
            extension = filename.rsplit('.', 1)[1] if '.' in filename else 'csv'
            filename = f"{base_name}_{timestamp}.{extension}"

        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Saved {len(df)} journals to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise

    def _extract_issns_from_df(self, df: pd.DataFrame) -> List[str]:
        """
        Extract unique ISSNs from DataFrame.

        Args:
            df: DataFrame with ISSN column

        Returns:
            List of unique ISSNs
        """
        issns = set()

        for issn_str in df['issn'].dropna():
            if issn_str and str(issn_str).strip():
                # Split multiple ISSNs
                for issn in str(issn_str).split(','):
                    issn = issn.strip()
                    if issn:
                        issns.add(issn)

        return list(issns)

    def _merge_dataframes(self, df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
        """
        Merge two dataframes with journal data.

        Args:
            df1: First DataFrame
            df2: Second DataFrame

        Returns:
            Merged DataFrame
        """
        # Concatenate both dataframes
        combined = pd.concat([df1, df2], ignore_index=True)

        # Deduplicate the combined data
        return self.deduplicate_journals(combined)


# Example usage
if __name__ == "__main__":
    # Initialize aggregator (optionally with email for polite pool)
    aggregator = JournalAggregator(email="your-email@example.com")

    # Example 1: Fetch journals by field
    df_field = aggregator.fetch_by_field("machine learning", limit=500)
    aggregator.save_to_csv(df_field, "ml_journals.csv")

    # Example 2: Fetch all journals
    df_all = aggregator.fetch_all_journals(limit=1000)
    aggregator.save_to_csv(df_all, "all_journals.csv")

    # Example 3: Use OpenAlex API directly
    openalex = OpenAlexAPI(email="your-email@example.com")
    df_openalex = openalex.fetch_journals_by_field("computer science", limit=200)
    print(f"Fetched {len(df_openalex)} journals from OpenAlex")

    # Example 4: Enrich with Crossref
    crossref = CrossrefAPI(email="your-email@example.com")
    journal_info = crossref.fetch_journal_by_issn("0028-0836")  # Nature journal
    if journal_info:
        print(f"Journal info: {journal_info}")
