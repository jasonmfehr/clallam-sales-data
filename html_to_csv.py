#!/usr/bin/python3

import sys
import glob
from bs4 import BeautifulSoup
import csv
import os

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

for html_file in html_files:
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    table = soup.find('table', id='saleSearchResults_resultsTable')
    if not table:
        print(f"Warning: Table not found in file {html_file}, skipping.")
        continue

    # Extract headers from the first table found (write only once)
    if not headers_written:
        headers = [th.get_text(strip=True) for th in table.find_all('tr')[0].find_all('th')]
        headers_written = True

    # Extract rows
    for tr in table.find_all('tr')[1:]:  # Skip header row
        cells = tr.find_all('td')
        row = [cell.get_text(strip=True) for cell in cells]
        if row:
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

