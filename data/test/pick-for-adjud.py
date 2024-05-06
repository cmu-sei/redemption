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

import sys, glob, argparse
import random

sys.path.append('../../code/acr')
from util import *
from make_run_clang import read_json_file


def parse_args():
    parser = argparse.ArgumentParser(description='Randomly selects alerts and adds adjudication fields')
    parser.add_argument("input_alerts_file", type=str, help="Input alerts.json file")
    parser.add_argument("-o", dest="output_file", type=str, required=True, help="Output file")
    parser.add_argument("-n", type=int, required=True, help="Number of alerts to select")
    return parser.parse_args()

def main():
    args = parse_args()
    alerts = read_json_file(args.input_alerts_file)

    assert(isinstance(alerts, list))
    num_added = 0
    for i in range(0,10): # give up after 10 attempts
        selected_alerts = random.sample(alerts, k=args.n)
        for alert in selected_alerts:
            if num_added == args.n:
                break
            skip = False
            for key in ["verdict", "randomness", "rationale", "repairable", "satisfactory"]:
                if alert.get(key):
                    skip = True
            if skip:
                continue
            if int(alert["line"]) == 0:
                continue
            alert["randomness"] = "random"
            alert["verdict"] = ""
            alert["rationale"] = ""
            alert["repairable"] = ""
            alert["satisfactory"] = ""
            num_added += 1

    with open(args.output_file, 'w') as outfile:
        outfile.write(json.dumps(alerts, indent=2) + "\n")

if __name__ == "__main__":
    main()
