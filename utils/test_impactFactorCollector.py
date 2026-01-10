"""
Test suite for Impact Factor Collector module.

Tests all three main classes:
1. SJRDataLoader - Loading and parsing SJR CSV data
2. OpenAlexMetrics - Fetching from OpenAlex API
3. ImpactFactorCollector - Main orchestrator
"""

import unittest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from impactFactorCollector import (
    SJRDataLoader,
    OpenAlexMetrics,
    ImpactFactorCollector
)


class TestSJRDataLoader(unittest.TestCase):
    """Test cases for SJRDataLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary CSV file with sample SJR data
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, 'test_sjr.csv')

        # Sample SJR data (semicolon-separated)
        csv_content = """Rank;Sourceid;Title;Type;Issn;SJR;SJR Best Quartile;H index;Total Docs. (2023);Total Docs;Total Refs;Total Cites (2023);Citable Docs. (2023);Cites / Doc. (2years);Ref. / Doc.;Country;Publisher
1;21100826309;Nature;journal;00280836;14.3;Q1;1234;2500;95000;125000;85000;2300;8.5;50.0;United Kingdom;Nature Publishing Group
2;21100777606;Science;journal;00368075;12.1;Q1;1100;2200;89000;115000;78000;2100;7.8;52.3;United States;American Association for the Advancement of Science
3;21100223807;The Lancet;journal;01406736;10.5;Q1;890;1800;75000;95000;68000;1700;6.9;52.8;United Kingdom;Elsevier
"""
        with open(self.csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_sjr_csv_success(self):
        """Test successful loading of SJR CSV."""
        loader = SJRDataLoader()
        result = loader.load_sjr_csv(self.csv_path)

        self.assertTrue(result)
        self.assertIsNotNone(loader.sjr_data)
        self.assertEqual(len(loader.sjr_data), 3)

    def test_load_sjr_csv_file_not_found(self):
        """Test handling of missing CSV file."""
        loader = SJRDataLoader()
        result = loader.load_sjr_csv("/nonexistent/path.csv")

        self.assertFalse(result)
        self.assertIsNone(loader.sjr_data)

    def test_normalize_issn(self):
        """Test ISSN normalization."""
        loader = SJRDataLoader()

        # Test with hyphen
        self.assertEqual(loader._normalize_issn("0028-0836"), "00280836")

        # Test without hyphen
        self.assertEqual(loader._normalize_issn("00280836"), "00280836")

        # Test with spaces
        self.assertEqual(loader._normalize_issn("0028 0836"), "00280836")

        # Test invalid length
        self.assertEqual(loader._normalize_issn("123"), "")

        # Test None
        self.assertEqual(loader._normalize_issn(None), "")

    def test_get_impact_metrics_found(self):
        """Test retrieving metrics for existing ISSN."""
        loader = SJRDataLoader()
        loader.load_sjr_csv(self.csv_path)

        metrics = loader.get_impact_metrics("0028-0836")

        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['title'], 'Nature')
        self.assertEqual(metrics['sjr'], 14.3)
        self.assertEqual(metrics['sjr_best_quartile'], 'Q1')
        self.assertEqual(metrics['h_index'], 1234)

    def test_get_impact_metrics_not_found(self):
        """Test retrieving metrics for non-existent ISSN."""
        loader = SJRDataLoader()
        loader.load_sjr_csv(self.csv_path)

        metrics = loader.get_impact_metrics("9999-9999")

        self.assertIsNone(metrics)

    def test_get_impact_metrics_no_data_loaded(self):
        """Test retrieving metrics when no data is loaded."""
        loader = SJRDataLoader()
        metrics = loader.get_impact_metrics("0028-0836")

        self.assertIsNone(metrics)

    def test_issn_index_building(self):
        """Test ISSN index is built correctly."""
        loader = SJRDataLoader()
        loader.load_sjr_csv(self.csv_path)

        # Check that all ISSNs are indexed
        self.assertIn("00280836", loader.issn_index)
        self.assertIn("00368075", loader.issn_index)
        self.assertIn("01406736", loader.issn_index)
        self.assertEqual(len(loader.issn_index), 3)


class TestOpenAlexMetrics(unittest.TestCase):
    """Test cases for OpenAlexMetrics class."""

    def setUp(self):
        """Set up test fixtures."""
        self.openalex = OpenAlexMetrics(email="test@example.com")

    @patch('impactFactorCollector.requests.Session.get')
    def test_get_citation_metrics_success(self, mock_get):
        """Test successful retrieval of citation metrics."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [{
                'id': 'https://openalex.org/V4210169703',
                'display_name': 'Nature',
                'issn': ['0028-0836'],
                'works_count': 95000,
                'cited_by_count': 8500000,
                'summary_stats': {
                    '2yr_mean_citedness': 8.5,
                    'h_index': 1234,
                    'i10_index': 15000
                },
                'is_oa': False,
                'is_in_doaj': False,
                'homepage_url': 'https://www.nature.com',
                'publisher': 'Nature Publishing Group'
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        metrics = self.openalex.get_citation_metrics("0028-0836")

        self.assertIsNotNone(metrics)
        self.assertEqual(metrics['display_name'], 'Nature')
        self.assertEqual(metrics['cited_by_count_2yr_mean'], 8.5)
        self.assertEqual(metrics['h_index'], 1234)

    @patch('impactFactorCollector.requests.Session.get')
    def test_get_citation_metrics_not_found(self, mock_get):
        """Test handling of non-existent journal."""
        mock_response = Mock()
        mock_response.json.return_value = {'results': []}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        metrics = self.openalex.get_citation_metrics("9999-9999")

        self.assertIsNone(metrics)

    @patch('impactFactorCollector.requests.Session.get')
    def test_get_2yr_mean_citedness(self, mock_get):
        """Test getting 2-year mean citedness specifically."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [{
                'id': 'test',
                'display_name': 'Test Journal',
                'summary_stats': {
                    '2yr_mean_citedness': 5.2
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        citedness = self.openalex.get_2yr_mean_citedness("0028-0836")

        self.assertEqual(citedness, 5.2)

    @patch('impactFactorCollector.requests.Session.get')
    def test_batch_get_metrics(self, mock_get):
        """Test batch fetching metrics."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'results': [{
                'id': 'test',
                'display_name': 'Test Journal',
                'works_count': 1000,
                'cited_by_count': 50000,
                'summary_stats': {'2yr_mean_citedness': 5.0}
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        issn_list = ["0028-0836", "0036-8075"]
        results = self.openalex.batch_get_metrics(issn_list)

        self.assertEqual(len(results), 2)
        self.assertIn("0028-0836", results)
        self.assertIn("0036-8075", results)


class TestImpactFactorCollector(unittest.TestCase):
    """Test cases for ImpactFactorCollector class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary SJR CSV
        self.temp_dir = tempfile.mkdtemp()
        self.csv_path = os.path.join(self.temp_dir, 'test_sjr.csv')

        csv_content = """Rank;Sourceid;Title;Type;Issn;SJR;SJR Best Quartile;H index;Total Docs. (2023);Total Refs;Total Cites (2023);Citable Docs. (2023);Cites / Doc. (2years);Ref. / Doc.;Country;Publisher
1;21100826309;Nature;journal;00280836;14.3;Q1;1234;2500;125000;85000;2300;8.5;50.0;United Kingdom;Nature Publishing Group
"""
        with open(self.csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_get_impact_factor_from_sjr(self):
        """Test getting impact factor from SJR source."""
        collector = ImpactFactorCollector(sjr_csv_path=self.csv_path)

        result = collector.get_impact_factor("0028-0836")

        self.assertEqual(result['source'], 'sjr')
        self.assertEqual(result['if_value'], 14.3)
        self.assertEqual(result['quartile'], 'Q1')
        self.assertEqual(result['h_index'], 1234)

    @patch('impactFactorCollector.OpenAlexMetrics.get_citation_metrics')
    def test_get_impact_factor_from_openalex(self, mock_openalex):
        """Test fallback to OpenAlex when SJR data unavailable."""
        mock_openalex.return_value = {
            'display_name': 'Test Journal',
            'cited_by_count_2yr_mean': 5.2,
            'h_index': 45,
            'works_count': 1000
        }

        collector = ImpactFactorCollector()  # No SJR data
        result = collector.get_impact_factor("9999-9999")

        self.assertEqual(result['source'], 'openalex')
        self.assertEqual(result['if_value'], 5.2)
        self.assertEqual(result['h_index'], 45)

    def test_get_impact_factor_no_data(self):
        """Test handling when no data is available."""
        collector = ImpactFactorCollector()  # No SJR data

        with patch.object(collector.openalex, 'get_citation_metrics', return_value=None):
            result = collector.get_impact_factor("9999-9999")

            self.assertEqual(result['source'], 'none')
            self.assertIsNone(result['if_value'])

    def test_batch_collect(self):
        """Test batch collection of multiple ISSNs."""
        collector = ImpactFactorCollector(sjr_csv_path=self.csv_path)

        issn_list = ["0028-0836", "9999-9999"]  # One exists, one doesn't
        results = collector.batch_collect(issn_list)

        self.assertEqual(len(results), 2)
        self.assertEqual(results["0028-0836"]['source'], 'sjr')

    def test_export_to_js(self):
        """Test exporting to JavaScript format."""
        collector = ImpactFactorCollector(sjr_csv_path=self.csv_path)

        data_dict = {
            "0028-0836": {
                'if_value': 14.3,
                'year': 2023,
                'source': 'sjr',
                'quartile': 'Q1',
                'h_index': 1234,
                'alternative_metrics': {'title': 'Nature'}
            }
        }

        output_file = os.path.join(self.temp_dir, 'test_output.js')
        collector.export_to_js(data_dict, output_file)

        # Verify file was created and contains expected content
        self.assertTrue(os.path.exists(output_file))

        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn('sfc.impactFactors', content)
            self.assertIn('0028-0836', content)
            self.assertIn('14.3', content)

    def test_export_to_csv(self):
        """Test exporting to CSV format."""
        collector = ImpactFactorCollector(sjr_csv_path=self.csv_path)

        data_dict = {
            "0028-0836": {
                'if_value': 14.3,
                'year': 2023,
                'source': 'sjr',
                'quartile': 'Q1',
                'h_index': 1234,
                'alternative_metrics': {'title': 'Nature'}
            }
        }

        output_file = os.path.join(self.temp_dir, 'test_output.csv')
        collector.export_to_csv(data_dict, output_file)

        # Verify file was created
        self.assertTrue(os.path.exists(output_file))

        # Verify content
        import pandas as pd
        df = pd.read_csv(output_file)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['issn'], '0028-0836')
        self.assertEqual(df.iloc[0]['if_value'], 14.3)

    def test_priority_ordering(self):
        """Test that SJR data takes priority over OpenAlex."""
        collector = ImpactFactorCollector(sjr_csv_path=self.csv_path)

        with patch.object(collector.openalex, 'get_citation_metrics') as mock_openalex:
            mock_openalex.return_value = {
                'cited_by_count_2yr_mean': 99.9  # Different value
            }

            result = collector.get_impact_factor("0028-0836")

            # Should use SJR data (14.3), not OpenAlex (99.9)
            self.assertEqual(result['source'], 'sjr')
            self.assertEqual(result['if_value'], 14.3)
            # OpenAlex should not have been called since SJR data exists
            mock_openalex.assert_not_called()


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""

    def test_end_to_end_workflow(self):
        """Test complete workflow from loading to export."""
        # Create temporary files
        temp_dir = tempfile.mkdtemp()

        try:
            # 1. Create test SJR CSV
            csv_path = os.path.join(temp_dir, 'sjr.csv')
            csv_content = """Rank;Sourceid;Title;Type;Issn;SJR;SJR Best Quartile;H index
1;123;Test Journal;journal;12345678;5.2;Q1;100
"""
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)

            # 2. Initialize collector
            collector = ImpactFactorCollector(sjr_csv_path=csv_path)

            # 3. Collect data
            issn_list = ["1234-5678"]
            results = collector.batch_collect(issn_list)

            # 4. Export to JavaScript
            js_output = os.path.join(temp_dir, 'output.js')
            collector.export_to_js(results, js_output)

            # 5. Export to CSV
            csv_output = os.path.join(temp_dir, 'output.csv')
            collector.export_to_csv(results, csv_output)

            # 6. Verify outputs
            self.assertTrue(os.path.exists(js_output))
            self.assertTrue(os.path.exists(csv_output))

            # Verify JS content
            with open(js_output, 'r') as f:
                js_content = f.read()
                self.assertIn('sfc.impactFactors', js_content)

        finally:
            import shutil
            shutil.rmtree(temp_dir)


def run_live_tests():
    """
    Run live tests against real APIs (not mocked).
    Only run these manually to avoid rate limiting.
    """
    print("\n" + "=" * 60)
    print("LIVE API TESTS (OpenAlex)")
    print("=" * 60)

    openalex = OpenAlexMetrics(email="test@example.com")

    # Test Nature journal
    print("\nTesting Nature (ISSN: 0028-0836)...")
    metrics = openalex.get_citation_metrics("0028-0836")
    if metrics:
        print(f"Success! Display name: {metrics.get('display_name')}")
        print(f"2yr mean citedness: {metrics.get('cited_by_count_2yr_mean')}")
        print(f"H-index: {metrics.get('h_index')}")
    else:
        print("Failed to retrieve data")

    # Test Science journal
    print("\nTesting Science (ISSN: 0036-8075)...")
    citedness = openalex.get_2yr_mean_citedness("0036-8075")
    if citedness:
        print(f"Success! 2yr mean citedness: {citedness}")
    else:
        print("Failed to retrieve data")


if __name__ == '__main__':
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Optionally run live tests
    # Uncomment the line below to test against real APIs
    # run_live_tests()
