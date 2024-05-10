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

import sys, glob, argparse, os
import random
import json

sys.path.append('../../code/acr')
from make_run_clang import read_json_file


def parse_args():
    parser = argparse.ArgumentParser(description='Adds info')
    parser.add_argument("input_alerts_file", type=str, help="Input alerts.json file")
    parser.add_argument("-o", dest="output_file", type=str, required=True, help="Output file")
    parser.add_argument("-b", "--base-dir", type=str, help="base dir")
    return parser.parse_args()

def get_all_lines_of_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines

def main():
    args = parse_args()
    alerts = read_json_file(args.input_alerts_file)

    for alert in alerts:
        filename = alert["file"]
        line_num = int(alert["line"])
        if args.base_dir:
            filename = os.path.join(args.base_dir, filename)
        if not os.path.exists(filename):
            print("File {filename:r} does not exist!")
            sys.exit(1)
        if line_num != 0:
            try:
                alert["line_text"] = get_all_lines_of_file(filename)[line_num - 1]
            except:
                pass

    with open(args.output_file, 'w') as outfile:
        outfile.write(json.dumps(alerts, indent=2) + "\n")

if __name__ == "__main__":
    main()
