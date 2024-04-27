import csv
import sqlite3
from pathlib import Path

USEFUL_TABLES = [
"ZARTISTMO",
"ZTAGCOLLECTIONMO",
"ZSYNCMETADATAMO",
"ZTAGMO",
]

output_folder = Path("tables")
output_folder.mkdir(exist_ok=True)

conn = sqlite3.connect("ShazamDataModel.sqlite")
cursor = conn.cursor()

for table in USEFUL_TABLES:
    cursor.execute(f"select * from {table};")
    with (output_folder / f"{table}.csv").open('w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description])
        csv_writer.writerows(cursor)

conn.close()
