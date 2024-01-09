#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
import sys
import glob
import pdb
import subprocess
import yaml
import argparse
import logging
import shutil
test_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, test_dir + "/..")
import test_known_inputs_output
import end_to_end_acr

stop = pdb.set_trace

# create an instance of the logger
logger = logging.getLogger('test_runner_logger')

logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler = logging.FileHandler('logs.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def parse_args():
    parser = argparse.ArgumentParser(description='Runs tests of code that creates repaired source code files')
    parser.add_argument("tests_file", type=str, help="The YAML file specifying a test list with inputs and answers")
    parser.add_argument("-k", type=str, dest="stringinput", help="only run tests which match the given substring expression")
    parser.add_argument("--check-ans", action="store_true", dest="check_ans")
    parser.add_argument("--create-ans", action="store_true", dest="create_ans", help="Create '.ans' file if it doesn't exist")
    argparse.cmdline_args = parser.parse_args()
    if argparse.cmdline_args.create_ans:
        argparse.cmdline_args.check_ans = True
    return argparse.cmdline_args

def read_yaml_file(filename):
    with open(filename, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data

class DummyException(Exception):
    pass

def run_test(**kwargs):
    # To print out test info as tests are being run, uncomment the following line:
    print("Running test: %r" % kwargs)
    current_dir = os.getcwd()
    no_try = (os.getenv('pytest_no_catch') == "true")
    if no_try:
        # This will catch all exceptions
        ExceptionClass = DummyException
    else:
        # This won't catch any exceptions; it's for breaking into the debugger
        # when an error occurs.
        ExceptionClass = BaseException
    try:
        end_to_end_acr.run(**kwargs)
    except ExceptionClass as exc:
        os.chdir(current_dir)
        # Exception info printed to file
        print("!!! Error: " + str(exc))
        logger.error("Exception while running test: %r" % kwargs)
        logger.exception(exc)


################################################################################
################################################################################


# If stringinput is empty string or doesn't match any test name in the .yml file, test passes.
def run(stringinput, tests_file,
        directory=".",
        step_dir="/host/code/acr/test/step",
        repair_in_place=None,
        single_file_mode=None,
        **extra_kwargs):
    tests_info = read_yaml_file(os.path.join(directory, tests_file))
    out_location = os.path.realpath("out/")
    all_passed_or_none_tested = 1
    count_results_compared = 0

    if not os.path.exists(out_location):
        os.makedirs(out_location)
    step_dir_prev_existed = os.path.isdir(step_dir)
    if(step_dir_prev_existed == False):
        print("step_dir didn't exist")
        cmd = "mkdir -p {0}".format(step_dir)
        os.system(cmd)

    all_diff_results = []

    for test in tests_info['tests']:
        if test.get('name') is None:
            test['name'] = os.path.splitext(test['input']['cfile'])[0]
        do_this = (not stringinput) or (stringinput in test['name'])
        cur_answer_file = os.path.realpath(os.path.join(directory, test['answer_file']))
        if do_this:
            count_results_compared += 1
            if ("base_dir" in test['input']):
                base_dir = os.path.realpath(test['input']['base_dir'])
                cur_c_file = os.path.realpath(os.path.join(base_dir, test['input']['cfile']))
            else:
                base_dir = None
                cur_c_file = os.path.realpath(test['input']['cfile'])

            if "hfile" in test['input'].keys():
                file_to_repair = test['input']['hfile']
                if ("base_dir" in test['input']):
                    file_to_repair = os.path.realpath(os.path.join(base_dir, file_to_repair))
                else:
                    file_to_repair = os.path.realpath(os.path.join(file_to_repair))
                single_file_mode = False
            else:
                file_to_repair = cur_c_file

            if base_dir and file_to_repair.startswith(base_dir+"/"):
                filename = file_to_repair[len(base_dir+"/"):]
            else:
                filename = os.path.basename(file_to_repair)
            file_prefix = os.path.splitext(os.path.basename(filename))[0]

            if (test['input'].get('compile_cmds_file', "autogen") != "autogen"):
                cur_compile_cmds_file = os.path.realpath(test['input']['compile_cmds_file'])
            else:
                cur_compile_cmds_file = "autogen"
            cur_alerts_file = os.path.realpath(os.path.join(directory, test['input']['alerts_file']))

            # Delete already-existing files, to avoid falsely reporting that
            # the test succeeds when it really fails.
            old_files = (
                glob.glob("%s/%s.*" % (out_location, file_prefix)) +
                glob.glob("%s/%s.*" % (step_dir, file_prefix)))
            for old_file in old_files:
                os.remove(old_file)

            # TODO: check each of files exists
            run_test(source_file=cur_c_file,
                     compile_commands=cur_compile_cmds_file,
                     alerts=cur_alerts_file,
                     out_src_dir=out_location,
                     base_dir=base_dir,
                     step_dir=step_dir,
                     repair_in_place=repair_in_place,
                     single_file_mode=single_file_mode)
            test_results_file = os.path.join(out_location, filename)
            if cur_answer_file.endswith(".json"):
                test_results_file = os.path.join(step_dir, os.path.basename(cur_answer_file))

            def print_test_cmd():
                print("        Test command: " + __file__ + " " + tests_file + " -k " + test['name'])

            # If no repair was possible, ACR produces no output file.
            print("%s:" % test['name'])
            all_diff_results = []
            if (os.path.exists(test_results_file)):
                if (os.path.exists(cur_answer_file)):
                    diff_results = subprocess.run(['diff', test_results_file, cur_answer_file], capture_output=True)
                    if diff_results.returncode != 0:
                        print("  FAIL: test result doesn't match answer key.\n")
                        all_diff_results.append([test['name'], diff_results.args, diff_results.stdout])
                        all_passed_or_none_tested = 0
                        print_test_cmd()
                    else:
                        print("  pass: test result and answer key are same")
                        cleanup(test_results_filepath=test_results_file, out_location=out_location, filename=filename, step_dir=step_dir, repair_in_place=repair_in_place, single_file_mode=single_file_mode, file_prefix=file_prefix)
                else:
                    print("  FAIL: test result exists, but answer key does not exist")
                    print("        missing answer key : " + cur_answer_file)
                    all_passed_or_none_tested = 0
                    print_test_cmd()
            else:
                if os.path.exists(cur_answer_file):
                    print("  FAIL: test result does not exist, but answer key does exist")
                    print("        missing test result file: " + test_results_file)
                    all_passed_or_none_tested = 0
                    print_test_cmd()
                else:
                    print("  pass: test result and answer key both do not exist")
                    cleanup(test_results_filepath=test_results_file, out_location=out_location, filename=filename, step_dir=step_dir, repair_in_place=repair_in_place, single_file_mode=single_file_mode, file_prefix=file_prefix)

    if all_diff_results:
        print("#"*70)
        print("Diff results:")
        print("#"*70)
        for (test_name, diff_args, diff_stdout) in all_diff_results:
            print("Test: " + test_name)
            print(diff_args)
            print(diff_stdout.decode())
            print("#"*70)

    dir_final_cleanup(step_dir, step_dir_prev_existed)
    print("count_results_compared is ", count_results_compared)
    return all_passed_or_none_tested

################################################################################
################################################################################



# If stringinput is empty string or doesn't match any test name in the .yml file, test passes.
def run_and_check_if_answer(stringinput, tests_file,
                            directory=".",
                            step_dir="/host/code/acr/test/step",
                            repair_in_place=None,
                            single_file_mode=None,
                            stop_if_no_answer_file=False,
                            **extra_kwargs):
    print("run_and_check_if_answer for tests_file: ", tests_file)

    tests_info = read_yaml_file(directory + "/" + tests_file)
    out_location = os.path.realpath("out/")
    all_passed_or_none_tested = 1
    count_results_compared = 0

    if not os.path.exists(out_location):
        os.makedirs(out_location)
    step_dir_prev_existed = os.path.isdir(step_dir)
    if(step_dir_prev_existed == False):
        cmd = "mkdir -p {0}".format(step_dir)
        os.system(cmd)

    all_diff_results = []

    for test in tests_info['tests']:
        if test.get('name') is None:
            test['name'] = os.path.splitext(test['input']['cfile'])[0]
        do_this = (not stringinput) or (stringinput in test['name'])
        cur_answer_file = os.path.realpath(os.path.join(directory, test['answer_file']))
        if(do_this and ((os.path.exists(cur_answer_file) == True) or (stop_if_no_answer_file == False))):
            count_results_compared += 1
            if ("base_dir" in test['input']):
                base_dir = os.path.realpath(test['input']['base_dir'])
                cur_c_file = os.path.realpath(os.path.join(base_dir, test['input']['cfile']))
            else:
                base_dir = None
                cur_c_file = os.path.realpath(test['input']['cfile'])

            if "hfile" in test['input'].keys():
                file_to_repair = test['input']['hfile']
                if ("base_dir" in test['input']):
                    file_to_repair = os.path.realpath(os.path.join(base_dir, file_to_repair))
                else:
                    file_to_repair = os.path.realpath(os.path.join(file_to_repair))
                single_file_mode = False
            else:
                file_to_repair = cur_c_file

            if base_dir and file_to_repair.startswith(base_dir+"/"):
                filename = file_to_repair[len(base_dir+"/"):]
            else:
                filename = os.path.basename(file_to_repair)
            file_prefix = os.path.splitext(os.path.basename(filename))[0]

            if (test['input'].get('compile_cmds_file', "autogen") != "autogen"):
                cur_compile_cmds_file = os.path.realpath(test['input']['compile_cmds_file'])
            else:
                cur_compile_cmds_file = "autogen"
            cur_alerts_file = os.path.realpath(os.path.join(directory, test['input']['alerts_file']))

            # Delete already-existing files, to avoid falsely reporting that
            # the test succeeds when it really fails.
            old_files = (
                glob.glob("%s/%s.*" % (out_location, file_prefix)) +
                glob.glob("%s/%s.*" % (step_dir, file_prefix)))
            for old_file in old_files:
                os.remove(old_file)

            # TODO: check each of files exists
            print("Test command: " + __file__ + " " + tests_file + " --check-ans -k " + test['name'])
            run_test(source_file=cur_c_file,
                     compile_commands=cur_compile_cmds_file,
                     alerts=cur_alerts_file,
                     out_src_dir=out_location,
                     base_dir=base_dir,
                     step_dir=step_dir,
                     repair_in_place=repair_in_place,
                     single_file_mode=single_file_mode)
            test_results_file = os.path.join(out_location, filename)
            if cur_answer_file.endswith(".json"):
                test_results_file = os.path.join(step_dir, os.path.basename(cur_answer_file))

            # If no repair was possible, ACR produces no output file.
            print("%s:" % test['name'])
            all_diff_results = []
            if (os.path.exists(test_results_file)):
                if ((os.path.exists(cur_answer_file) == True) or (stop_if_no_answer_file == False) or extra_kwargs.get("create_ans")):
                    # The OSS repaired files are often large, so answer files are patch files (diff -u).
                    # Therefore, the comparison is between an answer file (containing an older diff between repaired file and original file)
                    # and a diff between newly-repaired file and original file
                    # We use interdiff to ignore timestamp differences between diff files.
                    diff_from_original = subprocess.run(['diff', '-u', test_results_file, file_to_repair], capture_output=True)
                    cur_diff_file = step_dir + "/" + test["name"] + ".diff"
                    with open(cur_diff_file, mode="w") as df:
                        # Store diffs between the test_results_file and the original file
                        df.write("%s" % diff_from_original.stdout.decode())
                        # The decode() is so newlines are not converted to \n in file
                    df.close()

                    if extra_kwargs.get("create_ans") and not os.path.exists(cur_answer_file):
                        print("  Creating answer file: " + cur_answer_file)
                        shutil.copy(cur_diff_file, cur_answer_file)

                    diff_results = subprocess.run(['interdiff', cur_answer_file, cur_diff_file], capture_output=True)
                    if os.getenv('pytest_keep') != "true":
                        subprocess.run(['rm', cur_diff_file], capture_output=True)
                    if len(diff_results.stdout) != 0 or len(diff_results.stderr) != 0:
                        print("  FAIL: test result doesn't match answer key.\n")
                        all_diff_results.append([test['name'], diff_results.args, diff_results.stdout])
                        all_passed_or_none_tested = 0
                    else:
                        print("  pass: test result and answer key are same")
                        cleanup(test_results_filepath=test_results_file, out_location=out_location, filename=filename, step_dir=step_dir, repair_in_place=repair_in_place, single_file_mode=single_file_mode, file_prefix=file_prefix)
                else:
                    print("  FAIL: test result exists, but answer key does not exist AND stop_if_no_answer_file is True")
                    all_passed_or_none_tested = 0
            else:
                print("no os.path.exists(test_results_file)")
                if os.path.exists(cur_answer_file):
                    if os.path.getsize(cur_answer_file) == 0:
                        print("   pass: test result does not exist, and answer file is empty")
                    else:
                        print("  FAIL: test result does not exist, but non-null answer key does exist")
                        print("        file: " + test_results_file)
                        all_passed_or_none_tested = 0
                else:
                    print("  pass: test result and answer key both do not exist")
                    cleanup(test_results_filepath=test_results_file, out_location=out_location, filename=filename, step_dir=step_dir, repair_in_place=repair_in_place, single_file_mode=single_file_mode, file_prefix=file_prefix)
            # Below cleans up ear, brain, and hand -out.json and some .ll files
            cleanup(test_results_filepath=test_results_file, out_location=out_location, filename=filename, step_dir=step_dir, repair_in_place=repair_in_place, single_file_mode=single_file_mode, file_prefix=file_prefix)

        else:
            #print("test_runner: os.path.exists(cur_answer_file) is False and stop_if_no_answer_file is True")
            pass

    if all_diff_results:
        print("#"*70)
        print("Diff results:")
        print("#"*70)
        for (test_name, diff_args, diff_stdout) in all_diff_results:
            print("Test: " + test_name)
            print(diff_args)
            print(diff_stdout.decode())
            print("#"*70)

    dir_final_cleanup(step_dir, step_dir_prev_existed)
    print("count_results_compared is ", count_results_compared)
    return all_passed_or_none_tested


def dir_final_cleanup(step_dir, step_dir_prev_existed):
    if os.getenv('pytest_keep') == "true":
        return
    if(step_dir_prev_existed == False):
        cmd = "rm -r {0}".format(step_dir)
        os.system(cmd)

# this function can clean up after passing tests
def cleanup(filename, out_location, step_dir, test_results_filepath=None, file_prefix=None, repair_in_place=None, single_file_mode=None, base_dir=None, additional_files=None):
    if os.getenv('pytest_keep') == "true":
        return
    if(additional_files != None):
        results_filepath = os.path.realpath(os.path.join(additional_files))
        print("test_runner cleanup: results_filepath is ", results_filepath)
        cmd = "rm {0}".format(results_filepath)
        os.system(cmd)
    else:
        if(repair_in_place == True):
            test_results_filepath = filename
        if(file_prefix == None):
            file_prefix = os.path.splitext(os.path.basename(filename))[0]
        # Remove each separately so missing result files could be caught
        if(test_results_filepath == None):
            test_results_filepath = out_location + "/" + filename
        cmd = "rm {0}".format(test_results_filepath)
        os.system(cmd)
        for x in ("brain", "ear", "hand"):
            results_filepath = os.path.realpath(os.path.join(step_dir,file_prefix+"."+x+"-out.json"))
            cmd = "rm {0}".format(results_filepath)
            os.system(cmd)
        dot_h_results_filepath = out_location+"/"+"acr.h"
        cmd3 = "rm {0}".format(dot_h_results_filepath)
        os.system(cmd3)
        # delete .ll results
        ll_results_filepath = os.path.realpath(os.path.join(step_dir,file_prefix+".ll"))
        cmd4 = "rm {0}".format(ll_results_filepath)
        os.system(cmd4)


def test_two_good(stringinput, out_dir):
    assert run(stringinput, 'inputs.answers.yml') == 1
    # If assert returned 0, one or more tests ran then failed

def test_first_two_right_last_wrong(stringinput, out_dir):
    assert run(stringinput, "inputs.answers.lastfail.yml") == 0

def test_parameter_string_matches(stringinput, out_dir):
    assert run(stringinput, "in.out.substrings.match.some.names.yml") == 1

# def test_incorrect_assertion(stringinput, out_dir):
#     # With the incorrect assertion in the line below, pytest prints details of the failing last test and prints output from the first 2 passing tests.
#     assert run(stringinput, "inputs.answers.lastfail.yml") == 1

def test_errors(stringinput, out_dir):
    assert run(stringinput, "test_errors.yml") == 1

def test_array_null(stringinput, out_dir):
    assert run(stringinput, "array_null.yml") == 1


def main():
    cmdline_args = parse_args()
    if cmdline_args.check_ans:
        run_and_check_if_answer(**vars(cmdline_args))
    else:
        run(**vars(cmdline_args))


if __name__ == "__main__":
    main()
