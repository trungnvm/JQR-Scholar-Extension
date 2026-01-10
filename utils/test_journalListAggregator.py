"""
Unit tests for journalListAggregator module.

Run tests with: python -m pytest test_journalListAggregator.py
Or simply: python test_journalListAggregator.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from journalListAggregator import (
    RateLimiter,
    OpenAlexAPI,
    CrossrefAPI,
    JournalAggregator
)


class TestRateLimiter(unittest.TestCase):
    """Test RateLimiter class."""

    def test_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(max_requests_per_second=10)
        self.assertEqual(limiter.max_requests_per_second, 10)
        self.assertEqual(limiter.min_interval, 0.1)

    def test_wait(self):
        """Test that wait method respects rate limit."""
        import time
        limiter = RateLimiter(max_requests_per_second=5)

        start = time.time()
        limiter.wait()
        limiter.wait()
        elapsed = time.time() - start

        # Should take at least min_interval (0.2 seconds for 5 req/s)
        self.assertGreaterEqual(elapsed, 0.2)


class TestOpenAlexAPI(unittest.TestCase):
    """Test OpenAlexAPI class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api = OpenAlexAPI(email="test@example.com")

    def test_initialization(self):
        """Test API initialization."""
        self.assertEqual(self.api.email, "test@example.com")
        self.assertIsNotNone(self.api.session)
        self.assertIsNotNone(self.api.rate_limiter)

    def test_extract_journal_data_basic(self):
        """Test extracting journal data from venue object."""
        venue = {
            'display_name': 'Test Journal',
            'issn': ['1234-5678', '8765-4321'],
            'homepage_url': 'https://example.com',
            'publisher': 'Test Publisher',
            'works_count': 1000,
            'cited_by_count': 5000,
            'topics': [
                {'display_name': 'Computer Science'},
                {'display_name': 'Machine Learning'}
            ]
        }

        result = self.api._extract_journal_data(venue, 'AI')

        self.assertEqual(result['name'], 'Test Journal')
        self.assertEqual(result['issn'], '1234-5678,8765-4321')
        self.assertEqual(result['field'], 'AI')
        self.assertEqual(result['source'], 'OpenAlex')
        self.assertEqual(result['url'], 'https://example.com')
        self.assertEqual(result['works_count'], 1000)

    def test_extract_journal_data_missing_fields(self):
        """Test extracting journal data with missing fields."""
        venue = {
            'display_name': 'Minimal Journal'
        }

        result = self.api._extract_journal_data(venue)

        self.assertEqual(result['name'], 'Minimal Journal')
        self.assertEqual(result['issn'], '')
        self.assertEqual(result['url'], '')

    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {'test': 'data'}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.api._make_request('https://test.com')

        self.assertEqual(result, {'test': 'data'})
        mock_get.assert_called_once()

    @patch('requests.Session.get')
    def test_make_request_failure(self, mock_get):
        """Test failed API request."""
        mock_get.side_effect = Exception("Network error")

        result = self.api._make_request('https://test.com')

        self.assertIsNone(result)


class TestCrossrefAPI(unittest.TestCase):
    """Test CrossrefAPI class."""

    def setUp(self):
        """Set up test fixtures."""
        self.api = CrossrefAPI(email="test@example.com")

    def test_initialization(self):
        """Test API initialization."""
        self.assertEqual(self.api.email, "test@example.com")
        self.assertIsNotNone(self.api.session)

    def test_extract_journal_data(self):
        """Test extracting journal data from Crossref message."""
        message = {
            'title': 'Nature',
            'ISSN': ['0028-0836', '1476-4687'],
            'subjects': [
                {'name': 'Science'},
                {'name': 'Medicine'}
            ],
            'URL': 'https://www.nature.com',
            'publisher': 'Nature Publishing Group'
        }

        result = self.api._extract_journal_data(message)

        self.assertEqual(result['name'], 'Nature')
        self.assertEqual(result['issn'], '0028-0836,1476-4687')
        self.assertEqual(result['field'], 'Science,Medicine')
        self.assertEqual(result['source'], 'Crossref')
        self.assertEqual(result['publisher'], 'Nature Publishing Group')

    def test_fetch_journal_by_issn_empty(self):
        """Test fetching journal with empty ISSN."""
        result = self.api.fetch_journal_by_issn('')
        self.assertIsNone(result)

        result = self.api.fetch_journal_by_issn(None)
        self.assertIsNone(result)


class TestJournalAggregator(unittest.TestCase):
    """Test JournalAggregator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.aggregator = JournalAggregator(email="test@example.com")

    def test_initialization(self):
        """Test aggregator initialization."""
        self.assertIsNotNone(self.aggregator.openalex)
        self.assertIsNotNone(self.aggregator.crossref)
        self.assertEqual(self.aggregator.email, "test@example.com")

    def test_deduplicate_journals_empty(self):
        """Test deduplication with empty DataFrame."""
        df = pd.DataFrame()
        result = self.aggregator.deduplicate_journals(df)
        self.assertTrue(result.empty)

    def test_deduplicate_journals_no_issn(self):
        """Test deduplication with journals without ISSN."""
        data = {
            'name': ['Journal A', 'Journal B'],
            'issn': ['', ''],
            'field': ['CS', 'AI'],
            'source': ['OpenAlex', 'OpenAlex'],
            'url': ['', '']
        }
        df = pd.DataFrame(data)

        result = self.aggregator.deduplicate_journals(df)
        self.assertEqual(len(result), 2)

    def test_deduplicate_journals_with_duplicates(self):
        """Test deduplication with duplicate journals."""
        data = {
            'name': ['Journal A', 'Journal A', 'Journal B'],
            'issn': ['1234-5678', '1234-5678', '8765-4321'],
            'field': ['CS', 'AI', 'ML'],
            'source': ['OpenAlex', 'Crossref', 'OpenAlex'],
            'url': ['http://a.com', 'http://a.com', 'http://b.com']
        }
        df = pd.DataFrame(data)

        result = self.aggregator.deduplicate_journals(df)

        # Should deduplicate to 2 journals (Journal A merged)
        self.assertEqual(len(result), 2)

        # Check merged fields
        journal_a = result[result['issn'] == '1234-5678'].iloc[0]
        self.assertIn('CS', journal_a['field'])
        self.assertIn('AI', journal_a['field'])

    def test_extract_issns_from_df(self):
        """Test extracting ISSNs from DataFrame."""
        data = {
            'issn': ['1234-5678', '8765-4321,1111-2222', '', None],
            'name': ['A', 'B', 'C', 'D']
        }
        df = pd.DataFrame(data)

        issns = self.aggregator._extract_issns_from_df(df)

        self.assertIn('1234-5678', issns)
        self.assertIn('8765-4321', issns)
        self.assertIn('1111-2222', issns)
        self.assertEqual(len(issns), 3)

    def test_save_to_csv_empty(self):
        """Test saving empty DataFrame."""
        df = pd.DataFrame()

        # Should not raise exception
        self.aggregator.save_to_csv(df, 'test_output.csv', include_timestamp=False)

    @patch('pandas.DataFrame.to_csv')
    def test_save_to_csv_success(self, mock_to_csv):
        """Test successful CSV save."""
        data = {
            'name': ['Journal A'],
            'issn': ['1234-5678'],
            'field': ['CS'],
            'source': ['OpenAlex'],
            'url': ['http://a.com']
        }
        df = pd.DataFrame(data)

        self.aggregator.save_to_csv(df, 'test.csv', include_timestamp=False)

        mock_to_csv.assert_called_once_with('test.csv', index=False, encoding='utf-8')

    def test_save_to_csv_with_timestamp(self):
        """Test CSV save with timestamp."""
        data = {
            'name': ['Journal A'],
            'issn': ['1234-5678'],
            'field': ['CS'],
            'source': ['OpenAlex'],
            'url': ['http://a.com']
        }
        df = pd.DataFrame(data)

        # Should not raise exception
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, 'test.csv')
            self.aggregator.save_to_csv(df, filepath, include_timestamp=True)

            # Check that a file was created (with timestamp in name)
            files = os.listdir(tmpdir)
            self.assertTrue(any('test_' in f and '.csv' in f for f in files))


class TestIntegration(unittest.TestCase):
    """Integration tests (these will make real API calls if uncommented)."""

    def test_openalex_real_api_call(self):
        """
        Test real OpenAlex API call (commented out by default).

        Uncomment to test with real API.
        """
        pass
        # api = OpenAlexAPI(email="test@example.com")
        # df = api.fetch_journals_by_field("test", limit=5)
        # self.assertIsNotNone(df)
        # self.assertIsInstance(df, pd.DataFrame)

    def test_crossref_real_api_call(self):
        """
        Test real Crossref API call (commented out by default).

        Uncomment to test with real API.
        """
        pass
        # api = CrossrefAPI(email="test@example.com")
        # journal = api.fetch_journal_by_issn("0028-0836")
        # self.assertIsNotNone(journal)
        # self.assertEqual(journal['name'], 'Nature')


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
