#!/usr/bin/env python

# Python script that scrubs cppcheck alerts.
#
# The first argument indicates the file containing the input.
# The second argument specifies the output file.
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
import xml.etree.ElementTree as ET


def process_v18(root, output_file):
    output_file.write("\t".join(["Checker","Path","Line","Column","Message","CWE",
                                 "Tool","End_Line","End_Column"]) + "\n")
    for errors in root.iter("errors"):
        for node in errors.iter("error"):
            checker = node.get("id")
            cwe = node.get("cwe")
            if cwe is None:
                cwe = "NONE"

            message = node.get("msg")
            message = message.strip().replace('\t', " ")

            location = node.find("location")
            if location is None:
                continue
            file_path = location.get("file")
            line_number = location.get("line")
            column_number = location.get("column")

            column_values = "\t".join([checker, file_path, line_number, column_number, message, cwe, "cppcheck_oss", "0", "0"])
            output_file.write(column_values + "\n")


def process_v16(root, output_file):
    # SCALe-style input consists of alerts, one per line, each of the form:
    # <checker>        <file_path>        <line_number>        <column-number>        <message>[        <file_path>        <line_number>        <column-number>        <message>]*
    # Since cppcheck alerts map to a single source file line, we just have 5 elements per line (i.e., no secondary messages).
    # checker_id        source_file_path        line_number        column_number       alert message

    output_file.write("\t".join(["Checker","Path","Line","Column","Message",
                                 "Tool","End_Line","End_Column"]) + "\n")
    for node in root.iter("error"):
        checker = node.get("id")
        file_path = node.get("file")
        line_number = node.get("line")
        column_number = node.get("column")
        message = node.get("msg")
        message = message.strip().replace("\t", " ")

        if file_path is None or "" == file_path.strip():
            continue

        column_values = "\t".join([checker, file_path, line_number, column_number, message, cwe, "cppcheck_oss", "0", "0"])
        output_file.write(column_values + "\n")


def processFile(input_file, output_file):

    try:
        tree = ET.parse(input_file)
    except:
        raise Exception("An error occured while parsing the input file. Ensure it's a cppcheck xml file.\n")

    root = tree.getroot()

    version = None

    for node in root.iter("cppcheck"):
        version = node.get("version")

    if "1.80" <= version:
        process_v18(root, output_file)
    else:
        process_v16(root, output_file)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        raise TypeError("Usage: " + sys.argv[0] + " <cppcheck-xml-file> <tsv-output>")

    input_file = sys.argv[1]
    output_file = open(sys.argv[2], "w")

    processFile(input_file, output_file)

    output_file.close()
