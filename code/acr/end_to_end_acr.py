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
import re
import subprocess
import json
import argparse
import tempfile
import ear
import brain
import hand
from collections import OrderedDict, defaultdict
from util import *

def parse_args():
    def text_to_bool(s):
        if s is None:
            return None
        elif s.lower() == "true":
            return True
        elif s.lower() == "false":
            return False
        else:
            raise ValueError("Expecting 'true' or 'false'")
    parser = argparse.ArgumentParser(description='Creates repaired source-code files')
    parser.add_argument("source_file", type=str, help="The source-code file to repair")
    parser.add_argument("compile_commands", type=str, help="The compile_comands.json file produced by Bear")
    parser.add_argument("alerts", type=str, help="Static-analysis alerts")
    parser.add_argument('-o', type=str, metavar="OUTPUT_FILE", dest="hand_out_file", help=argparse.SUPPRESS) # deprecated
    parser.add_argument('--ast-dir', type=str, metavar="AST_DIR", dest="ast_dir", help=argparse.SUPPRESS)    # deprecated
    parser.add_argument('--repaired-src', type=str, dest="out_src_dir", help="Directory to write repaired source files")
    parser.add_argument('--step-dir', type=str, dest="step_dir", help="Directory to write intermediate files of the steps of the process")
    parser.add_argument('-b', "--base-dir", type=str, dest="base_dir",
        help="Base directory of the project")
    parser.add_argument('--in-place', action="store_true", dest="repair_in_place",
        help="Sets repaired-src directory to base-dir")
    parser.add_argument('--single-file', type=text_to_bool, dest="single_file_mode", metavar="{true,false}",
        help="Whether to repair only the single specified source file (as opposed to also repairing #include'd header files).  Choices: [true, false].")
    parser.add_argument('--skip-dom', type=text_to_bool,  metavar="{true,false}",
        help="Skip dominator analysis")
    cmdline_args = parser.parse_args()
    return cmdline_args

def main():
    cmdline_args = parse_args()
    run(**vars(cmdline_args))


def run(source_file, compile_commands, alerts, *, hand_out_file=None, ast_dir=None, out_src_dir=None, step_dir=None, base_dir=None, single_file_mode=None, repair_in_place=False, skip_dom=None):
    if os.getenv('acr_emit_invocation'):
        print("end_to_end_acr.py{}{}{}{}{}{}{}{} {} {} {}".format(
            f" -o {hand_out_file}" if hand_out_file else "",
            f" --ast-dir {ast_dir}" if ast_dir else "",
            f" --repaired-src {out_src_dir}" if out_src_dir else "",
            f" --step-dir {step_dir}" if step_dir else "",
            f" --base-dir {base_dir}" if base_dir else "",
            " --in-place" if repair_in_place else "",
            " --single-file" if single_file_mode else "",
            " --skip-dom true" if skip_dom else "",
            source_file, compile_commands, alerts))

    if repair_in_place == True:
        if (base_dir is None):
            raise Exception("Option '--in_place' requires that base_dir be set.")
        if not (out_src_dir is None):
            raise Exception("Cannot specify both '--in-place' and --repaired-src'.")
        out_src_dir = base_dir
        if single_file_mode is None:
            single_file_mode = False
    else:
        if single_file_mode is None:
            single_file_mode = True

    if (base_dir is None):
        base_dir = os.path.dirname(source_file)

    source_base_name = os.path.basename(source_file)
    source_base_name = strip_filename_extension(source_base_name)

    if step_dir:
        ast_dir = step_dir
        brain_out_file = step_dir + "/" + source_base_name + ".brain-out.json"
        hand_out_file = step_dir + "/" + source_base_name + ".hand-out.json"
        ast_file_suffix = ".ear-out.json"
    else:
        brain_out_file = hand_out_file
        ast_file_suffix = ".ast.json"

    temp_ast_dir = None
    if not ast_dir:
        temp_ast_dir = tempfile.TemporaryDirectory()
        ast_dir = temp_ast_dir.name
    ast_filename = ast_dir + "/" + source_base_name + ast_file_suffix

    print_progress("Running ear module...")
    ear.run_ear_for_source_file(source_file, compile_commands, ast_filename, base_dir=base_dir)
    print_progress("Running brain module...")
    brain.run(ast_file=ast_filename, alerts_filename=alerts, output_filename=brain_out_file, skip_dom=skip_dom)
    print_progress("Running hand module...")
    hand.run(ast_file=ast_filename, alerts_filename=brain_out_file, output_filename=hand_out_file)
    compile_dir = read_json_file(ast_filename)["compile_dir"]
    if out_src_dir:
        import glove
        kwargs = {}
        if single_file_mode:
            kwargs = {"single_file": source_file}
        print_progress("Running glove module...")
        glove.run(edits_file=hand_out_file, output_dir=out_src_dir, comp_dir=compile_dir, base_dir=base_dir, **kwargs)

    print_progress("Finished!")

    if temp_ast_dir:
        temp_ast_dir.cleanup()


if __name__ == "__main__":
    main()
