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

# The test data was produced by the following shell script:
#   cd data/test
#   for CODE in git zeek; do
#     for TOOL in cppcheck clang-tidy rosecheckers; do
#       for RULE in EXP34-C EXP33-C MSC12-C; do
#         python3 ../../code/analysis/generate_oss_testdata.py ../$TOOL/$CODE/$TOOL.csv  $CODE  /oss/$CODE  $RULE  $TOOL  ../compile_commands.$CODE.json  > ./$CODE.$TOOL.$RULE.test.yml
#   done ; done ; done
#
# For CWEs, use this script:
#   cd data/test
#   for CODE in git zeek; do
#     for TOOL in cppcheck; do
#       for RULE in CWE-476 CWE-561; do
#         python3 ../../code/analysis/generate_oss_testdata.py ../$TOOL/$CODE/${TOOL}_cwe.tsv $CODE /oss/$CODE $RULE $TOOL ../compile_commands.$CODE.json > ./$CODE.$TOOL.$RULE.test.yml
#   done ; done ; done
#
# Finally, remove any test.yml files with empty lists.

import csv, os, re, sys, argparse, json, yaml
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser(description='Produces test data given a file of alerts')
    parser.add_argument("alerts_file", type=str, help="CSV file for alerts")
    parser.add_argument("codebase", type=str, help="Name of OSS codebase")
    parser.add_argument("base_dir", type=str, help="Directory for OSS codebase")
    parser.add_argument("rule", type=str, help="Name of CERT rule (others are ignored)")
    parser.add_argument("tool", type=str, help="Static Analysis tool (others are ignored)")
    parser.add_argument("compile_cmds_file", type=str, help="Compile Commands JSON file")
    return parser.parse_args()

def is_header_file(path):
    return os.path.splitext(path)[-1] in [".h", ".hpp", ".hh"]

def run(alerts_file, codebase, base_dir, rule, tool, compile_cmds_file):
    paths = set()
    name = ".".join([codebase, tool, rule ])
    sa_alerts_file = name + ".alerts.json"
    sa_alerts = list()
    with open(alerts_file, 'r') as in_file:
        if alerts_file.endswith(".tsv"):
            dialect = "excel-tab"
        else:
            dialect = "excel"
        csv_reader = csv.DictReader(in_file, dialect=dialect)
        for data in csv_reader:
            # if "tool" in data.keys() and data["tool"] != tool
            #     continue

            # So far, only cppcheck produces valid CWE mappings in output
            if tool == "cppcheck":
                data["rule"] = "CWE-" + data["CWE"]
            if "rule" in data.keys() and data["rule"] != rule:
                continue
            path = data["Path"]
            if path.startswith("./"):
                path = path[2:]
            paths.add(path)

            # Produce alert
            sa_alert = {"rule": rule,
                        "file": data["Path"],
                        "line": data["Line"],
                        "column": data["Column"],
                        "tool": tool,
                        "checker": data["Checker"],
                        "message": data["Message"]}

            if "End_Line" in data.keys() and data["End_Line"] != 0 and data["End_Line"] != data["Line"]:
                sa_alert["end-line"] = data["End_Line"]
            if "End_Column" in data.keys() and data["End_Column"] != 0 and data["End_Column"] != data["Column"]:
                sa_alert["end-column"] = data["End_Column"]

            sa_alerts.append(sa_alert)

    with open(sa_alerts_file, "w") as out_file:
        out_file.write(json.dumps(sa_alerts, indent=2))

    # Produce test data for this test
    header_data = yaml.safe_load(open("headers.yml"))[codebase]
    tests = list()
    for path in sorted(paths):
        name_path = re.sub(r"/", "_", re.sub(r"\.", "_", path))
        test = {"name": name_path,
                "answer_file": name + "." + name_path + ".ans",
                "input": {
                    "alerts_file": sa_alerts_file,
                    "base_dir": base_dir,
                    "compile_cmds_file": compile_cmds_file}}
        if is_header_file(path):
            test["input"]["hfile"] = path
            test["input"]["cfile"] = header_data[path]
        else:
            test["input"]["cfile"] = path
        tests.append( test)

    test_data = dict();
    test_data["tests"] = tests
    print(yaml.dump(test_data))


if __name__ == "__main__":
    run(**vars(parse_args()))
