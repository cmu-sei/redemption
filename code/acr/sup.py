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
import ear, brain, hand
import pprint
import hashlib
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
    parser = argparse.ArgumentParser(description='Creates repaired source-code files',
                                     epilog="See the Redemption README.md file For more info.")
    parser.add_argument("-c", "--compile_commands", type=str, required=True, dest="compile_cmds_file",
        help="The compile_comands.json file produced by Bear")
    parser.add_argument("-a", "--alerts", type=str, required=True,
        help="Static-analysis alerts")
    parser.add_argument("-t", '--step-dir', type=str, dest="step_dir", default=None,
                        help="Directory to write intermediate files of the steps of the process. (default: temporary directory)")
    parser.add_argument("-b", "--base-dir", type=str, dest="base_dir", required=True,
        help="Base directory of the project")
    parser.add_argument("-e", type=str, dest="combined_hand_out", required=False,
        help="Output file (JSON) for combined edits")
    parser.add_argument('--inject-hand-output', action="store_true", required=False,
        help="If hand-module output files already exist, use them instead of regenerating them (this is for debugging/testing purposes)")
        # Note: This is for testing the code that detects conflicts between repairs,
        # because currently we need to hack the hand output files to get a conflict.
    parser.add_argument('--repaired-src', type=str, dest="out_src_dir", required=False,
        help="Directory to write repaired source files (or omit to refrain from running the glove module)")
    cmdline_args = parser.parse_args()
    return cmdline_args

def main():
    cmdline_args = parse_args()
    run(**vars(cmdline_args))

def tuplize(L):
    if isinstance(L, (list, tuple)):
        return tuple([tuplize(x) for x in L])
    else:
        return L

def flag_overlapping_repairs(alert_list):
    edits_by_file = OrderedDict()
    for alert in alert_list:
        alert_id = alert["alert_id"]
        for (filename, edit_list) in alert["patch"]:
            edits_by_file.setdefault(filename, [])
            edit_list = [[start, end, replacement, alert_id] for
                         [start, end, replacement] in edit_list]
            edits_by_file[filename].extend(edit_list)

    overlap_map = {}
    for (filename, edit_list) in edits_by_file.items():
        prev_end = -1
        prev_replacement = None
        prev_alert_id = None
        for [start, end, replacement, alert_id] in sorted(edit_list):
            has_bad_overlap = ((start < prev_end) or
                (start == prev_end and replacement != prev_replacement))
            if has_bad_overlap:
                overlap_map.setdefault(alert_id, set()).add(prev_alert_id)
                overlap_map.setdefault(prev_alert_id, set()).add(alert_id)
            prev_end = end
            prev_replacement = replacement
            prev_alert_id = alert_id

    #stop()

    for (alert_id, overlapping_alerts) in overlap_map.items():
        alert_index = alert_id - 1
        if (alert_list[alert_index]["patch"] != []):
            alert_list[alert_index]["skipped_repair"] = alert_list[alert_index]["patch"]
            alert_list[alert_index]["patch"] = []
            alert_list[alert_index]["why_skipped"] = "Overlaps with other alerts"
            alert_list[alert_index]["overlapping_alerts"] = sorted(overlapping_alerts)

def combine_hand_outs(indiv_hand_filenames):
    indiv_hand_outs = [read_json_file(x) for x in indiv_hand_filenames]
    def all_equal(L):
        return len(set(L)) == 1
    if not all_equal([len(x) for x in indiv_hand_outs]):
        # Our code is set up so that, for each TU, the hand module gets the
        # entire list of alerts (for the whole codebase) and adds additional
        # information for the alerts that are relevant to the TU; the hand
        # module then returns the enhanced alert list.  So, the alert lists
        # should all be the same length.  An injected hand output with the
        # wrong number of alerts will screw up the loop thru the alerts later
        # in this function.
        print("Error: Different number of alerts in individual hand output files!")
        for (j, filename) in zip(indiv_hand_outs, indiv_hand_filenames):
            print("%4d alerts in %s" % (len(j), filename))
    num_alerts = len(indiv_hand_outs[0])

    def combine_alert(alert_id, variants):
        non_empty = []
        algos = None
        for (v, filename) in zip(variants, indiv_hand_filenames):
            if v['alert_id'] != alert_id:
                print(f"Error in {filename}: Expecting alert_id {alert_id} but found alert_id {v['alert_id']}.")
            if v['patch'] != []:
                non_empty.append(tuplize(v['patch']))
                if algos is None:
                    algos = v.get('repair_algo')
        combined = variants[0].copy()
        if all_equal(non_empty):
            if algos:
                combined['repair_algo'] = algos
            if 'patch' in combined:
                del combined['patch']
            combined['patch'] = non_empty[0]
        elif len(non_empty) == 0:
            pass
        else:
            if 'repair_algo' in combined:
                del combined['repair_algo']
            combined['patch'] = []
            combined['why_skipped'] = "Different repairs from different translation units"
            combined['conflicting_repairs'] = sorted(non_empty)
        return combined

    combined_alert_list = []
    for alert_index in range(0, num_alerts):
        alert_id = alert_index + 1
        variants = [alert_list[alert_index] for alert_list in indiv_hand_outs]
        combined_alert_list.append(combine_alert(alert_id, variants))

    flag_overlapping_repairs(combined_alert_list)

    return combined_alert_list

def run(*, compile_cmds_file, alerts, base_dir, combined_hand_out=None, step_dir=None, out_src_dir=None, inject_hand_output=False):
    base_dir = os.path.realpath(base_dir)
    compile_commands = read_json_file(compile_cmds_file)
    num_tus = len(compile_commands)
    indiv_hand_filenames = []

    if base_dir == "/":
        raise Exception('Error: base_dir may not be the root directory ("/").')

    temp_step_dir = None
    if step_dir is None:
        temp_step_dir = TemporaryDirectory()
        step_dir = temp_step_dir.name

    if combined_hand_out is None:
        hashval = hashlib.sha256(read_whole_file(compile_cmds_file, "b") + read_whole_file(alerts, "b")).hexdigest()[:24]
        base_name = strip_filename_extension(os.path.basename(compile_cmds_file))
        combined_hand_out = f"{step_dir}/{hashval}.combined.json"

    try:
        for (tu_index, cmd) in enumerate(compile_commands):
            compile_dir = ear.get_compile_dir(cmd)
            cur_file = os.path.realpath(os.path.join(compile_dir, cmd['file']))
            if not cur_file.startswith(base_dir + "/"):
                raise Exception("Error: Source file %r is not in the base dir %r" % (cur_file, base_dir))

            source_base_name = os.path.basename(cur_file)
            source_base_name = strip_filename_extension(source_base_name)
            source_base_name = source_base_name + "." + (("tu%0"+str(len(str(num_tus)))+"d") % tu_index)

            ast_filename = step_dir + "/" + source_base_name + ".ear-out.json"
            brain_out_file = step_dir + "/" + source_base_name + ".brain-out.json"
            hand_out_file = step_dir + "/" + source_base_name + ".hand-out.json"

            skip_generating_hand_out = inject_hand_output and os.path.exists(hand_out_file)
            if not skip_generating_hand_out:
                ear.write_ear_output_for_cmd(cmd, ast_filename, base_dir)
                brain.run(ast_file=ast_filename, alerts_filename=alerts, output_filename=brain_out_file)
                hand.run(ast_file=ast_filename, alerts_filename=brain_out_file, output_filename=hand_out_file, warn_missing=False)
            indiv_hand_filenames.append(hand_out_file)

        combined_alerts = combine_hand_outs(indiv_hand_filenames)
        with open(combined_hand_out, 'w') as outfile:
            outfile.write(json.dumps(combined_alerts, indent=2) + "\n")

        if out_src_dir:
            import glove
            glove.run(edits_file=combined_hand_out, output_dir=out_src_dir, base_dir=base_dir)

    finally:
        if temp_step_dir is not None:
            temp_step_dir.cleanup()


if __name__ == "__main__":
    main()
