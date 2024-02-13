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

import csv, os, re, sys, shutil
import subprocess, argparse, json, yaml
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description='Produces alerts.json + alerts.yml files given a file of alerts')
    parser.add_argument("base_dir", type=str, help="Directory of codebase")
    parser.add_argument("tool", type=str, help="Static Analysis tool")
    parser.add_argument("alerts_file", type=str, help="Alerts, produced by SA tool")
    parser.add_argument("output_file", type=str, help="Output alerts in JSON format")
    return parser.parse_args()


def is_header_file(path):
    return os.path.splitext(path)[-1] in [".h", ".hpp", ".hh"]


def run(base_dir, tool, alerts_file, output_file):
    temp_dir = "/tmp/alerts2input"
    os.mkdir(temp_dir)
    try:

        # Parse the alerts into a TSV file
        alerts1_tsv = os.path.join(temp_dir, "alerts1.tsv")
        parse_cmd = ["python3", "/host/code/analysis/sa_parsers/" + tool + "2tsv.py",
                     alerts_file, alerts1_tsv]
        subprocess.check_call(parse_cmd)

        # Remove absolute pathnames, everything should be relative to base_dir
        alerts2_tsv = os.path.join(temp_dir, "alerts2.tsv")
        sed_cmd = "< " + alerts1_tsv + " sed 's@\t./@\t@;' | sed 's@\t" + base_dir + "/@\t@;' > " + alerts2_tsv
        subprocess.check_output(sed_cmd, shell=True)

        # Associate alerts with CERT rules
        alerts3_csv = os.path.join(temp_dir, "alerts3.csv")
        sql_cmds = '''
.mode tabs
.import /tmp/alerts2input/alerts2.tsv Alerts
.mode csv
.import /host/code/analysis/checkers.csv Checkers
.headers on
.output /tmp/alerts2input/alerts3.csv
.mode csv
SELECT * FROM Alerts, Checkers WHERE Checkers.tool="''' + tool + '''" AND Checkers.checker=Alerts.checker;
'''
        cmds_sql = os.path.join(temp_dir, "cmds.sql")
        with open(cmds_sql, "w") as o:
            o.write( sql_cmds)
        subprocess.check_output("sqlite3 < " + cmds_sql, shell=True)

        # Create json test data, suitable for passing to end_to_end_acr.py
        sa_alerts = list()
        with open("/tmp/alerts2input/alerts3.csv", 'r') as in_file:
            csv_reader = csv.DictReader(in_file, dialect="excel")
            for data in csv_reader:
                if "CWE" in data.keys() and data["rule"] is None:
                    data["rule"] = data["CWE"]
                if "NONE" == data["rule"]:
                    continue

                # Produce alert
                sa_alert = {"rule": data["rule"],
                            "file": data["Path"],
                            "line": data["Line"],
                            "column": data["Column"],
                            "tool": tool,
                            "checker": data["Checker"],
                            "message": data["Message"]}
                sa_alerts.append(sa_alert)

        with open(output_file, "w") as out_file:
            out_file.write(json.dumps(sa_alerts, indent=2))
            out_file.write("\n")

    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    run(**vars(parse_args()))
