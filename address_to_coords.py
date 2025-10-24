import ssl
import certifi
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

import duckdb
import sys

from OSMPythonTools.nominatim import Nominatim

# Create a Nominatim instance
nominatim = Nominatim(userAgent="clallam-county-sales-geocoder/0.1")

# Connect to duckdb
with duckdb.connect(database=sys.argv[1], read_only=False) as conn:
    results = conn.execute('select "Geo ID","Sale Date", Address from sales_data WHERE city = \'PORT ANGELES\' order by "Geo ID"').fetchall()

    for row in results:
        print(row)
        import pdb;pdb.set_trace()
        address = f"{row[2]}, Clallam County, WA, USA"
        result = nominatim.query(address)

        # Extract latitude and longitude
        if result and result.toJSON():
            lat = result.toJSON()[0]['lat']
            lon = result.toJSON()[0]['lon']
            print(f"{address} => Latitude: {lat}, Longitude: {lon}")
        else:
            print("Address not found")

# address = "174, Camelot Road, Clallam County, WA, USA"
# # address = "1600 Amphitheatre Parkway, Mountain View, CA, USA"
# result = nominatim.query(address)

# # Extract latitude and longitude
# if result and result.toJSON():
#     lat = result.toJSON()[0]['lat']
#     lon = result.toJSON()[0]['lon']
#     print(f"{address} => Latitude: {lat}, Longitude: {lon}")
# else:
#     print("Address not found")
