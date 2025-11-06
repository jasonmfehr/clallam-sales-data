import sys
import glob
from bs4 import BeautifulSoup
import csv
import re

# Check command-line argument
if len(sys.argv) < 2:
    print("Usage: python extract_sales_tables.py '<file_glob>'")
    sys.exit(1)

file_glob = sys.argv[1]
html_files = glob.glob(file_glob)

if not html_files:
    print(f"No files found matching: {file_glob}")
    sys.exit(1)

# Output CSV file
csv_file = 'sales_results.csv'

all_rows = []
headers_written = False

VALID_CITIES = ["CLALLAM BAY", "SEQUIM", "FORKS", "PORT ANGELES", "BEAVER", "SEKIU", "JOYCE", "NEAH BAY", "LA PUSH"]

def clean_text(text):
    """Remove newlines and extra spaces from cell text."""
    return ' '.join(text.split())

def split_situs(situs_text, html_file):
    """
    Split the ss-situs text into address, city.
    Expected format: "{address} {city}, WA {zip}" with {zip} being optional
    Abort if no valid city is found.
    """
    situs_text = clean_text(situs_text)
    # Match city first
    for city in VALID_CITIES:
        pattern = re.escape(city) + r', WA'
        match = re.search(pattern, situs_text, re.IGNORECASE)
        if match:
            address = situs_text[:match.start()].strip()
            return address, city
    # No valid city found → abort
    print(f"WARNING: Invalid city in ss-situs field in file '{html_file}': '{situs_text}'")
    return "", ""

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    table = soup.find('table', id='saleSearchResults_resultsTable')
    if not table:
        print(f"Warning: Table not found in file {html_file}, skipping.")
        continue

    # Extract headers from the first table found (write only once)
    if not headers_written:
        headers = []
        for th in table.find_all('tr')[0].find_all('th')[2:]:  # Skip first two columns
            if 'ss-view-map' in th.get('class', []) or th.find('a'):
                continue
            text = clean_text(th.get_text())
            if text:
                if 'ss-situs' in th.get('class', []):
                    headers.extend(['Address', 'City'])
                else:
                    headers.append(text)
        headers_written = True

    # Extract rows
    for tr in table.find_all('tr')[1:]:  # Skip header row
        cells = tr.find_all('td')[2:]  # Skip first two columns
        row = []
        skip_row = False

        for cell in cells:
            # Skip cell if it contains <a> or has class ss-view-map
            if 'ss-view-map' in cell.get('class', []) or cell.find('a'):
                continue
            text = clean_text(cell.get_text())

            # Drop row if ss-situs is blank
            if 'ss-situs' in cell.get('class', []) and text == '':
                skip_row = True
                break

            # Split ss-situs into three columns
            if 'ss-situs' in cell.get('class', []):
                address, city = split_situs(text, html_file)
                if address == "" and city == "":
                    skip_row = True
                    break
                row.extend([address, city])
            else:
                row.append(text)

        if skip_row:
            continue  # Skip this row entirely

        # Safety check: row must match header length unless the row contains 0 columns in which case it is a multi-property divider row
        if len(row) == 0:
            continue
        elif len(row) != len(headers):
            import pdb;pdb.set_trace()
            print(f"Error: Row length {len(row)} does not match header length {len(headers)} in file '{html_file}'.")
            print("Row data:", row)
            sys.exit(1)

        all_rows.append(row)

# Write all rows to CSV
if all_rows:
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_rows)
    print(f"CSV file '{csv_file}' has been created successfully with {len(all_rows)} rows.")
else:
    print("No data found in any files.")

