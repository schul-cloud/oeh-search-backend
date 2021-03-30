"""
Converts JSON with nested fields into a flattened CSV file.
https://stackoverflow.com/questions/1871524/how-can-i-convert-json-to-csv
"""

import sys
import json
import csv
import os

import jsonlines

# from orderedset import OrderedSet

# from https://stackoverflow.com/a/28246154/473201
from jsonlines import Error
from orderedset._orderedset import OrderedSet


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


if __name__ == '__main__':
  main(sys.argv)