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
# Example usage:
# export acr_gzip_ear_out=true
# export acr_parser_cache=/host/code/acr/test/cache/
# mkdir $acr_parser_cache -p
# cd /host/data/test
# time /host/code/acr/test/test_runner.py git.rosecheckers.MSC12-C.test.yml
# python3 /host/code/analysis/extract_ear_func_bounds.py -o func_bounds.json
######################################################################

import os, sys
import argparse
import subprocess
import pprint
import glob
import json

sys.path.append('/host/code/acr')
from util import *
from make_run_clang import read_json_file

func_bounds = []

class FuncVisitor(AstVisitor):
    def previsit(self, node):
        if not isinstance(node, dict):
            return
        func_like_decls = [
            "CXXMethodDecl",
            "CXXConstructorDecl",
            "CXXDestructorDecl",
            "CXXConversionDecl",
        ]
        if node.get("kind") in func_like_decls:
            self.visit_FunctionDecl(node)

    def visit_FunctionDecl(self, node):
        filename = get_dict_path(node, "range", "file")
        #if node.get("name") == "fiber_switch":
        #    breakpoint()
        if not filename:
            return

        # Quick and dirty way to exclude system header files.
        # For a more robust solution, take the base dir as a command-line
        # argument and test whether the file is within the base dir.
        if filename.startswith("/usr"):
            return

        inner = node.get("inner")
        if not inner:
            return

        def get_body(inner):
            for body in inner:
                try:
                    body_kind = body["kind"]
                except:
                    continue
                if body_kind == "CompoundStmt":
                    return body
            return None
        body = get_body(inner)
        if body is None:
            return

        def get_line(subnode):
            if not subnode:
                return None
            if subnode.get("expansionLoc"):
                subnode = subnode.get("expansionLoc")
            return subnode.get("line")
        begin_line = get_line(get_dict_path(node, "range", "begin"))
        end_line   = get_line(get_dict_path(node, "range", "end"))
        if (not begin_line) or (not end_line):
            return

        func_bounds.append([filename, begin_line, end_line, node["name"]])

def parse_args():
    parser = argparse.ArgumentParser(description='Finds boundaries (starting line and ending line) of functions, using the cached ear output in $acr_parser_cache.')
    parser.add_argument('-f', type=str, dest="single_input_file", required=False, help="Run on just the single specified ear output file")
    parser.add_argument('-o', type=str, dest="out_file", required=True, help="Output file")
    return parser.parse_args()


def main():
    args = parse_args()

    cache_dir = os.getenv('acr_parser_cache')
    if (not cache_dir) or not cache_dir.startswith("/"):
        print("ERROR: environment variable 'acr_parser_cache' must be an absolute path!")
        sys.exit(1)

    if args.single_input_file:
        all_ear_files = [args.single_input_file]
    else:
        all_ear_files = list(glob.iglob(f'{cache_dir}/*.json*'))
    num_files = len(all_ear_files)
    for (ix, filename) in enumerate(all_ear_files):
        print(f"[{ix+1:4}/{num_files}] File: {filename}")
        try:
            ast = read_json_file(filename)
        except:
            print(f"Error reading {filename}!!!")
            continue
        FuncVisitor().visit(ast)

    with open(args.out_file, "w") as out_file:
        out_file.write(json.dumps(func_bounds, indent=2) + "\n")

if __name__ == "__main__":
    main()
