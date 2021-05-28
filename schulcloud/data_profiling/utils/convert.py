"""
Converts JSON with nested fields into a flattened CSV file.
https://stackoverflow.com/questions/1871524/how-can-i-convert-json-to-csv
"""

import csv
import json

import csv_to_sqlite
import ijson
import pandas as pd
# from https://stackoverflow.com/a/28246154/473201
from ordered_set import OrderedSet
from tqdm import tqdm


# from orderedset import OrderedSet
from schulcloud.data_profiling.utils.data_cleaning_utils import get_prepared_record


def flattenjson( b, prefix='', delim='/', val=None ):
  if val is None:
    val = {}

  if isinstance( b, dict ):
    for j in b.keys():
      flattenjson(b[j], prefix + delim + j, delim, val)
  elif isinstance( b, list ):
    get = b
    for j in range(len(get)):
      key = str(j)

      # If the nested data contains its own key, use that as the header instead.
      if isinstance( get[j], dict ):
        if 'key' in get[j]:
          key = get[j]['key']

      flattenjson(get[j], prefix + delim + key, delim, val)
  else:
    val[prefix] = b

  return val

def convert_file(dataset_json, dataset_csv):
  # TODO: Check if file exists.

  print("Loading and Flattening...")

  allRows = []
  fieldnames = OrderedSet()
  with open(dataset_json) as json_file:
    data = json.load(json_file)
    for obj in data:
      # print 'orig:\n'
      # print obj
      flattened = flattenjson(obj)
      #print 'keys: %s' % flattened.keys()
      # print 'flattened:\n'
      # print flattened
      fieldnames.update(flattened.keys())
      allRows.append(flattened)

  print("Exporting to CSV...")
  outfilename = dataset_csv
  count = 0
  with open(outfilename, 'w') as file:
    csvwriter = csv.DictWriter(file, fieldnames=fieldnames)
    csvwriter.writeheader()
    for obj in allRows:
      # print 'allRows:\n'
      # print obj
      csvwriter.writerow(obj)
      count += 1

  print("Wrote %d rows" % count)

def convert_json_to_csv(dataset_json: str, dataset_csv: str):
  items = []
  with open(dataset_json, 'rb') as json_file:
    for item in tqdm(ijson.items(json_file, "item")):
      item = get_prepared_record(item)
      del item["thumbnail"]
      items.append(item)

  df = pd.DataFrame.from_records(items)
  json_struct = json.loads(df.to_json(orient="records"))
  df_flat = pd.io.json.json_normalize(json_struct)  # use pd.io.json
  df_flat.to_csv(dataset_csv, index=False)


def convert_csv_to_sqlite(dataset_csv: str, dataset_sqlite: str):
  # https://github.com/zblesk/csv-to-sqlite: all the usual options are supported
  # options = csv_to_sqlite.CsvOptions(typing_style="full", encoding="windows-1250")
  options = csv_to_sqlite.CsvOptions(drop_tables=True)
  # input_files = ["abilities.csv", "moves.csv"]  # pass in a list of CSV files
  input_files = [dataset_csv]  # pass in a list of CSV files
  # input_files = dataset_csv  # pass in a list of CSV files
  csv_to_sqlite.write_csv(input_files, dataset_sqlite, options)
