#!/usr/bin/env python

# Script takes a CodeDX xml output file and extracts its alert
# information
#
# The CodeCX XML file name should be this script's first argument.
#
# This script's second argument specifies the output file.
#
# Output is of form:
#     "\t".join(["tool", "checker", "path", "line", "message"]);
#
# TODO Add column
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
import xmltodict
import json


def process_file(input_file, output_file):
    data_dict = xmltodict.parse(input_file.read())
    json_data = json.dumps(data_dict)
    j = json.loads(json_data)

    for f in j["report"]["findings"]["finding"]:
        rs = f["results"]["result"]
        if not type(rs) is list:
            rs = [rs]
        for r in rs:
            text = r["description"]["#text"]
            text = re.sub(r'\s', ' ', text);
            output_file.write("\t".join([r["tool"]["@name"],
                                         r["tool"]["@code"],
                                         r["location"]["@path"],
                                         r["location"]["line"]["@start"],
                                         text])
                              + "\n")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        raise TypeError("Usage: " + sys.argv[0] + " <xml-input> <tsv-output>")
    dummy, input_filename, output_filename = sys.argv

    with open(output_filename, "w") as output_file:
        with open(input_filename, "r") as input_file:
            process_file(input_file, output_file)
