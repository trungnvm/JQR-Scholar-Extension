"""
Example script demonstrating the usage of journalListAggregator.

This script shows how to:
1. Fetch journals by field
2. Fetch all journals
3. Use individual APIs
4. Enrich data with multiple sources
5. Save results to CSV
"""

from journalListAggregator import JournalAggregator, OpenAlexAPI, CrossrefAPI


def example_fetch_by_field():
    """Example: Fetch journals for a specific field."""
    print("\n=== Example 1: Fetch journals by field ===")

    # Initialize aggregator
    aggregator = JournalAggregator(email="your-email@example.com")

    # Fetch journals for machine learning
    df = aggregator.fetch_by_field("machine learning", limit=100)

    print(f"Found {len(df)} journals")
    print("\nFirst 5 journals:")
    print(df[['name', 'issn', 'field', 'source']].head())

    # Save to CSV
    aggregator.save_to_csv(df, "ml_journals.csv")


def example_fetch_all_journals():
    """Example: Fetch comprehensive journal list."""
    print("\n=== Example 2: Fetch all journals ===")

    aggregator = JournalAggregator(email="your-email@example.com")

    # Fetch first 500 journals
    df = aggregator.fetch_all_journals(limit=500)

    print(f"Found {len(df)} journals")
    print("\nJournals by source:")
    print(df['source'].value_counts())

    # Save to CSV
    aggregator.save_to_csv(df, "all_journals.csv")


def example_openalex_direct():
    """Example: Use OpenAlex API directly."""
    print("\n=== Example 3: OpenAlex API direct usage ===")

    openalex = OpenAlexAPI(email="your-email@example.com")

    # Fetch computer science journals
    df = openalex.fetch_journals_by_field("computer science", limit=50)

    print(f"Found {len(df)} computer science journals")
    print("\nTop journals by citations:")
    if 'cited_by_count' in df.columns:
        top_journals = df.nlargest(5, 'cited_by_count')[['name', 'cited_by_count', 'works_count']]
        print(top_journals)


def example_crossref_enrichment():
    """Example: Enrich journal data with Crossref."""
    print("\n=== Example 4: Crossref enrichment ===")

    crossref = CrossrefAPI(email="your-email@example.com")

    # Fetch specific journal by ISSN (Nature)
    journal = crossref.fetch_journal_by_issn("0028-0836")

    if journal:
        print(f"Journal: {journal['name']}")
        print(f"Publisher: {journal.get('publisher', 'N/A')}")
        print(f"Subjects: {journal.get('subjects', 'N/A')}")

    # Batch enrichment
    issn_list = ["0028-0836", "0036-8075", "1476-4687"]  # Nature, Science, Nature Reviews
    df = crossref.enrich_journal_data(issn_list)

    print(f"\nEnriched {len(df)} journals")
    print(df[['name', 'issn', 'publisher']])


def example_multiple_fields():
    """Example: Fetch journals for multiple fields and combine."""
    print("\n=== Example 5: Multiple fields ===")

    aggregator = JournalAggregator(email="your-email@example.com")

    fields = ["artificial intelligence", "data science", "bioinformatics"]
    all_journals = []

    for field in fields:
        print(f"Fetching journals for: {field}")
        df = aggregator.fetch_by_field(field, limit=50)
        all_journals.append(df)

    # Combine all dataframes
    import pandas as pd
    combined_df = pd.concat(all_journals, ignore_index=True)

    # Deduplicate
    combined_df = aggregator.deduplicate_journals(combined_df)

    print(f"\nTotal unique journals: {len(combined_df)}")

    # Save combined results
    aggregator.save_to_csv(combined_df, "multiple_fields_journals.csv")


def example_with_enrichment():
    """Example: Fetch from OpenAlex and enrich with Crossref."""
    print("\n=== Example 6: Fetch with enrichment ===")

    aggregator = JournalAggregator(email="your-email@example.com")

    # Fetch with Crossref enrichment
    df = aggregator.fetch_by_field(
        "biology",
        limit=20,
        enrich_with_crossref=True
    )

    print(f"Found and enriched {len(df)} journals")
    print("\nSample data:")
    print(df[['name', 'issn', 'field', 'source']].head(10))


if __name__ == "__main__":
    print("Journal Aggregator Examples")
    print("=" * 50)

    # Run examples (comment out the ones you don't need)

    # Basic examples
    example_fetch_by_field()
    # example_fetch_all_journals()

    # Direct API usage
    # example_openalex_direct()
    # example_crossref_enrichment()

    # Advanced examples
    # example_multiple_fields()
    # example_with_enrichment()

    print("\n" + "=" * 50)
    print("Examples completed!")
