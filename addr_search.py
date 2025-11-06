# Simple script to call nominatim with a provided address.
# Outputs the latitude and longitude of that address.

import ssl
import certifi
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

import sys

from OSMPythonTools.nominatim import Nominatim

nominatim = Nominatim(userAgent="clallam-county-sales-geocoder/0.1 addr_search")

address = sys.argv[1]
# address = "1600 Amphitheatre Parkway, Mountain View, CA, USA"
result = nominatim.query(address)

# Extract latitude and longitude
if result and result.toJSON():
    lat = result.toJSON()[0]['lat']
    lon = result.toJSON()[0]['lon']
    print(f"{address} => Latitude: {lat}, Longitude: {lon}")
else:
    print("Address not found")