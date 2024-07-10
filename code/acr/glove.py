
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

import json
import os
import argparse
import re
import shutil
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

from util import *
from make_run_clang import read_json_file

def parse_args():
    parser = argparse.ArgumentParser(description='Creates repaired source-code files')
    parser.add_argument("edits_file", type=str, help="JSON file specifying edits to make")
    parser.add_argument('-o', type=str, metavar="OUTPUT_DIR", dest="output_dir", required=True, help="Output directory")
    parser.add_argument('--cd', type=str, dest="comp_dir", default=".", help="Current directory used for compile command")
    parser.add_argument('-b', "--base-dir", type=str, dest="base_dir",
        help="Base directory of the project")
    parser.add_argument('--repair-only', type=str, dest="repair_only",
        help="Repair the single specified source file (don't repair header files).")
    cmdline_args = parser.parse_args()
    return cmdline_args

def main():
    cmdline_args = parse_args()
    run(**vars(cmdline_args))

def run(edits_file, output_dir, *, comp_dir=".", base_dir=None, repair_only=None):
    if os.getenv('acr_emit_invocation'):
        print("glove.py -o {} --cd {}{}{} {}".format(
            output_dir, comp_dir,
            f" -b {base_dir}" if base_dir is not None else "",
            f" --repair-includes {repair_only}" if repair_only is not None else "",
            edits_file))
    outdir = Path(output_dir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    if repair_only:
        repair_only = Path(repair_only).resolve()
    if (base_dir is None):
        base_dir = comp_dir
    base_dir = Path(base_dir).resolve()

    edits_by_file = OrderedDict()
    edit_json = read_json_file(edits_file)
    if not isinstance(edit_json, list):
        edit_json = [edit_json]
    add_acr = set()
    for top_item in edit_json:
        patches = top_item.get("edits") or top_item.get("patch")
        alert_id = top_item.get("alert_id", "<unknown>")
        acr = "acr.h" in top_item.get("add-headers", [])
        for (filename, edit_list) in patches:
            edits_by_file.setdefault(filename, [])
            edits_by_file[filename].append((alert_id, sorted(edit_list)))
            if acr:
                add_acr.add(filename)

    for (filename, edit_list) in edits_by_file.items():
        ranges = sorted((edits[0][0], edits[-1][1], alert_id, edits)
                        for (alert_id, edits) in edit_list)
        accum = []
        riter = iter(ranges)
        try:
            (_, end, alert_id, edits) = next(riter)
            accum.extend(edits)
            while True:
                (nstart, nend, nalert_id, nedits) = next(riter)
                if nstart > end:
                    (end, alert_id) = (nend, nalert_id)
                    accum.extend(nedits)
                else:
                    print(f"Warning: skipping patch for alert {nalert_id} since it intersects with the patch for alert {alert_id}.")
        except StopIteration:
            pass
        edits_by_file[filename] = accum

    acr_added = False
    repaired_files = []
    for (filename, edit_list) in edits_by_file.items():
        abs_filename = base_dir.joinpath(filename).resolve()
        if repair_only and (abs_filename != repair_only):
            print("Warning: Skipping #include'd file: %s" % filename)
            continue
        try:
            outname = outdir.joinpath(abs_filename.relative_to(base_dir))
        except ValueError:
            sys.stderr.write("Warning: Skipping file outside of out_dir: %r" % abs_filename)
            continue
        assert(abs_filename.is_absolute())
        contents_string = read_whole_file(abs_filename, 'b')
        contents = list(contents_string)
        if len(edit_list) > 0 and filename in add_acr:
            include_line = '#include "acr.h"'
            already_present = re.search(b'^' + bytes(include_line, "utf-8") + b'$',
                                        contents_string, flags=re.MULTILINE)
            if not already_present:
                acr_added = True
                edit_list.append([0, 0, include_line + "\n\n"])
        for (start, end, replacement) in reversed(sorted(edit_list)):
            contents[start:end] = list(bytes(replacement, 'utf-8'))
        contents = bytes(contents)
        out_subdir = outname.parent
        out_subdir.mkdir(parents=True, exist_ok=True)
        with open(outname, 'wb') as outfile:
            outfile.write(contents)
            repaired_files.append(outname)
    print("Repaired files: %r" % repaired_files)

    if acr_added:
        # Copy the header file to the output directory
        script_dir = Path(__file__).resolve().parent
        shutil.copy(script_dir.joinpath("acr.h"), outdir)

if __name__ == "__main__":
    main()
