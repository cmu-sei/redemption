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

######################################################################
# Example usage, using func_bounds.test_errors.json produced by 
# extract_func_names_lines_clang.py or extract_ear_func_bounds.py:
#
# python3 /host/code/analysis/get_enclosing_func.py /host/code/acr/test/test_errors.c 10 func_bounds.test_errors.json
######################################################################

import argparse
import sys
import os
import json
import pdb

def get_enclosing_func(filename, alert_line_num, func_boundaries):
    filename = os.path.realpath(filename)
    with open(filename, 'r') as file:
        lines = file.readlines()

    lines[alert_line_num - 1] = lines[alert_line_num - 1].rstrip('\n') + f" // Line {alert_line_num}\n"

    def find_start_and_end():
        for (func_file, start_line, end_line, func_name) in func_boundaries:
            if filename != func_file:
                continue
            if start_line <= alert_line_num <= end_line:
                return (start_line, end_line)
        return (None, None)
    (start_line, end_line) = find_start_and_end()
    if start_line is None:
        sys.stderr.write("Error: unable to locate function enclosing specified line!\n")
        return ""

    if end_line - start_line <= 300:
        func_text = ''.join(lines[start_line-1:end_line-1 + 1])
    else:
        chosen_lines = []
        last_chosen = start_line - 1
        for i in range(start_line, end_line+1):
            is_chosen = (
                (i - start_line <= 10) or
                (abs(i - alert_line_num) <= 100) or
                (end_line - i <= 3)
            )
            if is_chosen:
                if last_chosen != i - 1:
                    chosen_lines.append("...\n")
                chosen_lines.append(lines[i-1]) # 1-based indexing for line nums
                last_chosen = i
        func_text = ''.join(chosen_lines)
        
    return func_text

def main():
    parser = argparse.ArgumentParser(description="Find and return the function enclosing a specified line in a C file.")
    parser.add_argument("filename", type=str, help="C source code file.")
    parser.add_argument("line_num", type=int, help="The line number to examine (1-indexed).")
    parser.add_argument("func_boundaries", type=str, help="Function-boundary JSON file.")
    args = parser.parse_args()

    with open(args.func_boundaries, 'r') as f:
        func_boundaries = json.load(f)
    
    func_text = get_enclosing_func(args.filename, args.line_num, func_boundaries)
    
    print(func_text)

if __name__ == "__main__":
    main()
