#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (for testing with toy, git, zeek files) Run these commands from /host/data/test:
#   python3 test_oss.py [-k <filter>] <yml-files>
# or just
#   pytest -k <filter-which-can-filter-yml-files>

# <legal>
# 'Redemption' Automated Code Repair Tool
# 
# Copyright 2023 Carnegie Mellon University.
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
import pytest
sys.path.append('../../code/acr/test')
from test_runner import run_and_check_if_answer

def parse_args():
    parser = argparse.ArgumentParser(description='Runs all local test configurations')
    parser.add_argument('files', nargs='*',
                        help="The YML files to test")
    parser.add_argument("-k", type=str, dest="stringinput",
                        help="Only run tests (or yml files) whose name contain the given substring")
    return parser.parse_args()

test_args = {
    "yfiles": glob.glob("*.test.yml"),
    "stringinput": ""
    }

@pytest.fixture
def stringinput():
    return test_args["stringinput"]

@pytest.mark.parametrize("yfile", test_args["yfiles"])
def test_oss(yfile):
    run_oss("", yfile)

def run_oss(stringinput, yfile):
    assert(run_and_check_if_answer(stringinput, yfile, stop_if_no_answer_file=True) == 1)
    print("test_oss: passed " + yfile)

def run_all(stringinput, files):
    for yfile in files:
        run_oss(stringinput, yfile)

if __name__ == "__main__":
    test_args = parse_args()
    run_all(**vars(test_args))
