#!/usr/bin/env python

# Script takes a Clang 'plist' output file and extracts its alert
# information
#
# The PList file name should be this script's first argument. It should
# be produced from Clang's 'scan-build -plist' analysis tool.
#
# This script's second argument specifies the output file.
#
# TODO: Add column numbers to output
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
from zipfile import ZipFile
from plistlib import readPlistFromString


def process_plist(input_file, output):
    plist = readPlistFromString(input_file.read())
    files = plist.files
    for d in plist.diagnostics:
        # Primary alert
        output.write("\t".join([d.check_name,
                                files[d.location.file],
                                str(d.location.line),
                                d.path[-1].message]))

        # Secondary alerts
        paths = d.path
        del paths[-1]
        for p in paths:
            if hasattr(p, "message"):
                output.write("\t"+"\t".join([files[p.location.file],
                                             str(p.location.line),
                                             p.message])),

        output.write("\n")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        raise TypeError("Usage: " + sys.argv[0] + " <zip-input> <tsv-output>")
    dummy, input_filename, output_filename = sys.argv

    with open(output_filename, "w") as output_file:
        with ZipFile(input_filename, "r") as archive:
            for filename in archive.namelist():
                if filename.endswith(".plist"):
                    with archive.open(filename) as input_file:
                        process_plist(input_file, output_file)
