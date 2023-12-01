#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (For testing with git and/or zeek files) Run these commands from /host/data/test:
# python3 -c 'import create_answer_file; create_answer_file.create_answer_file_if_none()'
# (for testing with the toy data) Run these commands in the directory /host/data/test:
# python3 -c 'import create_answer_file; import os; os.chdir("toy"); create_answer_file.create_answer_file_if_none()'

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

import os
import sys, glob, subprocess
sys.path.append('../../code/acr/test')
from test_runner import run_test, cleanup, dir_final_cleanup, read_yaml_file


def run_create_answer_if_not_there(stringinput, tests_file, directory=".", step_dir="/host/code/acr/test/step", repair_in_place=None, single_file_mode=None):
    print("tests_file: ", tests_file)
    tests_info = read_yaml_file(directory + "/" + tests_file)
    out_location = os.path.realpath("out/")
    acr_or_failed_test = 1

    if not os.path.exists(out_location):
        os.makedirs(out_location)
    step_dir_prev_existed = os.path.isdir(step_dir)
    if(step_dir_prev_existed == False):
        cmd = "mkdir -p {0}".format(step_dir)
        os.system(cmd)

    for test in tests_info['tests']:
        if test.get('name') is None:
            test['name'] = os.path.splitext(test['input']['cfile'])[0]
        print("create_answer_file: test['name']: ", test['name'])

        do_this = (not stringinput) or (stringinput in test['name'])
        cur_answer_file = os.path.realpath(os.path.join(directory, test['answer_file']))
        if(do_this and (os.path.exists(cur_answer_file) == False)):
            if ("base_dir" in test['input']):
                base_dir = os.path.realpath(test['input']['base_dir'])
                cur_c_file = os.path.realpath(os.path.join(base_dir, test['input']['cfile']))
            else:
                base_dir = None
                cur_c_file = os.path.realpath(test['input']['cfile'])

            if (test['input'].get('compile_cmds_file', "autogen") != "autogen"):
                cur_compile_cmds_file = os.path.realpath(test['input']['compile_cmds_file'])
            else:
                cur_compile_cmds_file = "autogen"
            cur_alerts_file = os.path.realpath(os.path.join(directory, test['input']['alerts_file']))

            filename = os.path.basename(cur_c_file)
            file_prefix = os.path.splitext(filename)[0]

            # Delete already-existing files, to avoid falsely reporting that
            # the test succeeds when it really fails.
            old_files = (
                glob.glob("%s/%s.*" % (out_location, file_prefix)) +
                glob.glob("%s/%s.*" % (step_dir, file_prefix)))
            for old_file in old_files:
                os.remove(old_file)

            run_test(source_file=cur_c_file, compile_commands=cur_compile_cmds_file, alerts=cur_alerts_file, out_src_dir=out_location, base_dir=base_dir, step_dir=step_dir, repair_in_place=repair_in_place, single_file_mode=single_file_mode)

            test_results_file = os.path.join(out_location, filename)

            if cur_answer_file.endswith(".json"):
                test_results_file = os.path.join(step_dir, os.path.basename(cur_answer_file))

            # If no repair was possible, ACR produces no output file.
            print("%s:" % test['name'])
            with open(cur_answer_file, mode="w") as caf:
                if (os.path.exists(test_results_file)):
                    # Do a diff -r between the test_results_file and the ORIGINAL file
                    if (os.path.exists(cur_c_file)):
                        diff_results = subprocess.run(['diff', '-u', test_results_file, cur_c_file], capture_output=True)
                        # Write the diff_results to the answer_file
                        caf.write("%s" % diff_results.stdout)
                        if diff_results.returncode != 0:
                            print("  DIFFERENT but fine: acr ran, did code repair. Test result doesn't match initial file.\n")
                        else:
                            print("  SAME but fine: acr ran, but no code repair. Test result and initial file are same")
                            # Do limited cleanup, but leave answer file
                            cleanup(test_results_filepath=test_results_file, out_location=out_location, filename=filename, step_dir=step_dir, repair_in_place=repair_in_place, single_file_mode=single_file_mode, file_prefix=file_prefix)
                    else:
                        print("  FAIL: test result exists, but cur_c_file does not exist")
                        acr_or_failed_test = 2 # failed test
                else:
                    # glove.py does not write a test results file if there are no repairs indicated
                    if os.path.exists(cur_answer_file):
                        print("  DIFFERENT but ok: test result does not exist (normal if no repairs supposed to be made), but cur_answer_file does exist")
                    else:
                        print("  Same: test result and cur_answer_file both do not exist")
                        # Do limited cleanup, but leave answer file
                        cleanup(test_results_filepath=test_results_file, out_location=out_location, filename=filename, step_dir=step_dir, repair_in_place=repair_in_place, single_file_mode=single_file_mode, file_prefix=file_prefix)
                caf.close()

    dir_final_cleanup(step_dir, step_dir_prev_existed)
    return acr_or_failed_test

def create_answer_file_if_none():
    for f in glob.glob("*.test.yml"):
        assert(run_create_answer_if_not_there(None, f) == 1)
        print("create_answer_file: after assert")

create_answer_file_if_none()
