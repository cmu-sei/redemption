#!/usr/bin/env python

# Script takes a codecheckers text output file and extracts its alert
# information
#
# The first argument indicates the file containing the input.
# The data should be produced from a codecheckers process
# A suitable command to generate the Codechecker JSON data is:
#
# CodeChecker parse -e json reports.codechecker > codechecker.json
#
# The second argument specifies the output file.
#
# This script currently produces only one message per alert
#
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

import sys
import re
import json


Tool_Map = {
    "clang-tidy": "clang_tidy_oss",
    "cppcheck": "cppcheck_oss",
    "gcc": "gcc_oss",
    "clangsa": "clang_sa_oss",
}


def processFile(input_file, output_file):
    output_file.write("\t".join(["Checker","Path","Line","Column","Message",
                                 "Tool","End_Line","End_Column"]) + "\n")
    data = json.load( input_file)

    for d in data["reports"]:
        line_end = column_end = 0
        if "notes" in d and len(d["notes"]) > 0:
            line_end = d["notes"][0]["range"]["end_line"]
            column_end = d["notes"][0]["range"]["end_col"]
        elif "bug_path_events" in d and len(d["bug_path_events"]) > 0:
            line_end = d["bug_path_events"][0]["range"]["end_line"]
            column_end = d["bug_path_events"][0]["range"]["end_col"]

        tool = Tool_Map[d["analyzer_name"]]
        checker = d["checker_name"]
        if checker.startswith(d["analyzer_name"]):
            checker = checker[len(d["analyzer_name"])+1:]
        column_values = "\t".join([
            checker, d["file"]["path"], str(d["line"]), str(d["column"]),
            d["message"], tool, str(line_end), str(column_end)])
        output_file.write(column_values + "\n")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        raise TypeError("Usage: " + sys.argv[0] + " <raw-input> <tsv-output>")

    input_file = open(sys.argv[1], "r")
    output_file = open(sys.argv[2], "w")

    processFile(input_file, output_file)

    input_file.close()
    output_file.close()
