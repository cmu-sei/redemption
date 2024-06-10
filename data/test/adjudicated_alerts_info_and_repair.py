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

# At minimum, set environment variable `pytest_keep` to true.
# To be able to inspect results of the different steps, it's useful to have all these environmental settings.
"""
export acr_show_progress=true   # Show progress and timing
export acr_warn_unlocated_alerts=true # Warn when alerts cannot be located in AST
export pytest_keep=true         # Keep output of individual modules (ear, brain, etc.)
"""

# Some code below expects `pytest_keep` to be `true` and the default step directory location to be used. Deletion of files
# and moving files requires those.

import json
import argparse
import re
import os
#from subprocess import call run
from subprocess import run


parser = argparse.ArgumentParser(
                    prog='adjudicated_alerts_info_and_repair',
                    description='This script runs tests on adjudicated alerts from a single alerts.json file and gathers data about their repair in `*out.txt` file, `*brain-out.json`, and `*.diff` files (latter 2 put in new subdirectory under `step` directory). Prerequisites include setting environment variables per the comments at the top of the file. It assumes related alerts.json and test.yml files have the same prefix. It puts the brain output and .diff files into a subdirectory of the step directory. It 1. identifies adjudicated alerts; 2. identifies the associated test name; and also (with the -t argument) 3. checks if a .ans file currently exists and creates one if it does not (using test_runner.py); 4. runs the test which compares against the .ans file; 5. redirects output from testing to a .txt file; and 6. deletes a bunch of large files in the step directory.  After this step, manually we can inspect the output file contents, and compare those to the adjudication and current "satisfactory" entry if any, and may edit the "satisfactory" value (e.g., it may become `true` after a repair has been implemented). In the future, would be nice to combine this with step 7 automated creation of summary for each adjudicated alert: test name, if .ans previously existed, if .ans was created, and result of test (pass/fail), latter with some functionality in `test_satisfaction_status_table.py`.')
parser.add_argument("filename", help="provide filename ending alerts.json")
parser.add_argument("-t", "--test", help="run tests", action="store_true")
parser.add_argument("-v", "--verbose", help="verbose", action="store_true")

args = parser.parse_args()


# Set environment variable
os.environ['acr_gzip_ear_out'] = "true"

alertsfilename = args.filename
print(alertsfilename)
file = open(alertsfilename) # open JSON file

ymlfilename = re.sub(r'\.alerts\.json$', '.test.yml',alertsfilename)

# return JSON object as dictionary
data = json.load(file)

# Iterate through the json list and print test names
for x in data:
    if("rationale" in x):
        x_filename = x["file"]
        endc = ".c"
        result = re.search(r'endc$', x_filename)
        testname = re.sub(r'[/]|(?<=\w)\.(?=[^/]*$)', r'_', x_filename)
        
        print("test_name: ", testname)
        filename = (os.path.basename(x_filename))
        filename_no_ext = os.path.splitext(filename)[0]
        print("filename_no_ext: ", filename_no_ext)
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
            outfile.close()


            # store just the brain-out and .diff files, in new directories per testfilename
            prefix = re.sub(r'\.alerts\.json$', '',alertsfilename)
            new_dir_str="/host/code/acr/test/step/"+prefix
            new_dir=os.path.realpath(new_dir_str)
            if ( not os.path.exists(new_dir)):            
                os.mkdir(new_dir)
            mvfile1 = filename_no_ext+".brain-out.json"
            mvfile2 = testname+".diff"
            for mv_file in (mvfile1, mvfile2):
                new_file = os.path.realpath(os.path.join(new_dir, mv_file))
                mv_file = os.path.realpath(os.path.join("/host/code/acr/test/step",mv_file))
                itExists = os.path.exists(mv_file)
                if (os.path.exists(mv_file)):
                    os.replace(mv_file,new_file)
                    
            # delete (sometimes-huge) step dir files that we won't need for test stats for wiki page
            for x in (".ll", ".txt",  ".gz", ".nulldom.json", ".ear-out.json.gz"):
                rmfile = filename_no_ext+"*"+x
                # eventually want step directory files to have full testname string, to differentiate same-named files
                #     rmfile = "*"+testname+x
                path_string = os.path.realpath("/host/code/acr/test/step/"+rmfile)
                try:
                    os.remove(path_string)
                except FileNotFoundError:
                    pass



file.close()

