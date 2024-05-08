#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

import subprocess, json, argparse

#####################################################################
# This script provides the following: 
#
# 1. pytest cases for scenarios
#    pytest -s ast_comparer.py --config scenarios.json 
# 2. Compare JSON ASTs
#    ./ast_comparer.py --compare FILE_1.json FILE_2.json
# 3. Generate an AST from Clang and then compare it to an existing JSON AST
#    ./ast_comparer.py --config scenarios.json
#
# The scenarios config file specifies which clang to use as well as a test name, 
# json AST file, and source file that should be used to test against the json file
#
#####################################################################

"""
Loads a JSON file into a Python JSON Object

file_path (str): location of json file
"""
def load_json_from_file(file_path):
  try:
    with open(file_path, 'r') as file:
      try:
        json_data = json.load(file)
        return json_data
      except json.JSONDecodeError as e:
        print(f"ERROR: Malformed JSON in file '{file_path}': {e}")
        return None
  except FileNotFoundError:
    print(f"ERROR: File '{file_path}' not found.")
    return None

#####################################################################

"""
Generates JSON output from clang into a Python JSON Object.

source_file (str): location of source file, e.g., .c, .cpp
clang_location (str): location of clang to use
"""
def clang_ast_dump_json(source_file, clang_location):
  try:
    # Run clang command
    result = subprocess.run(
      [clang_location, '-fsyntax-only', '-Xclang', '-ast-dump=json', source_file],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      universal_newlines=True
    )

    # Check if clang command produced an error
    if result.returncode != 0:
      print(f"ERROR: Clang encountered an error:\n{result.stderr}")
      return None

    # Load JSON output from clang into Python JSON object
    try:
      json_data = json.loads(result.stdout)
      return json_data
    except json.JSONDecodeError as e:
      print(f"ERROR: Malformed JSON output from clang:\n{e}")
      return None

  except FileNotFoundError:
    print(f"ERROR: Source file '{source_file}' not found.")
    return None

#####################################################################

"""
Recursively compare JSON nodes and print any mismatches.

Args:
node1 (any): First JSON node to compare.
node2 (any): Second JSON node to compare.

Return: number of mismatches
"""
def compare_json_nodes(node1, node2):

  mismatches = 0

  # inner function for walking the JSON trees
  def compare(node1, node2, path=""):
    if isinstance(node1, dict) and isinstance(node2, dict):
      for key in set(node1.keys()) | set(node2.keys()):
        compare(node1.get(key), node2.get(key), f"{path}.{key}" if path else key)
    elif isinstance(node1, list) and isinstance(node2, list):
      for i, (item1, item2) in enumerate(zip(node1, node2)):
        compare(item1, item2, f"{path}[{i}]")
    else:
      if node1 != node2:

        # ids and file are flexible components of the AST tree.
        # the id can change between generations or between builds.
        # the file will change based on the location provided to clang
        if (path != "id" and path[-3:] != ".id" and 
            path != "refId" and path[-6:] != ".refId" and 
            path != "referencedMemberDecl" and path[-21:] != ".referencedMemberDecl" and 
            path != "file" and path[-5:] != ".file"):
          
          nonlocal mismatches
          mismatches = mismatches + 1
          print(f"{path}:")
          print(f"  First node:  {node1}")
          print(f"  Second node: {node2}")
  
  compare(node1, node2)
  return mismatches
    
#####################################################################

"""
Converts both files to Python JSON objects and then compares them.
The first file is the pre-computed JSON file that is expected and 
the source file is used to compute a new JSON object for comparison.

Args:
json_file (str): the JSON file that is correctly formed
source_file (str): the source file to use for creating a JSON AST
clang_location (str): the clang binary to use for generating JSON
"""
def compare_json_trees(json_file, source_file, clang_location):
  existing_json = load_json_from_file(json_file)
  assert(existing_json != None)

  generated_json = clang_ast_dump_json(source_file, clang_location)
  assert(generated_json != None)

  result = compare_json_nodes(existing_json, generated_json)

  if (result != 0):
    print(f"ERROR: {result} mismatch(es) found")
  else:
    print("OK: 0 mismatches found")
  
#####################################################################

"""
Loads the configuration file for the scenarios and clang location.

Args:
options (dict): command-line arguments
"""
def run_tests(options):

  config = load_json_from_file(options["config"])
  
  if (config == None):
    print(f"ERROR: failed to load config file `{options['config']}`")
    return
  
  scenario_count = len(config["scenarios"])
  print(f"`{options['config']}` contains `{scenario_count}` scenario(s)")

  if ("clang" in config):
    print(f"using clang `{config['clang']}`")

    if ("scenarios" in config):
      for scenario in config['scenarios']:
        print(f"Running scenario `{scenario['name']}`")
        compare_json_trees(scenario['json'], scenario['source'], config['clang'])

    else:
      print("ERROR: scenarios missing from config file")
  else:
    print("ERROR: clang binary path missing from config file")

#####################################################################

'''
Determines what option to take given the parameters passed via the CLI
'''
def main(cmdline_args):
  # run a simple comparison between two files?
  if (cmdline_args["compare"] != None):
    first_file = load_json_from_file(cmdline_args['compare'][0])
    if (first_file == None):
      return
    
    second_file = load_json_from_file(cmdline_args['compare'][1])
    if (second_file == None):
      return
    
    errors = compare_json_nodes(first_file, second_file)
    print(f"{errors} mismatch(es) occurred")

  # test the scenarios
  else:
    if (cmdline_args["config"] == None):
      print("ERROR: config file must be specified")
      return

    run_tests(cmdline_args)
      

#####################################################################

"""
PYTEST
Loads the scenarios from a config file and then runs each scenario.

Args:
config (dict): from the JSON config file
"""
def test_scenarios(config):
  assert(config != None)
  assert("clang" in config)
  assert("scenarios" in config)

  for scenario in config['scenarios']:
    print(f"Running scenario `{scenario['name']}`")

    existing_json = load_json_from_file(scenario['json'])
    assert(existing_json != None)

    generated_json = clang_ast_dump_json(scenario['source'], config['clang'])
    assert(generated_json != None)

    result = compare_json_nodes(existing_json, generated_json)
    assert(result == 0)

#####################################################################    

if __name__ == "__main__":
  parser = argparse.ArgumentParser("description='runs existing JSON output against newly generated JSON output'")
  parser.add_argument("--compare", type=str, nargs=2, help="compares two JSON AST Trees")
  parser.add_argument("--config", type=str, help="JSON configuration file for testing scenarios")
  cmdline_args = parser.parse_args()
  main(vars(cmdline_args))
