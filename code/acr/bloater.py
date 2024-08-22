# <legal>
# 'Redemption' Automated Code Repair Tool
#
# Copyright 2023, 2024 Carnegie Mellon University.
#
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
# INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
# UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
# AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
# PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
# THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
# KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
# INFRINGEMENT.
#
# Licensed under a MIT (SEI)-style license, please see License.txt or
# contact permission@sei.cmu.edu for full terms.
#
# [DISTRIBUTION STATEMENT A] This material has been approved for public
# release and unlimited distribution.  Please see Copyright notice for
# non-US Government use and distribution.
#
# This Software includes and/or makes use of Third-Party Software each
# subject to its own license.
#
# DM23-2165
# </legal>

# bloater replaces all references of debloated clang AST

import json
import sys
import time

def build_id_cache(data, cache):
  if isinstance(data, dict):
    if 'id' in data:
      cache[data['id']] = data
    for value in data.values():
      build_id_cache(value, cache)
  elif isinstance(data, list):
    for item in data:
      build_id_cache(item, cache)

def resolve_references(data, cache):
  if isinstance(data, dict):
    for key, value in data.items():
      resolve_references(value, cache)
    if 'refId' in data:
      ref_id = data['refId']
      if ref_id in cache:
        referenced_data = cache[ref_id]
        data.clear()
        data.update(referenced_data)
  elif isinstance(data, list):
    for index in range(len(data)):
      resolve_references(data[index], cache)
    for index, item in enumerate(data):
      if isinstance(item, dict) and 'refId' in item:
        ref_id = item['refId']
        if ref_id in cache:
          data[index] = cache[ref_id]

def debloat(data):
  cache = {}
  build_id_cache(data, cache)
  resolve_references(data, cache)
  return data

def main(json_read, json_write):

  running_time = time.perf_counter()
  timestamp = running_time

  try:
    with open(json_read, 'r') as file:
      json_data = json.load(file)
  except Exception as e:
    print(f"Error reading JSON file: {e}")
    return

  print(f"opened file in: {(time.perf_counter() - timestamp):0.2f} seconds")

  timestamp = time.perf_counter()
  cache = {}
  build_id_cache(json_data, cache)

  print(f"built cache in: {(time.perf_counter() - timestamp):0.2f} seconds")

  timestamp = time.perf_counter()
  resolve_references(json_data, cache)
  print(f"resolved refs in: {(time.perf_counter() - timestamp):0.2f} seconds")

  timestamp = time.perf_counter()
  try:
    with open(json_write, "w+") as file:
      file.write(json.dumps(json_data, indent=2))
  except Exception as e:
    print(f"Error writing JSON file: {e}")
    return

  print(f"wrote file in: {(time.perf_counter() - timestamp):0.2f} seconds")
  print(f"total running time: {(time.perf_counter() - running_time):0.2f} seconds")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
