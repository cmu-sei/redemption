#!/usr/bin/env python

# Script takes a clang-tidy text output file and extracts its alert
# information
#
# The first argument indicates the file containing the input.
# The data should be produced from a clang-tidy process
# A suitable command to generate the text data is:
#
# clang-tidy -checks='*' querycp.c  dos2unix.c  common.c > clang-tidy.txt
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


def canonicalize_path(dirstack, filename):
    path = filename if len(dirstack) == 0 else "/".join(dirstack) + "/" + filename
    while (True):
        newpath = re.sub(r"([^/]*)/\.\./", r"", path)
        if (len(newpath) == len(path)):
            break
        path = newpath
    while (True):
        newpath = re.sub(r"$./", r"", path)
        if (len(newpath) == len(path)):
            break
        path = newpath
    while (True):
        newpath = re.sub(r"/./", r"/", path)
        if (len(newpath) == len(path)):
            break
        path = newpath
    return path


def processFile(input_file, output_file):
    output_file.write("\t".join(["Checker","Path","Line","Column","Message"]) + "\n")

    inCtrFlag = 0
    message = ""
    links = ""
    dirstack = []

    for line in input_file:
        line = line.strip()

        parse = re.match(r"pushd *(.*)$", line)
        if (None != parse):
            dirstack.append(parse.group(1))
            continue
        if (line == "popd") and len(dirstack) > 0:
            del dirstack[len(dirstack) - 1]

         # 1-line alerts
        parse = re.match(r"^([^ :]*?\.(c|C|cpp|cxx|h|H)):([0-9]*):([0-9]*): warning: *(\S.*?) \[(.*)\]$", line)
        if (parse != None and parse.group(2) != ""):
            file_path = canonicalize_path( dirstack, parse.group(1))
            line_number = parse.group(3)
            column_number = parse.group(4)
            message = parse.group(5)
            message = message.strip().replace("\t", " ")
            checker = parse.group(6)
            column_values = "\t".join([checker, file_path, line_number, column_number, message])
            output_file.write(column_values + "\n")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        raise TypeError("Usage: " + sys.argv[0] + " <raw-input> <tsv-output>")

    input_file = open(sys.argv[1], "r")
    output_file = open(sys.argv[2], "w")

    processFile(input_file, output_file)

    input_file.close()
    output_file.close()
