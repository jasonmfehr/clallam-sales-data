# Clallam County, Washington Home Sales
This repo contains code and a DuckDB database file with a years worth of home sales in the Washington state county of Clallam.  Sourcing the data and cleaning it are handled through several scripts.

## Sourcing Data
Home sales can be found on the [assessor's website](https://websrv22.clallam.net/propertyaccess/SaleSearch.aspx).  After performing a search, save each results page as a separate html file.  Then, run the `html_to_csv.py` script passing it a file glob to use when locating the results html pages:
```bash
python html_to_csv.py "page*.html"
```

This script parses through the table of results in each html file and outputs a single csv named `sales_results.csv`.

## Importing Data to DuckDB
Start a new DuckDB file (or open the existing `sales_data.duckdb` file).  Then, import the csv as a table:
```sql
create table sales_data as select * from read_csv_auto('sales_results.csv');
```

## Data Enhancement
Add columns to the DuckDB table to store latitude and longitude:
```sql
alter table sales_data add column lat(float);
alter table sales_data add column lng float;
```

Enhance the addresses in the table adding their latitude and longitude as determined by Nominatim.  Note this script contains both a hardcoded db table name and a query limiting results to only the city of Port Angeles:
```bash
python address_to_coords.py sales_data.duckdb
```

Note: due to issues with the sales data, not all addresses will be found.  This situation happens mostly when land is sold.

## Find Close Sales
Finally, run a DuckDB query to located sales close to a given latitude and longitude.  This query locates sales close to the Clallam County Courthouse.  The results shows both the raw distance and the distance converted to miles that each property is from the courthouse:

```sql
LOAD SPATIAL;
SELECT
  "property id",
  "geo id",
  address,
  st_distance(st_point(48.115560, -123.431911),st_point(lat,lng)) as dist,
  round(ST_Length_Spheroid(st_makeline(st_point(48.115560, -123.431911),st_point(lat,lng))) * 0.000621371,2) dist_miles
FROM sales_data
WHERE
  lat is not null and
  lng is not null
ORDER BY dist limit 20;
```
