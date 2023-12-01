
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
import os
import argparse
import re
import shutil
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

from util import *

def parse_args():
    parser = argparse.ArgumentParser(description='Creates repaired source-code files')
    parser.add_argument("edits_file", type=str, help="JSON file specifying edits to make")
    parser.add_argument('-o', type=str, metavar="OUTPUT_DIR", dest="output_dir", required=True, help="Output directory")
    parser.add_argument('--cd', type=str, dest="comp_dir", default=".", help="Current directory used for compile command")
    parser.add_argument('-b', "--base-dir", type=str, dest="base_dir",
        help="Base directory of the project")
    parser.add_argument('--single-file', type=str, dest="single_file",
        help="Repair the single specified source file (don't repair header files).")
    cmdline_args = parser.parse_args()
    return cmdline_args

def main():
    cmdline_args = parse_args()
    run(**vars(cmdline_args))

def run(edits_file, output_dir, *, comp_dir=".", base_dir=None, single_file=None):
    outdir = output_dir
    outdir = os.path.realpath(outdir)
    if single_file:
        single_file = os.path.realpath(single_file)
    if (base_dir is None):
        base_dir = comp_dir
    base_dir = os.path.realpath(base_dir)

    edits_by_file = OrderedDict()
    edit_json = read_json_file(edits_file)
    if not isinstance(edit_json, list):
        edit_json = [edit_json]
    for top_item in edit_json:
        for (filename, edit_list) in (top_item.get("edits") or top_item.get("repair")):
            edits_by_file.setdefault(filename, [])
            edits_by_file[filename].extend(edit_list)
    def remove_base_dir(s):
        if s.startswith(base_dir + "/"):
            return s[len(base_dir + "/"):]
        else:
            return s
    repaired_files = []
    for (filename, edit_list) in edits_by_file.items():
        abs_filename = os.path.realpath(os.path.join(base_dir, filename))
        if single_file and (abs_filename != os.path.realpath(single_file)):
            print("Warning: Skipping #include'd file: %s" % filename)
            continue
        outname = os.path.realpath(outdir + "/" + remove_base_dir(abs_filename))
        if not outname.startswith(outdir + "/"):
            sys.stderr.write("Warning: Skipping file outside of out_dir: %r" % outname)
            continue
        assert(abs_filename.startswith("/"))
        contents_string = read_whole_file(abs_filename)
        contents = list(contents_string)
        if len(edit_list) > 0:
            include_line = '#include "acr.h"'
            already_present = re.search('^' + include_line + '$', contents_string, flags=re.MULTILINE)
            if not already_present:
                edit_list.append([0, 0, include_line + "\n\n"])
        for (start, end, replacement) in reversed(sorted(edit_list)):
            contents[start:end] = list(replacement)
        contents = "".join(contents)
        out_subdir = os.path.dirname(outname)
        Path(out_subdir).mkdir(parents=True, exist_ok=True)
        with open(outname, 'w') as outfile:
            outfile.write(contents)
            repaired_files.append(outname)
    print("Repaired files: %r" % repaired_files)

    # Copy the header file to the output directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    shutil.copy(script_dir + "/acr.h", outdir)

if __name__ == "__main__":
    main()
