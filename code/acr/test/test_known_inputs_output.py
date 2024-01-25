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

import os
import re
import subprocess
import json
import argparse
import tempfile
import sys

test_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, test_dir + "/..")
import end_to_end_acr

def read_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

class Tester(object):
    def run_clang_parse(self, compile_cmd):
        cur_dir = os.getcwd()
        os.chdir(compile_cmd['directory'])
        compile_cmd['arguments'][0] = "clang"
        ast = subprocess.check_output(compile_cmd['arguments'] + ["-Xclang", "-ast-dump=json", "-fsyntax-only"])
        os.chdir(cur_dir)
        return ast

def run(source_file,  alerts, base_dir, step_dir, repair_in_place, single_file_mode, out_src_dir, compile_commands_file="autogen",):
    output_filename = source_file+".repairs.json"
    source_file = os.path.realpath(source_file)

    # TODO: Handle multiple files with same name in different directories
    #print("source_file: ", source_file, " compile_commands: ", compile_commands_file, " alerts: ", alerts, " base_dir: ", base_dir, " out_src_dir: ", out_src_dir, " step_dir ", step_dir, " repair_in_place: ", repair_in_place, " single_file_mode: ", single_file_mode)
    end_to_end_acr.run(source_file=source_file, compile_commands=compile_commands_file, alerts=alerts, base_dir=base_dir, out_src_dir=out_src_dir, step_dir=step_dir, repair_in_place=repair_in_place, single_file_mode=single_file_mode)


def parse_args():
    parser = argparse.ArgumentParser(description='Creates repaired source-code files')
    parser.add_argument("source_file", type=str, help="The source-code file to repair")
    parser.add_argument("compile_commands", type=str, help="The compile_comands.json file produced by Bear")
    parser.add_argument("alerts", type=str, help="Static-analysis alerts")
    # Automatically make output filename, AST directory, and out_src_dir
    cmdline_args = parser.parse_args()
    return cmdline_args


def main():
    cmdline_args = parse_args()
    run(**vars(cmdline_args))


if __name__ == "__main__":
    main()
