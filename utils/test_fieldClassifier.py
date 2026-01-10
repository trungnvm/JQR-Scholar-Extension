"""
Unit Tests for Field Classifier Module

Tests all major functionality of the OECD field classification system including:
- Name-based classification
- Topic-based classification
- ISSN-based classification
- Multi-method classification
- Field hierarchy operations
- Validation and search functions

Author: Scholar Extension Team
Date: January 10, 2026
"""

import unittest
import sys
from typing import List, Dict

# Import the module to test
from fieldClassifier import FieldClassifier, classify_journal, get_field_info


class TestFieldClassifierInitialization(unittest.TestCase):
    """Test classifier initialization and basic properties."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FieldClassifier()

    def test_initialization(self):
        """Test that classifier initializes correctly."""
        self.assertIsNotNone(self.classifier)
        self.assertIsInstance(self.classifier, FieldClassifier)

    def test_major_fields_count(self):
        """Test that we have exactly 6 major fields."""
        self.assertEqual(len(self.classifier.MAJOR_FIELDS), 6)

    def test_sub_fields_count(self):
        """Test that we have exactly 42 sub-fields."""
        self.assertEqual(len(self.classifier.SUB_FIELDS), 42)

    def test_major_field_codes(self):
        """Test that major field codes are correct."""
        expected_codes = ['1', '2', '3', '4', '5', '6']
        self.assertEqual(list(self.classifier.MAJOR_FIELDS.keys()), expected_codes)

    def test_keyword_patterns_compiled(self):
        """Test that keyword patterns are compiled."""
        self.assertIsNotNone(self.classifier.keyword_patterns)
        self.assertEqual(len(self.classifier.keyword_patterns), 42)

    def test_field_keywords_exist(self):
        """Test that all sub-fields have keywords defined."""
        for field_code in self.classifier.SUB_FIELDS.keys():
            self.assertIn(field_code, self.classifier.FIELD_KEYWORDS)
            self.assertGreater(len(self.classifier.FIELD_KEYWORDS[field_code]), 0)


class TestClassifyByName(unittest.TestCase):
    """Test journal name-based classification."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FieldClassifier()

    def test_classify_computer_science_journal(self):
        """Test classification of a computer science journal."""
        results = self.classifier.classify_by_name(
            "Journal of Machine Learning Research"
        )
        self.assertGreater(len(results), 0)
        # Should include Computer and information sciences (1.2)
        field_codes = [r['field_code'] for r in results]
        self.assertIn('1.2', field_codes)

    def test_classify_medical_journal(self):
        """Test classification of a medical journal."""
        results = self.classifier.classify_by_name(
            "The New England Journal of Medicine"
        )
        self.assertGreater(len(results), 0)
        # Should include Clinical medicine (3.2)
        field_codes = [r['field_code'] for r in results]
        self.assertIn('3.2', field_codes)

    def test_classify_physics_journal(self):
        """Test classification of a physics journal."""
        results = self.classifier.classify_by_name(
            "Physical Review Letters"
        )
        self.assertGreater(len(results), 0)
        # Should include Physical sciences (1.3)
        field_codes = [r['field_code'] for r in results]
        self.assertIn('1.3', field_codes)

    def test_classify_agricultural_journal(self):
        """Test classification of an agricultural journal."""
        results = self.classifier.classify_by_name(
            "Agricultural Economics"
        )
        self.assertGreater(len(results), 0)
        # Should include Agriculture field (4.1 or 4.5)
        field_codes = [r['field_code'] for r in results]
        self.assertTrue(any(code.startswith('4.') for code in field_codes))

    def test_classify_empty_name(self):
        """Test that empty journal name returns empty results."""
        results = self.classifier.classify_by_name("")
        self.assertEqual(len(results), 0)

    def test_classify_none_name(self):
        """Test that None journal name returns empty results."""
        results = self.classifier.classify_by_name(None)
        self.assertEqual(len(results), 0)

    def test_classify_invalid_name(self):
        """Test that invalid name type returns empty results."""
        results = self.classifier.classify_by_name(12345)
        self.assertEqual(len(results), 0)

    def test_top_n_parameter(self):
        """Test that top_n parameter limits results."""
        results = self.classifier.classify_by_name(
            "Journal of Artificial Intelligence and Machine Learning",
            top_n=2
        )
        self.assertLessEqual(len(results), 2)

    def test_min_confidence_parameter(self):
        """Test that min_confidence filters results."""
        results = self.classifier.classify_by_name(
            "Journal of Machine Learning",
            min_confidence=0.5
        )
        for result in results:
            self.assertGreaterEqual(result['confidence'], 0.5)

    def test_result_structure(self):
        """Test that results have correct structure."""
        results = self.classifier.classify_by_name(
            "Journal of Computer Science"
        )
        if results:
            result = results[0]
            self.assertIn('field_code', result)
            self.assertIn('field_name', result)
            self.assertIn('major_field_code', result)
            self.assertIn('major_field_name', result)
            self.assertIn('confidence', result)
            self.assertIn('matched_keywords', result)

    def test_confidence_range(self):
        """Test that confidence scores are between 0 and 1."""
        results = self.classifier.classify_by_name(
            "Journal of Computational Biology"
        )
        for result in results:
            self.assertGreaterEqual(result['confidence'], 0)
            self.assertLessEqual(result['confidence'], 1)


class TestClassifyByTopics(unittest.TestCase):
    """Test topic-based classification."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FieldClassifier()

    def test_classify_single_topic(self):
        """Test classification with single topic."""
        results = self.classifier.classify_by_topics(["physics"])
        self.assertGreater(len(results), 0)
        field_codes = [r['field_code'] for r in results]
        self.assertIn('1.3', field_codes)

    def test_classify_multiple_topics(self):
        """Test classification with multiple topics."""
        topics = ["machine learning", "neural networks", "AI"]
        results = self.classifier.classify_by_topics(topics)
        self.assertGreater(len(results), 0)
        field_codes = [r['field_code'] for r in results]
        self.assertIn('1.2', field_codes)

    def test_classify_empty_topics(self):
        """Test that empty topics list returns empty results."""
        results = self.classifier.classify_by_topics([])
        self.assertEqual(len(results), 0)

    def test_classify_none_topics(self):
        """Test that None topics returns empty results."""
        results = self.classifier.classify_by_topics(None)
        self.assertEqual(len(results), 0)

    def test_classify_medical_topics(self):
        """Test classification of medical topics."""
        topics = ["cardiology", "surgery", "clinical medicine"]
        results = self.classifier.classify_by_topics(topics)
        self.assertGreater(len(results), 0)
        field_codes = [r['field_code'] for r in results]
        # Should include Clinical medicine (3.2)
        self.assertIn('3.2', field_codes)

    def test_classify_engineering_topics(self):
        """Test classification of engineering topics."""
        topics = ["electrical engineering", "circuits", "electronics"]
        results = self.classifier.classify_by_topics(topics)
        self.assertGreater(len(results), 0)
        field_codes = [r['field_code'] for r in results]
        # Should include Electrical engineering (2.2)
        self.assertIn('2.2', field_codes)


class TestClassifyByISSN(unittest.TestCase):
    """Test ISSN-based classification."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FieldClassifier()
        # Sample ISSN database for testing
        self.issn_db = {
            '0028-0836': ['1.3', '1.6'],  # Nature: Physics & Biology
            '0036-8075': ['1.3', '1.6'],  # Science: Multi-field
            '1476-4687': ['1.2'],         # Nature Biotechnology: CS
            '00280836': ['1.3', '1.6'],   # Alternative format
        }

    def test_classify_valid_issn(self):
        """Test classification with valid ISSN."""
        results = self.classifier.classify_by_issn('0028-0836', self.issn_db)
        self.assertEqual(len(results), 2)
        field_codes = [r['field_code'] for r in results]
        self.assertIn('1.3', field_codes)
        self.assertIn('1.6', field_codes)

    def test_classify_issn_without_hyphen(self):
        """Test classification with ISSN without hyphen."""
        results = self.classifier.classify_by_issn('00280836', self.issn_db)
        self.assertGreater(len(results), 0)

    def test_classify_invalid_issn(self):
        """Test that invalid ISSN returns empty results."""
        results = self.classifier.classify_by_issn('9999-9999', self.issn_db)
        self.assertEqual(len(results), 0)

    def test_classify_empty_issn(self):
        """Test that empty ISSN returns empty results."""
        results = self.classifier.classify_by_issn('', self.issn_db)
        self.assertEqual(len(results), 0)

    def test_classify_none_issn(self):
        """Test that None ISSN returns empty results."""
        results = self.classifier.classify_by_issn(None, self.issn_db)
        self.assertEqual(len(results), 0)

    def test_classify_empty_database(self):
        """Test with empty ISSN database."""
        results = self.classifier.classify_by_issn('0028-0836', {})
        self.assertEqual(len(results), 0)

    def test_result_has_database_source(self):
        """Test that ISSN results have source field."""
        results = self.classifier.classify_by_issn('0028-0836', self.issn_db)
        if results:
            self.assertEqual(results[0]['source'], 'issn_database')

    def test_confidence_is_one(self):
        """Test that ISSN lookup has confidence 1.0."""
        results = self.classifier.classify_by_issn('0028-0836', self.issn_db)
        for result in results:
            self.assertEqual(result['confidence'], 1.0)


class TestGetFieldHierarchy(unittest.TestCase):
    """Test field hierarchy operations."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FieldClassifier()

    def test_get_major_field_hierarchy(self):
        """Test hierarchy for major field."""
        hierarchy = self.classifier.get_field_hierarchy('1')
        self.assertIsNotNone(hierarchy)
        self.assertEqual(hierarchy['field_code'], '1')
        self.assertEqual(hierarchy['level'], 'major')
        self.assertIsNone(hierarchy['parent'])
        self.assertGreater(len(hierarchy['children']), 0)

    def test_get_sub_field_hierarchy(self):
        """Test hierarchy for sub-field."""
        hierarchy = self.classifier.get_field_hierarchy('1.2')
        self.assertIsNotNone(hierarchy)
        self.assertEqual(hierarchy['field_code'], '1.2')
        self.assertEqual(hierarchy['level'], 'sub')
        self.assertIsNotNone(hierarchy['parent'])
        self.assertEqual(hierarchy['parent']['field_code'], '1')

    def test_sub_field_has_siblings(self):
        """Test that sub-field has siblings."""
        hierarchy = self.classifier.get_field_hierarchy('1.2')
        self.assertGreater(len(hierarchy['siblings']), 0)

    def test_invalid_field_code(self):
        """Test that invalid field code returns None."""
        hierarchy = self.classifier.get_field_hierarchy('99.99')
        self.assertIsNone(hierarchy)

    def test_empty_field_code(self):
        """Test that empty field code returns None."""
        hierarchy = self.classifier.get_field_hierarchy('')
        self.assertIsNone(hierarchy)

    def test_all_major_fields_have_children(self):
        """Test that all major fields have at least one child."""
        for major_code in self.classifier.MAJOR_FIELDS.keys():
            hierarchy = self.classifier.get_field_hierarchy(major_code)
            self.assertGreater(len(hierarchy['children']), 0)


class TestClassifyMultiMethod(unittest.TestCase):
    """Test multi-method classification."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FieldClassifier()
        self.issn_db = {
            '0028-0836': ['1.3', '1.6']
        }

    def test_all_methods(self):
        """Test using all classification methods together."""
        results = self.classifier.classify_multi_method(
            journal_name="Nature Physics",
            topics_list=["physics", "quantum mechanics"],
            issn='0028-0836',
            issn_database=self.issn_db
        )
        self.assertGreater(len(results['classifications']), 0)
        self.assertGreater(results['total_methods'], 0)

    def test_name_only(self):
        """Test with only journal name."""
        results = self.classifier.classify_multi_method(
            journal_name="Journal of Computer Science"
        )
        self.assertIn('name_classification', results['methods_used'])

    def test_topics_only(self):
        """Test with only topics."""
        results = self.classifier.classify_multi_method(
            topics_list=["machine learning", "AI"]
        )
        self.assertIn('topic_classification', results['methods_used'])

    def test_issn_only(self):
        """Test with only ISSN."""
        results = self.classifier.classify_multi_method(
            issn='0028-0836',
            issn_database=self.issn_db
        )
        self.assertIn('issn_lookup', results['methods_used'])

    def test_no_methods(self):
        """Test with no inputs."""
        results = self.classifier.classify_multi_method()
        self.assertEqual(len(results['classifications']), 0)
        self.assertEqual(results['total_methods'], 0)

    def test_aggregated_confidence(self):
        """Test that results have aggregated confidence."""
        results = self.classifier.classify_multi_method(
            journal_name="Nature",
            topics_list=["biology"]
        )
        if results['classifications']:
            for classification in results['classifications']:
                self.assertIn('aggregated_confidence', classification)


class TestValidationAndUtility(unittest.TestCase):
    """Test validation and utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FieldClassifier()

    def test_validate_valid_major_field(self):
        """Test validation of valid major field code."""
        self.assertTrue(self.classifier.validate_field_code('1'))

    def test_validate_valid_sub_field(self):
        """Test validation of valid sub-field code."""
        self.assertTrue(self.classifier.validate_field_code('1.2'))

    def test_validate_invalid_field(self):
        """Test validation of invalid field code."""
        self.assertFalse(self.classifier.validate_field_code('99.99'))

    def test_get_all_fields_major(self):
        """Test getting all major fields."""
        fields = self.classifier.get_all_fields(level='major')
        self.assertEqual(len(fields), 6)

    def test_get_all_fields_sub(self):
        """Test getting all sub-fields."""
        fields = self.classifier.get_all_fields(level='sub')
        self.assertEqual(len(fields), 42)

    def test_get_all_fields_all(self):
        """Test getting all fields."""
        fields = self.classifier.get_all_fields(level='all')
        self.assertEqual(len(fields), 48)  # 6 + 42

    def test_search_fields(self):
        """Test field search functionality."""
        results = self.classifier.search_fields("computer")
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIn('computer', result['field_name'].lower())

    def test_search_fields_case_insensitive(self):
        """Test that field search is case-insensitive."""
        results1 = self.classifier.search_fields("computer")
        results2 = self.classifier.search_fields("COMPUTER")
        self.assertEqual(len(results1), len(results2))

    def test_search_fields_no_match(self):
        """Test field search with no matches."""
        results = self.classifier.search_fields("xyz123abc")
        self.assertEqual(len(results), 0)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    def test_classify_journal_function(self):
        """Test the classify_journal convenience function."""
        results = classify_journal("Journal of Machine Learning")
        self.assertIsInstance(results, list)

    def test_get_field_info_function(self):
        """Test the get_field_info convenience function."""
        info = get_field_info('1.2')
        self.assertIsNotNone(info)
        self.assertEqual(info['field_code'], '1.2')

    def test_get_field_info_invalid(self):
        """Test get_field_info with invalid code."""
        info = get_field_info('99.99')
        self.assertIsNone(info)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FieldClassifier()

    def test_classify_multidisciplinary_journal(self):
        """Test classification of multidisciplinary journal."""
        results = self.classifier.classify_by_name(
            "Nature Medicine Biotechnology Journal",
            top_n=5
        )
        # Should return multiple fields
        self.assertGreater(len(results), 1)

    def test_classify_very_long_name(self):
        """Test with very long journal name."""
        long_name = "International Journal of Advanced Research in " * 10
        results = self.classifier.classify_by_name(long_name)
        # Should handle without error
        self.assertIsInstance(results, list)

    def test_classify_special_characters(self):
        """Test with special characters in name."""
        results = self.classifier.classify_by_name(
            "Journal of C++, AI & Machine-Learning"
        )
        self.assertIsInstance(results, list)

    def test_classify_unicode_characters(self):
        """Test with Unicode characters."""
        results = self.classifier.classify_by_name(
            "Journal of Médecine et Santé"
        )
        self.assertIsInstance(results, list)

    def test_issn_normalization(self):
        """Test that different ISSN formats work."""
        issn_db = {'00280836': ['1.3']}
        # Test with hyphen
        results1 = self.classifier.classify_by_issn('0028-0836', issn_db)
        # Test without hyphen
        results2 = self.classifier.classify_by_issn('00280836', issn_db)
        # Both should return results
        self.assertGreater(len(results1), 0)
        self.assertGreater(len(results2), 0)


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world classification scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.classifier = FieldClassifier()

    def test_nature_journal(self):
        """Test classification of Nature journal."""
        results = self.classifier.classify_by_name("Nature")
        # Nature is multidisciplinary, might not have strong matches
        self.assertIsInstance(results, list)

    def test_ieee_journal(self):
        """Test classification of IEEE journal."""
        results = self.classifier.classify_by_name(
            "IEEE Transactions on Pattern Analysis and Machine Intelligence"
        )
        self.assertGreater(len(results), 0)
        field_codes = [r['field_code'] for r in results]
        # Should include Computer science or Engineering
        has_cs_or_eng = any(code.startswith('1.2') or code.startswith('2.')
                           for code in field_codes)
        self.assertTrue(has_cs_or_eng)

    def test_medical_journal_lancet(self):
        """Test classification of The Lancet."""
        results = self.classifier.classify_by_name("The Lancet")
        # "Lancet" alone might not match, but this tests real scenario
        self.assertIsInstance(results, list)

    def test_plos_journal(self):
        """Test classification of PLOS journal."""
        results = self.classifier.classify_by_name("PLOS Biology")
        self.assertGreater(len(results), 0)
        field_codes = [r['field_code'] for r in results]
        self.assertIn('1.6', field_codes)  # Biological sciences

    def test_multidisciplinary_with_topics(self):
        """Test multidisciplinary journal with topic hints."""
        results = self.classifier.classify_multi_method(
            journal_name="Science Advances",
            topics_list=["physics", "chemistry", "biology"]
        )
        self.assertGreater(len(results['classifications']), 0)
        # Should detect multiple natural science fields
        field_codes = [r['field_code'] for r in results['classifications']]
        natural_science_fields = [code for code in field_codes
                                 if code.startswith('1.')]
        self.assertGreater(len(natural_science_fields), 0)


def run_tests():
    """Run all tests and display results."""
    print("=" * 80)
    print("OECD Field Classifier - Unit Tests")
    print("=" * 80)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFieldClassifierInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestClassifyByName))
    suite.addTests(loader.loadTestsFromTestCase(TestClassifyByTopics))
    suite.addTests(loader.loadTestsFromTestCase(TestClassifyByISSN))
    suite.addTests(loader.loadTestsFromTestCase(TestGetFieldHierarchy))
    suite.addTests(loader.loadTestsFromTestCase(TestClassifyMultiMethod))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationAndUtility))
    suite.addTests(loader.loadTestsFromTestCase(TestConvenienceFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldScenarios))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print("=" * 80)
    print("Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("=" * 80)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
