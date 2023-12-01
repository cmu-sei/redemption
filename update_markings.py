#!/usr/bin/env python3

# This script updates legal markings in every file in the manifest
# that contains legal tags, just like this file, that are , based on
# the contents of the ABOUT file.  It has not been tested with
# symbolic links, device files, pipes, sockets, or other non-regular
# files It ignores files that are not in the manifest.
#
# This script includes some pytests to verify that all files that need
# legal tags have them, that every file is in either the manifest or
# the denylist, and that every file in the manifest or denylist
# actually exists.
#
# How to use:
# 1. Make sure update_markings.py is up-to-date, and fix other bugs
# 2. Run update_markings.py -w , update any file missing legal tags that should have them.
# 3. Run update_markings.py, verify that any one looks correct.

# <legal>
# 'Redemption' Automated Code Repair Tool
# 
# Copyright 2023 Carnegie Mellon University.
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

import json
import io
import os
import pytest
import re
import sys
import yaml

VERSION_MAGIC_STR = '{{BASP_VERSION}}'
VERSION_FIX_FILES = ['License.txt']


def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Script to update markings info")
    p.add_argument('-w', '--warnings', action='store_true',
                   help="Print warnings, but don't update legal info in source files")
    cui_group = p.add_mutually_exclusive_group()
    cui_group.add_argument('--cui', action='store_true', help="Adds CUI footer")
    cui_group.add_argument('--no-cui', action='store_true', help="Don't add CUI footer")
    args = p.parse_args()

    if (not args.cui) and (not args.no_cui) and (not args.warnings):
        p.print_usage()
        print("Error: exactly one of {'--cui', '--no-cui'} must be specified.")
        exit()

    return args


def update_markings(markings_data, config_data, warnings=True, cui=False):
    '''
        Updating markings info in each file that contains it
    '''
    missing_legal_tags = 0

    for dirpath, _, files in os.walk('.'):
        for filename in files:
            full_path = os.path.join(dirpath, filename)

            if full_path.startswith("./"):
                full_path = full_path[2:]
            full_path = full_path.rstrip()
            ext = os.path.splitext(full_path)[-1][1:]
            regex = None
            if ext in config_data["Exempt_Extensions"]:
                regex = None
            elif any([re.match(x, full_path) for x in config_data["Exempt_Files"]]):
                regex = None
            elif full_path.startswith("./bin"):
                regex = config_data["Extension_Map"]["sh"]
            elif full_path in config_data["File_Map"]:
                regex = config_data["File_Map"][full_path]
            elif ext in config_data["Extension_Map"]:
                regex = config_data["Extension_Map"][ext]
            else:
                if warnings:
                    print("WARNING: Not checking markings in " + full_path)

            if not regex:
                continue

            with io.open(full_path, 'r+', encoding="utf-8") as fp:

                try:
                    contents = fp.read()
                    # This matches all lines where the <legal> tags
                    # live. So anything on these lines outside the <legal>
                    # tags will get erased. IOW this presumes that the
                    # lines with <legal> tags have nothing else of
                    # importance.
                    match = re.search(r'(?im)^.*?<legal>(.|\n)*?</legal>.*?$',
                                      contents)
                    if not match:
                        missing_legal_tags = missing_legal_tags + 1
                        if warnings:
                            print("WARNING: No markings for " + full_path)
                        continue
                    if not warnings:
                        new_contents = contents
                        cui_line = ""
                        if cui:
                            # Assumption: If the CUI footer is already present, then so is the CUI header.
                            if not re.search("(\n|\r)[^A-Za-z0-9]*CUI[^A-Za-z0-9]*(\n|\r)*$", new_contents):
                                cui_line = "CUI\n\n"
                                if not new_contents.endswith("\n"):
                                    new_contents += "\n"
                                new_contents += "\n" + re.sub(r'(?m)(^.*$)', regex, "CUI") + "\n"
                        new_legal = cui_line + "<legal>\n" + "\n".join(markings_data['legal']) + "\n</legal>"
                        prot_new_legal = re.sub(r'(?m)(^.*$)', regex, new_legal)
                        new_contents = (new_contents[:match.start(0)] +
                                        prot_new_legal +
                                        new_contents[match.end(0):])
                        fp.seek(0)
                        fp.write(new_contents)
                        fp.truncate()
                except UnicodeDecodeError:
                    print("WARNING: Non-UTF8 file: " + full_path)

    return missing_legal_tags


def adjust_version_numbers(markings_data):
    '''
        Replacing version numbers with the version from the ABOUT file.
    '''
    for filename in VERSION_FIX_FILES:
        with io.open(filename, 'r', encoding="utf-8") as input_f:
            new_str = input_f.read().replace(VERSION_MAGIC_STR, markings_data['version'])
        with io.open(filename, 'w', encoding="utf-8") as output_f:
            output_f.write(new_str)


def main(args):
    with open("ABOUT") as f:
        markings_data = json.load(f)
    with open("update_markings.yml") as f:
        config_data = yaml.safe_load(f)

    # Setup the local directory for packaging
    update_markings(markings_data, config_data, args.warnings, args.cui)
    adjust_version_numbers(markings_data)


# pytest methods

def test_about_ascii():
    with open("ABOUT", "r", encoding="ASCII") as s:
        data = s.read()

def test_license_ascii():
    with open("License.txt", "r", encoding="ASCII") as s:
        data = s.read()

def test_all_files_have_legal_tags():
    with open("ABOUT") as f:
        markings_data = json.load(f)
    with open("update_markings.yml") as f:
        config_data = yaml.safe_load(f)
    assert 0 == update_markings(markings_data, config_data)

def ignore_file(filename):
    return "/__pycache__/" in filename or \
       "/.pytest_cache/"  in filename or \
       "/.git/" in filename

if __name__ == '__main__':
    main(parse_args())
