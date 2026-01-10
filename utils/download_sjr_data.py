import os
import pandas as pd
import sys

def provide_instructions():
    """Prints instructions for manual download of SJR data."""
    print("=" * 60)
    print("SCIMAGOJR DATA DOWNLOAD INSTRUCTIONS")
    print("=" * 60)
    print("1. Go to: https://www.scimagojr.com/journalrank.php")
    print("2. Select the year and category you are interested in (default is all).")
    print("3. Click on the 'Download data' button (usually exports to CSV).")
    print("4. Save the downloaded file as 'scimagojr.csv' in the following directory:")
    print(f"   {os.path.abspath('scholar_extention_trung/data/raw/')}")
    print("=" * 60)

def validate_csv(file_path):
    """Validates the CSV format for SJR data."""
    try:
        # SJR CSVs usually use ';' as delimiter
        df = pd.read_csv(file_path, sep=';', encoding='utf-8')

        required_columns = ['Rank', 'Sourceid', 'Title', 'Type', 'Issn', 'SJR', 'SJR Best Quartile']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"Warning: Missing expected columns: {missing_columns}")
            print("The script might need adjustments for this specific CSV version.")
            return False

        print(f"Success: CSV validated. Found {len(df)} journals.")
        print(f"Columns found: {list(df.columns)}")
        return True
    except Exception as e:
        print(f"Error validating CSV: {e}")
        return False

def main():
    raw_data_dir = os.path.join('scholar_extention_trung', 'data', 'raw')
    csv_filename = 'scimagojr.csv'
    csv_path = os.path.join(raw_data_dir, csv_filename)

    # 1. Create directory if it doesn't exist
    if not os.path.exists(raw_data_dir):
        print(f"Creating directory: {raw_data_dir}")
        os.makedirs(raw_data_dir)

    # 2. Check if file exists
    if not os.path.exists(csv_path):
        print(f"Error: {csv_filename} not found in {raw_data_dir}")
        provide_instructions()
        sys.exit(1)

    # 3. Validate file
    print(f"Found {csv_filename}. Validating...")
    if validate_csv(csv_path):
        print("Data is ready for processing.")
    else:
        print("Validation failed. Please check the CSV file format.")
        sys.exit(1)

if __name__ == "__main__":
    main()
