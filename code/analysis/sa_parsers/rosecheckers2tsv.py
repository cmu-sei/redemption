#!/usr/bin/env python

# Script takes a Rosecheckers output file and extracts its alert
# information
#
# The first argument indicates the file containing the input.
# The second argument specifies the output file.
#
# The script should take the text data via standard input. The data
# should be produced from a build process using make and g++.  A
# suitable command to generate the text data is:
#
# make 2>&! > makelog
#
# This script produces only one message per alert
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
import os


def processFile(input_file, output_file):
    output_file.write("\t".join(["Checker","Path","Line","Column","Message",
                                 "Tool","End_Line","End_Column"]) + "\n")

    directory = ""
    file_path = None

    for line in input_file:
        line = line.strip()

        parse = re.match(r"^In directory: *(.*)$", line)
        if (parse != None):
            directory = parse.group(1)
            continue

        parse = re.match(r"^Compiler args are: .* (.*?)$", line)
        if (parse != None):
            file_path = parse.group(1)
            suffix = os.path.splitext(file_path)[1]
            if suffix not in [".c", ".h", ".cc", ".cxx", ".cpp", ".hpp"]:
                file_path = None
            else:
                if not os.path.isabs(file_path):
                    file_path = directory + "/" + file_path

        parse = re.match(r"^(.*?):([0-9]*):([0-9]*): (warning|error): ([-A-Za-z0-9]*): (.*?) *$", line)

        if (parse == None):
            continue
        file_name = parse.group(1)
        line_number = parse.group(2)
        column_number = parse.group(3)
        checker = parse.group(5)
        message = parse.group(6)
        message = message.strip().replace("\t", " ")

        if file_path is None:
            file_path = directory + "/" + file_name
            file_path = file_path.strip()

        column_values = "\t".join([checker, file_path, line_number, column_number, message
                                       "rosecheckers", "0", "0"])
        output_file.write(column_values + "\n")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        raise TypeError("Usage: " + sys.argv[0] + " <raw-input> <tsv-output>")
    input_file = open(sys.argv[1], "r")
    output_file = open(sys.argv[2], "w")

    processFile(input_file, output_file)

    input_file.close()
    output_file.close()
