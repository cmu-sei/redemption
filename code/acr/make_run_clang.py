#!/usr/bin/python3
# -*- coding: utf-8 -*-

# This script is meant to be self-sufficient, because it is useful to
# other projects. (Hence no use of code outside the Python libraries)

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
import hashlib
import json
import shlex
import gzip
import textwrap
import argparse

from collections import OrderedDict, defaultdict


class JSONFileException(Exception):
    pass

def read_json_file(filename):
    if filename.endswith(".gz"):
        fn_open = gzip.open
    else:
        fn_open = open
    with fn_open(filename, 'rt') as f:
        try:
            data = json.load(f, object_pairs_hook=OrderedDict)
        except Exception as e:
            raise JSONFileException(
                "Error reading JSON file: {}: {}" .format(filename, e)) from e
    return data


def init_clang_script(output_file):
        output_file.write(textwrap.dedent(
        """\
        #!/bin/sh

        ast_out_dir=$1\n
        if [ "$#" -ne 1 ]; then
            echo "Usage $0 ast_out_dir"
            exit 1
        fi
        if [ ! -d "$ast_out_dir" ]; then
            echo "Error: Output directory ($ast_out_dir) does not exist!"
            exit 1
        fi
        ast_out_dir=`realpath $ast_out_dir`
        """))


def get_compile_cmds_for_source_file(compile_cmds_file=None, source_file=None):
    if compile_cmds_file is None or compile_cmds_file == "autogen":
        compile_commands = autogen_compile_cmd(source_file)
    else:
        compile_commands = read_json_file(compile_cmds_file)

    if source_file is not None:
        source_file = os.path.realpath(source_file)

    cmds = []
    for cmd in compile_commands:
        compile_dir = get_compile_dir(cmd)
        cur_file = os.path.realpath(os.path.join(compile_dir, cmd['file']))
        if source_file is None or source_file == cur_file:
            cmds.append(cmd)
    if len(cmds) == 0:
        err_msg = (("Error: source file %r not found in compile commands!\n" % source_file) +
                   ("Files available in compile commands: %r" % skipped_files))
        raise Exception(err_msg)

    return cmds


cxx_filename = re.compile(r".*\.([ch](xx|pp?|\+\+)|[CH](PP)?|ii|t?cc)$")

def autogen_compile_cmd(source_pathname):
    source_basename = os.path.basename(source_pathname)
    if cxx_filename.match(source_basename):
        compiler = "clang++"
    else:
        compiler = "clang"
    source_dir = os.path.dirname(os.path.realpath(source_pathname))
    return (
        [
            {
                "arguments": [compiler, "-c", source_basename],
                "directory": source_dir,
                "file": source_basename
            }
        ]
    )


def get_compile_dir(cmd):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    test_dir = script_dir + "/test"
    compile_dir = cmd['directory']
    if re.match("^[$]TEST_DIR\\b", compile_dir):
        compile_dir = compile_dir.replace("$TEST_DIR", test_dir, 1)
    return compile_dir


def get_clang_cmds(compile_cmd):
    ast_out_dir = "$ast_out_dir"
    hashval = hashlib.sha256(repr(compile_cmd).encode("utf-8")).digest().hex()[:24]

    args = compile_cmd['arguments']
    compiler = args[0]
    if compiler.endswith("clang++"):
        args[0] = "clang++"
        cplusplus = True
    else:
        args[0] = "clang"
        cplusplus = False
    default_lang_std = os.getenv('acr_default_lang_std')
    if default_lang_std:
        args.insert(1, "--std=" + default_lang_std)
    new_args = []
    i = 0
    while i < len(args):
        if args[i] == "-o":
            i += 2
            continue
        else:
            new_args.append(args[i])
            i += 1
    args = new_args

    cache_base_name = os.path.splitext(os.path.basename(compile_cmd["file"]))[0][:20]
    assert(shlex.quote(cache_base_name) == cache_base_name)
    cache_ast_file = f"{cache_base_name}.{hashval}.raw.ast.json.gz"
    stderr_file    = f"{cache_base_name}.{hashval}.raw.stderr.txt"
    retcode_file   = f"{cache_base_name}.{hashval}.raw.retcode.txt"
    ll_raw_file    = f"{cache_base_name}.{hashval}.raw.ll"

    proc_args = args + "-Xclang -ast-dump=json -fsyntax-only".split()
    ll_args = args + "-Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o".split()
    compile_dir = get_compile_dir(compile_cmd)
    return [
        [
            "echo -e '\n' Building " + cache_base_name,
            "cd " + get_compile_dir(compile_cmd),
            shlex.join(proc_args) + f" 2> {ast_out_dir}/{stderr_file} | gzip > {ast_out_dir}/{cache_ast_file}; echo $? > {ast_out_dir}/{retcode_file}",
            shlex.join(ll_args) + " " + ast_out_dir + "/" + ll_raw_file
        ],
        [compile_dir, cache_ast_file, stderr_file, retcode_file, ll_raw_file],
        cplusplus
            ]


def run(compile_cmds_file, output_clang_script, source_file=None):
    if os.getenv('acr_emit_invocation'):
        print("make_run_clang.py {}{}{}{}".format(
            source_file,
            f" -c {compile_cmds_file}" if compile_cmds_file is not None else "",
            f" -s {source_file}" if source_file is not None else "",
            f" -o {output_clang_script}" if output_clang_script is not None else ""))

    cmds = get_compile_cmds_for_source_file(compile_cmds_file, source_file)
    with open(output_clang_script, 'w') as outfile:
        init_clang_script(outfile)
        for cmd in cmds:
            (clang_cmds, files, cplusplus) = get_clang_cmds(cmd)
            for clang_cmd in clang_cmds:
                outfile.write(clang_cmd + "\n")


def parse_args():
    parser = argparse.ArgumentParser(description='Creates Clang AST/LL files from source code')
    parser.add_argument('-c', "--compile-commands", type=str, dest="compile_cmds_file",
        required=True, help="The compile_comands.json file produced by Bear. Or 'autogen' for default on source file")
    parser.add_argument('-s', "--source-file", type=str, dest="source_file",
        help="Source '.c' file. If not supplied makes script for all files in codebase")
    parser.add_argument('-o', "--output-clang-script", type=str, dest="output_clang_script",
        required=True, help="Generate script that runs Clang, but do no further processing")
    cmdline_args = parser.parse_args()
    return cmdline_args


def main():
    cmdline_args = parse_args()
    run(**vars(cmdline_args))

if __name__ == "__main__":
    main()
