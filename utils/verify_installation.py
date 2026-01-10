#!/usr/bin/env python3
"""
Quick verification script for Impact Factor Collector installation.

Run this to verify the module is correctly installed and working.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import pandas
        print("  ✓ pandas")
    except ImportError:
        print("  ✗ pandas - Run: pip install pandas")
        return False

    try:
        import requests
        print("  ✓ requests")
    except ImportError:
        print("  ✗ requests - Run: pip install requests")
        return False

    try:
        from impactFactorCollector import (
            ImpactFactorCollector,
            SJRDataLoader,
            OpenAlexMetrics
        )
        print("  ✓ impactFactorCollector")
    except ImportError as e:
        print(f"  ✗ impactFactorCollector - {e}")
        return False

    return True


def test_sjr_data_loader():
    """Test SJRDataLoader basic functionality."""
    print("\nTesting SJRDataLoader...")
    from impactFactorCollector import SJRDataLoader

    loader = SJRDataLoader()

    # Test ISSN normalization
    assert loader._normalize_issn("0028-0836") == "00280836", "ISSN normalization failed"
    assert loader._normalize_issn("00280836") == "00280836", "ISSN normalization failed"
    assert loader._normalize_issn("invalid") == "", "Invalid ISSN should return empty"

    print("  ✓ ISSN normalization works")

    # Test CSV loading (will fail if file doesn't exist, which is OK)
    sjr_path = "data/raw/scimagojr.csv"
    if os.path.exists(sjr_path):
        result = loader.load_sjr_csv(sjr_path)
        if result:
            print(f"  ✓ SJR CSV loaded successfully ({len(loader.sjr_data)} journals)")
        else:
            print("  ⚠ SJR CSV found but failed to load")
    else:
        print(f"  ⚠ SJR CSV not found at: {sjr_path}")
        print("    This is optional - download from: https://www.scimagojr.com/journalrank.php")

    return True


def test_openalex_client():
    """Test OpenAlexMetrics client initialization."""
    print("\nTesting OpenAlexMetrics...")
    from impactFactorCollector import OpenAlexMetrics

    client = OpenAlexMetrics(email="test@example.com")
    print("  ✓ OpenAlexMetrics client initialized")

    # Don't make actual API calls in verification script
    print("  ℹ Skipping live API test (run example_impact_factor_collector.py for full test)")

    return True


def test_collector():
    """Test ImpactFactorCollector initialization."""
    print("\nTesting ImpactFactorCollector...")
    from impactFactorCollector import ImpactFactorCollector

    # Test without SJR data
    collector = ImpactFactorCollector()
    print("  ✓ ImpactFactorCollector initialized (no SJR data)")

    # Test with SJR data if available
    sjr_path = "data/raw/scimagojr.csv"
    if os.path.exists(sjr_path):
        collector = ImpactFactorCollector(sjr_csv_path=sjr_path)
        print("  ✓ ImpactFactorCollector initialized (with SJR data)")

    return True


def test_data_structures():
    """Test that data structures are correct."""
    print("\nTesting data structures...")
    from impactFactorCollector import ImpactFactorCollector

    collector = ImpactFactorCollector()

    # Test get_impact_factor returns correct structure
    result = collector.get_impact_factor("0000-0000")  # Fake ISSN

    required_keys = ['if_value', 'year', 'source', 'quartile', 'h_index', 'alternative_metrics']
    for key in required_keys:
        assert key in result, f"Missing required key: {key}"

    assert result['source'] == 'none', "Source should be 'none' for non-existent ISSN"
    assert result['if_value'] is None, "if_value should be None for non-existent ISSN"

    print("  ✓ Data structure is correct")

    return True


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Impact Factor Collector - Installation Verification")
    print("=" * 60)

    tests = [
        ("Dependencies", test_imports),
        ("SJRDataLoader", test_sjr_data_loader),
        ("OpenAlexMetrics", test_openalex_client),
        ("ImpactFactorCollector", test_collector),
        ("Data Structures", test_data_structures),
    ]

    failed = []

    for name, test_func in tests:
        try:
            if not test_func():
                failed.append(name)
        except Exception as e:
            print(f"\n✗ {name} test failed with error: {e}")
            import traceback
            traceback.print_exc()
            failed.append(name)

    print("\n" + "=" * 60)

    if not failed:
        print("✓ All verification tests passed!")
        print("\nYou can now use the Impact Factor Collector.")
        print("\nNext steps:")
        print("  1. Download SJR data: python download_sjr_data.py")
        print("  2. Run examples: python example_impact_factor_collector.py")
        print("  3. Run tests: python test_impactFactorCollector.py")
    else:
        print(f"✗ {len(failed)} test(s) failed:")
        for test_name in failed:
            print(f"  - {test_name}")
        print("\nPlease fix the issues above before using the module.")
        sys.exit(1)

    print("=" * 60)


if __name__ == "__main__":
    main()
