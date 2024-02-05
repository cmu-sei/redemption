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

# To be able to inspect results of the different steps, it's useful to have these environmental settings:
# export acr_show_progress=true   # Show progress and timing
# export acr_warn_unlocated_alerts=true # Warn when alerts cannot be located in AST
# export acr_show_progress=true   # Show progress and timing
# export pytest_keep=true         # Keep output of individual modules (ear, brain, etc.)


import json
import argparse
import re
#from subprocess import call run
from subprocess import run


parser = argparse.ArgumentParser(
                    prog='adjudicated_alerts_info_and_repair',
                    description='This script 1. identifies adjudicated alerts; 2. identifies the associated test name; and also (with the -t argument) 3. checks if a .ans file currently exists and creates one if it does not (using test_runner.py); 4. runs the test which compares against the .ans file; 5. redirects output from testing to a file.  After this step, currently manually we check the output file contents, and compare that to the adjudication and current "satisfactory" entry if any, and may edit the "satisfactory" value (e.g., it may become `true` after a repair has been implemented.  In the future, would be nice to have step 6 automate creation of summary for each adjudicated alert: test name, if .ans previously existed, if .ans was created, and result of test (pass/fail).')
parser.add_argument("filename", help="provide filename ending alerts.json")
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
    if("rationale" in x):
        str = x["file"]
        endc = ".c"
        result = re.search(r'endc$', str)
        changed1 = re.sub(r'\.h$', '_h',str)
        changed2 = re.sub(r'\.hh$', '_hh',changed1)
        changed3 = re.sub(r'\.c$', '_c',changed2)
        changed4 = re.sub(r'\.cc$', '_cc',changed3)        
        testname = changed4.replace("/", "_")
        print("test_name: ", testname)
        dotansfilename = re.sub(r'\.alerts\.json$', "."+testname, alertsfilename)
        print(".ans filename: ", dotansfilename+".ans")

        if(args.verbose):
            print("file: ",x["file"])
            print("line: ",x["line"])
            print("column: ",x["column"])
            if(result):
                print(result)

        if(args.test):
            # Test and redirect output to a file. Create .ans file if none previously and there's a repair.
            my_cmd = ["python3", "/host/code/acr/test/test_runner.py","-k", testname, ymlfilename, "--create-ans"]
            testoutfilename = testname+".test.out.txt"
            with open(testoutfilename, "w") as outfile:
                run(my_cmd, stdout=outfile)
                #run(my_cmd, capture_output=True, check=True)
            outfile.close()

file.close()

