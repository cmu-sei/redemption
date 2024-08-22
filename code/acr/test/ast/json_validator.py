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

# example
# ./json_validator.sh .

import os
import json
import sys

def check_json_files(directory):
  # Check if the provided directory exists
  if not os.path.isdir(directory):
    print(f"The directory '{directory}' does not exist.")
    return
  
  # List all files in the directory
  files = os.listdir(directory)
  json_files = [file for file in files if file.endswith('.json')]
  
  # Check each JSON file for validity
  for json_file in json_files:
    file_path = os.path.join(directory, json_file)
    try:
      with open(file_path, 'r') as file:
        json.load(file)
      print(f"Valid JSON: {json_file}")
    except json.JSONDecodeError as e:
      print(f"Invalid JSON: {json_file} - Error: {e}")
    except Exception as e:
      print(f"An error occurred with file {json_file} - Error: {e}")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python check_json_files.py <directory>")
  else:
    directory = sys.argv[1]
    check_json_files(directory)


