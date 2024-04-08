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

import os, sys
import re
import subprocess
import json
import argparse
import tempfile
import ear
import brain
from tempfile import TemporaryDirectory
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
    parser = argparse.ArgumentParser(description="Creates repaired source-code files",
                                     epilog="See the Redemption README.md file For more info.")
    parser.add_argument("source_file", type=str, help="The source-code file to repair")
    parser.add_argument("compile_commands", type=str, help="The compile_commands.json file (produced by Bear) or \"autogen\"")
    parser.add_argument("alerts", type=str, help="Static-analysis alerts")
    parser.add_argument('--repaired-src', type=str, dest="out_src_dir", help="Directory to write repaired source files")
    parser.add_argument('--step-dir', type=str, dest="step_dir", default=None, help="Directory to write intermediate files of the steps of the process. (default: temporary directory)")
    parser.add_argument('-b', "--base-dir", type=str, dest="base_dir",
        help="Base directory of the project")
    parser.add_argument('--in-place', action="store_true", dest="repair_in_place",
        help="Sets repaired-src directory to base-dir")
    parser.add_argument('--repair-includes', type=text_to_bool, dest="repair_includes_mode", metavar="{true,false}",
        help="Whether to repair #include'd header files or only the single specified source file.  Choices: [true, false].")
    cmdline_args = parser.parse_args()
    return cmdline_args

def main():
    cmdline_args = parse_args()
    run(**vars(cmdline_args))


def run(source_file, compile_commands, alerts, *, out_src_dir=None, step_dir=None, base_dir=None, repair_includes_mode=None, repair_in_place=False):
    if os.getenv('acr_emit_invocation'):
        print("end_to_end_acr.py{}{}{}{}{} {} {} {}".format(
            f" --repaired-src {out_src_dir}" if out_src_dir else "",
            f" --step-dir {step_dir}" if step_dir else "",
            f" --base-dir {base_dir}" if base_dir else "",
            " --in-place" if repair_in_place else "",
            " --repair-includes" if repair_includes_mode else "",
            source_file, compile_commands, alerts))

    if repair_in_place == True:
        if (base_dir is None):
            raise Exception("Option '--in_place' requires that base_dir be set.")
        if not (out_src_dir is None):
            raise Exception("Cannot specify both '--in-place' and --repaired-src'.")
        out_src_dir = base_dir
    if repair_includes_mode is None:
        repair_includes_mode = False

    if not os.path.exists(source_file):
        raise Exception(f'Error: The specified source-code file ({source_file}) does not exist.')
    if os.path.isdir(source_file):
        raise Exception(f'Error: The specified source-code file ({source_file}) is a directory, not a regular file.')

    orig_source_file = source_file
    source_file = os.path.realpath(source_file)

    if (base_dir is None):
        base_dir = os.path.dirname(source_file)
        if base_dir == "/":
            if source_file == orig_source_file:
                src_name_dump = repr(source_file)
            else:
                src_name_dump = repr(orig_source_file) + " -> " + repr(source_file)
            raise Exception(f'Error: The source-code file ({src_name_dump}) resides directly in the root directory ("/"); this is not supported.')

    base_dir = os.path.realpath(base_dir)

    if base_dir == "/":
        raise Exception('Error: base_dir may not be the root directory ("/").')

    source_base_name = os.path.basename(source_file)
    source_base_name = strip_filename_extension(source_base_name)

    if not os.path.exists(alerts):
        sys.stderr.write("Error: Alerts file %r doesn't exist!\n" % alerts)
        sys.exit(1)

    temp_step_dir = None
    if step_dir is None:
        temp_step_dir = TemporaryDirectory()
        step_dir = temp_step_dir.name

    try:
        brain_out_file = step_dir + "/" + source_base_name + ".brain-out.json"
        ast_filename   = step_dir + "/" + source_base_name + ".ear-out.json"
        if (os.getenv('acr_gzip_ear_out') or "").lower() == "true":
            ast_filename += ".gz"

        print_progress("Running ear module...")
        ear.run_ear_for_source_file(source_file, compile_commands, ast_filename, base_dir=base_dir)
        print_progress("Running brain module...")
        brain.run(ast_file=ast_filename, alerts_filename=alerts, output_filename=brain_out_file)
        compile_dir = read_json_file(ast_filename)["compile_dir"]
        if out_src_dir:
            import glove
            kwargs = {}
            if not repair_includes_mode:
                kwargs = {"repair_only": source_file}
            print_progress("Running glove module...")
            glove.run(edits_file=brain_out_file, output_dir=out_src_dir, comp_dir=compile_dir, base_dir=base_dir, **kwargs)
    finally:
        if temp_step_dir is not None:
            temp_step_dir.cleanup()

    print_progress("Finished!")


if __name__ == "__main__":
    main()
