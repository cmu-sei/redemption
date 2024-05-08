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
import os
import json
import argparse

def create_file_list(directory, extensions):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(tuple(extensions)):
                file_list.append({'name': os.path.splitext(file)[0], 'json': os.path.splitext(file)[0] + ".json", 'source': file})
    return file_list

def save_to_json(file_list, output_file, clang_path=None):
    json_data = {"scenarios": file_list}
    if clang_path:
        json_data["clang"] = clang_path
    else:
        json_data["clang"] = "/opt/clang/build/bin/clang" # Default clang path
    with open(output_file, 'w') as json_file:
        json.dump(json_data, json_file, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Create a JSON file of files in a directory that match certain file extensions.')
    parser.add_argument('directory', type=str, help='The directory path')
    parser.add_argument('extensions', type=str, help='The file extensions separated by comma (e.g., txt, pdf)')
    parser.add_argument('output_file', type=str, help='The output JSON file path')
    parser.add_argument('--clang', type=str, help='Path to clang (optional)')
    args = parser.parse_args()

    extensions = args.extensions.split(',')
    file_list = create_file_list(args.directory, extensions)
    
    if file_list:
        save_to_json(file_list, args.output_file, args.clang)
        print(f"JSON file '{args.output_file}' created successfully.")
    else:
        print("No files found with the specified extensions.")

if __name__ == "__main__":
    main()
