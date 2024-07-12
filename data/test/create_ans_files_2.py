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

# DO THE FOLLOWING, PRIOR TO RUNNING THE SCRIPT, IN THE TERMINAL. Must do this first, so the .diff file can be copied from the step directory to create the .ans file
'''
export acr_show_progress=true
export pytest_keep=true
export REPAIR_MSC12=true
'''
# CAUTION: pytest_keep can result in too much disk space use (e.g., in /host/code/acr/test/step) and (lesser) in repaired files-only, in data/test/out


import json
import argparse
import re
import os
import shutil
from subprocess import run

os.environ['acr_gzip_ear_out'] = "true"
os.environ['REPAIR_MSC12'] = "true"

parser = argparse.ArgumentParser(
                    prog='create_ans_files_2',
                    description='Before running this script, set environmental variables per the comments at the top of the script. (Must do that first, so the .diff file can be copied from the step directory to create the .ans file.) This script creates .ans files if they do not already exist for adjudicated alerts with "satisfactory": "true" matching fields. STEPS include: 1. identifies alerts with "satisfactory": "true" matching fields; 2. identifies the associated test name; and also (with the -t argument) 3. checks if a .ans file currently exists and creates one if it does not (using test_runner.py); 4. runs the test which compares against the .ans file; 5. redirects output from testing to a file.  After this step, currently manually we check the output file contents, and compare that to the adjudication and current "satisfactory" entry if any, and may edit the "satisfactory" value (e.g., it may become `true` after a repair has been implemented.  In the future, would be nice to have step 6 automate creation of summary for each adjudicated alert: test name, if .ans previously existed, if .ans was created, and result of test (pass/fail).')

parser.add_argument("filename", help="provide a single filename ending alerts.json")
parser.add_argument("-t", "--test", help="run tests", action="store_true")
parser.add_argument("-v", "--verbose", help="verbose", action="store_true")

args = parser.parse_args()

alertsfilename = args.filename
print(alertsfilename)
file = open(alertsfilename) # open JSON file

ymlfilename = re.sub(r'\.alerts\.json$', '.test.yml',alertsfilename)

# return JSON object as dictionary
data = json.load(file)

# Iterate through the json list and print test names
for x in data:
    if("satisfactory" in x):
        sat_value = x["satisfactory"]
        if(sat_value == "false"):
            x_filename = x["file"]
            #testname = re.sub(r'[.]([^.]*)$', r'_\1', x_filename)
            testname = re.sub(r'[/]|(?<=\w)\.(?=[^/]*$)', r'_', x_filename)
            print("test_name: ", testname)
            dotansfilename = re.sub(r'\.alerts\.json$', "."+testname, alertsfilename)
            dotansfilename = dotansfilename+".ans"
            print(".ans filename: ", dotansfilename)
            ans_file_there = os.path.exists(dotansfilename)
            print("ans_file_there: ", ans_file_there)

            if(args.verbose):
                print("file: ",x["file"])
                print("line: ",x["line"])

            if(args.test):
                # Test and redirect output to a file. Create .ans file if none previously and there's a repair.
                my_cmd = ["python3", "/host/code/acr/test/test_runner.py","-k", testname, ymlfilename, "--create-ans"]
                testoutfilename = testname+".test.out.txt"
                testdifffilename = testname+".diff"
                with open(testoutfilename, "w") as outfile:
                    run(my_cmd, stdout=outfile)
                    if(ans_file_there == False):
                        copyfrom = os.path.join("/host/code/acr/test/step/", testdifffilename)
                        if(os.path.isfile(copyfrom)):
                            shutil.copy(copyfrom, dotansfilename)
                        else:
                            print("copyfrom doesn't exist: ", copyfrom)
                            print("so, creating empty .ans file")
                            with open(dotansfilename, 'w') as fp:
                                pass
                            fp.close()

                outfile.close()

file.close()
