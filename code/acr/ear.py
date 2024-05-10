
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
import sys
import subprocess
import pprint
from util import print_progress, read_whole_file, is_nonzero_file, \
                 is_newer_file, get_ast_file_base, condense_json_int_pairs
import hashlib
import shutil
import functools
import bisect
import gzip
import json
from collections import OrderedDict
import argparse

import parse_preproc
from make_run_clang import get_compile_cmds_for_source_file, get_compile_dir, get_clang_cmds

class EarException(Exception):
    pass


def run_clang_parse(compile_cmd, clang_output_dir, generated=False):
    print_progress(f"Running Clang on {compile_cmd['file']}...")

    (clang_cmds, clang_output_files) = get_clang_cmds(compile_cmd)
    (compile_dir, ast_file, stderr_file, retcode_file, ll_file) = clang_output_files

    clang_output_dir = os.path.realpath(clang_output_dir)
    ast_file = clang_output_dir + "/" + ast_file
    stderr_file = clang_output_dir + "/" + stderr_file
    retcode_file = clang_output_dir + "/" + retcode_file
    ll_file = clang_output_dir + "/" + ll_file

    if generated is True:
        if (not clang_output_dir) or not os.path.isdir(clang_output_dir):
            sys.stderr.write(f"Error: \"--raw-ast-dir {clang_output_dir}\": directory doesn't exit!\n")
            sys.exit(1)

    environ = {**os.environ, "ast_out_dir": clang_output_dir}
    cur_dir = os.getcwd()
    os.chdir(compile_dir)
    if generated is False:
        ast_proc = subprocess.run(clang_cmds[1], env=environ, shell=True, capture_output=True, encoding="utf-8")

    class AttrDict(dict):
        def __getattr__(self, item):
            return self[item]
    try:
        ast_proc = AttrDict({
            "stdout": read_whole_file(ast_file),
            "stderr": read_whole_file(stderr_file),
            "returncode": int(read_whole_file(retcode_file)),
        })
    except FileNotFoundError as exc:
        raise EarException(f"File not found: {exc.filename!r}") from None

    if ast_proc.returncode != 0:
        sys.stderr.write("="*78 + "\n")
        err_msg = ("Clang encountered an error!\n" +
            "Command line:\n" + clang_cmds[1] + "\n" +
            "Error message:\n" + ast_proc.stderr + "\n")
        os.chdir(cur_dir)
        raise EarException(err_msg)
    if generated is False:
        subprocess.check_output(clang_cmds[2], shell=True, env=environ)
    os.chdir(cur_dir)

    print_progress("Finished running Clang.")
    return [ast_file, ll_file]


def update_ast( ast_json, base_dir, cmd):
    compile_dir = os.path.realpath(get_compile_dir(cmd))
    base_dir = os.path.realpath(base_dir or compile_dir)
    ast_json["base_dir"] = base_dir
    ast_json["compile_dir"] = compile_dir
    ast_json["file"] = cur_file = os.path.realpath(os.path.join(compile_dir, cmd['file']))
    @functools.lru_cache(maxsize=None)
    def add_path(s):
        return os.path.realpath(os.path.join(compile_dir, s))
    print_progress("Processing AST...")
    incl_files = find_included_files(ast_json, add_path)
    renumber_ids(ast_json, {})
    add_filenames(ast_json, [cur_file], add_path)
    preproc_db = {}
    comments_db = {}
    newlines_db = {}
    print_progress("Parsing preprocessor tokens...")
    for cur_file in incl_files:
        info = parse_preproc.parse_file(cur_file)
        preproc_db[cur_file] = info['directives']
        comments_db[cur_file] = info['comments']
        newlines_db[cur_file] = info['newlines']
    add_line_numbers(ast_json, newlines_db, add_path)
    ast_json["preproc_db"] = preproc_db
    ast_json["comments_db"] = comments_db
    ast_json["newlines_db"] = newlines_db

    return ast_json


def run_ear_for_cmd(cmd, base_dir, ast_file, ll_outfile, raw_ast_dir=None):
    generated = (raw_ast_dir is not None)
    if generated is False:
        raw_ast_dir = os.path.dirname(ll_outfile)
    [ast_raw_file, ll_raw_file] = run_clang_parse(cmd, raw_ast_dir, generated)
    shutil.copy(ll_raw_file, ll_outfile)

    print_progress("Parsing JSON AST...")
    ast1 = read_whole_file(ast_raw_file)
    ast_json = json.loads(ast1, object_pairs_hook=OrderedDict)

    ast_json = update_ast( ast_json, base_dir, cmd)

    print_progress("Converting AST to JSON string...")
    ast2 = json.dumps(ast_json, indent=2) + "\n"
    print_progress("Condensing JSON...")
    ast2 = condense_json_int_pairs(ast2)
    print_progress("Writing AST to file...")
    if ast_file.endswith(".gz"):
        fn_open = lambda name, mode: gzip.open(name, mode, compresslevel=7)
    else:
        fn_open = open
    with fn_open(ast_file, 'wt') as outfile:
        outfile.write(ast2)


def write_ear_output_for_cmd(cmd, base_dir, ast_file=None, raw_ast_dir=None):
    cache_dir = os.getenv('acr_parser_cache')
    if cache_dir and not cache_dir.startswith("/"):
        print("ERROR: environment variable 'acr_parser_cache' must be an absolute path!")
        cache_dir = None
    compile_dir = os.path.realpath(get_compile_dir(cmd))
    base_dir = os.path.realpath(base_dir or compile_dir)
    ll_outfile = None
    if ast_file is not None:
        ast_file = os.path.realpath(ast_file)
        ll_outfile = get_ast_file_base(ast_file) + ".ll"
    if (not cache_dir) or not os.path.isdir(cache_dir):
        if os.getenv('acr_parser_cache_verbose'):
            print("No cache dir")
        return run_ear_for_cmd(cmd, base_dir, ast_file, ll_outfile, raw_ast_dir)

    cur_file = os.path.realpath(os.path.join(compile_dir, cmd['file']))
    cache_base_name = os.path.splitext(os.path.basename(cmd["file"]))[0][:20]
    script_dir = os.path.dirname(os.path.realpath(__file__))

    hashval = hashlib.sha256(repr(cmd).encode("utf-8")).digest().hex()[:24]
    okay_cache = None
    if ast_file is not None:
        opt_gz = (".gz" if ast_file.endswith(".gz") else "")
        cache_ast_file = cache_dir + "/" + cache_base_name + "." + hashval + ".ear-out.json" + opt_gz
        cache_ll_file  = cache_dir + "/" + cache_base_name + "." + hashval + ".ll"
        okay_cache = (
            is_nonzero_file(cache_ast_file) and
            is_nonzero_file(cache_ll_file) and
            is_newer_file(cache_ast_file, cur_file) and
            is_newer_file(cache_ast_file, __file__) and
            (not is_newer_file(cache_ast_file, cache_ll_file)))
    if okay_cache:
        if os.getenv('acr_parser_cache_verbose'):
            print("Using cached ear output for " + cmd["file"])
        shutil.copy(cache_ast_file, ast_file)
        shutil.copy(cache_ll_file, ll_outfile)
    else:
        if os.getenv('acr_parser_cache_verbose'):
            print("Generating ear output for " + cmd["file"])
        run_ear_for_cmd(cmd, base_dir, ast_file, ll_outfile, raw_ast_dir)
        shutil.copy(ast_file, cache_ast_file)
        shutil.copy(ll_outfile, cache_ll_file)


def run_ear_for_source_file(source_file, compile_cmds_file=None, ast_file=None, base_dir=None, raw_ast_dir=None):
    if os.getenv('acr_emit_invocation'):
        print("ear.py -s {}{}{}{}{}".format(
            source_file,
            f" -c {compile_cmds_file}" if compile_cmds_file is not None else "",
            f" -o {ast_file}" if ast_file is not None else "",
            f" -b {base_dir}" if base_dir is not None else "",
            f" -r {raw_ast_dir}" if raw_ast_dir is not None else ""))
    if base_dir:
        base_dir = os.path.realpath(base_dir)
    if raw_ast_dir is None:
        if compile_cmds_file is None and ast_file is None:
            sys.stderr.write("Must provide either compile_cmds_file or ast_file when running complete ear module")
            sys.exit(1)

    cmds = get_compile_cmds_for_source_file(compile_cmds_file, source_file)
    write_ear_output_for_cmd(cmds[0], base_dir, ast_file, raw_ast_dir)


def add_line_numbers(node, newlines, add_path, /):
    def add_line_numbers_helper(node, current_id, current_file, /):
        match node:
            case [*_]:
                for x in node:
                    add_line_numbers_helper(x, current_id, current_file)
            case {}:
                current_id = node.get("id", current_id)
                match node:
                    case {"file": fn}:
                        current_file = add_path(fn)
                offset = node.get("offset")
                if offset is not None and "line" not in node:
                    indices = newlines.get(current_file)
                    if indices is not None:
                        idx = bisect.bisect_left(indices, offset)
                        node["line"] = idx + 1
                        if "col" not in node:
                            if idx == 0:
                                node["col"] = offset + 1
                            else:
                                node["col"] = offset - indices[idx - 1]
                for x in node.values():
                    add_line_numbers_helper(x, current_id, current_file)
    add_line_numbers_helper(node, None, None)

def add_filenames(node, p_cur_filename, add_path):
    if isinstance(node, list):
        for x in node:
            add_filenames(x, p_cur_filename, add_path)
        return
    if node == {}:
        return
    if node is None:
        return
    if isinstance(node, (str, int)):
        return
    node_type = node.get('kind')
    if node_type is None:
        return

    if node.get('loc'):
        if node['loc'].get('file'):
            p_cur_filename[0] = node['loc'].get('file')
        if not node.get('range'):
            print(node["id"])
    if node.get("range") and node["range"].get("begin"):
        range_file = node["range"]["begin"].get("file")
        # FIXME: assert fails on git/builtin/push.c
        # assert(range_file is None)
        node["range"]["file"] = add_path(p_cur_filename[0])

    for (k,v) in node.items():
        add_filenames(v, p_cur_filename, add_path)


def renumber_ids(node, id_map):
    if isinstance(node, list):
        for x in node:
            renumber_ids(x, id_map)
        return
    if node is None:
        return
    if isinstance(node, (str, int)):
        return
    for id_field in ["id", "previousDecl", "typeAliasDeclId"]:
        node_id = node.get(id_field)
        if node_id:
            new_id = id_map.get(node_id)
            if not new_id:
                new_id = len(id_map) + 1000
                id_map[node_id] = new_id
                node[id_field] = new_id
            else:
                if id_field == "id":
                    node["prevId"] = new_id
                    node["id"] = str(new_id) + "b"
                else:
                    node[id_field] = new_id
    for (k,v) in node.items():
        renumber_ids(v, id_map)

def find_included_files(ast, add_path):
    incl_files = set()
    find_included_files_aux(ast, incl_files)
    base_dir = ast["base_dir"]
    def is_fake_file(s):
        return s.startswith("<") and s.endswith(">")
    def in_base_dir(pathname, base_dir):
        return pathname.startswith(base_dir + "/")
    def is_okay_file(s):
        if is_fake_file(s):
            return False
        abs_file = add_path(s)
        if not os.path.isfile(abs_file):
            return False
        return in_base_dir(abs_file, base_dir)
    incl_files = sorted([add_path(x) for x in incl_files if is_okay_file(x)])
    return incl_files

def find_included_files_aux(node, files):
    if isinstance(node, list):
        for child in node:
            find_included_files_aux(child, files)
        return
    if node is None:
        return
    if isinstance(node, (str, int)):
        return
    cur_file = node.get('file')
    if cur_file:
        files.add(cur_file)
    for (k,v) in node.items():
        find_included_files_aux(v, files)

def parse_args():
    parser = argparse.ArgumentParser(description='Creates AST files from source code')
    parser.add_argument('-c', "--compile-commands", type=str, dest="compile_cmds_file",
        required=True, help="The compile_comands.json file produced by Bear")
    parser.add_argument('-b', "--base-dir", type=str, dest="base_dir",
        help="Base directory of the project")
    parser.add_argument('-s', "--source-file", type=str, dest="source_file",
        required=True, help="Source '.c' file")
    parser.add_argument('-o', "--ast-file", type=str, dest="ast_file",
        help="Filename for output AST file, must end in '.ear-out.json' or '.ear-out.json.gz'")
    parser.add_argument('-r', "--raw-ast-dir", type=str, dest="raw_ast_dir",
        help="Process contents of AST directory, rather than source code")

    cmdline_args = parser.parse_args()
    return cmdline_args

def main():
    cmdline_args = parse_args()
    run_ear_for_source_file(**vars(cmdline_args))


if __name__ == "__main__":
    main()
