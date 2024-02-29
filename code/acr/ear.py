
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
import subprocess
import pprint
from util import *
import parse_preproc
import re
import hashlib
import shutil
import shlex
import functools
import bisect

class EarException(Exception):
    pass

def run_clang_parse(compile_cmd, ll_outfile):
    print_progress("Running Clang...")
    cur_dir = os.getcwd()
    os.chdir(get_compile_dir(compile_cmd))
    args = compile_cmd['arguments']
    compiler = args[0]
    if compiler.endswith("clang++"):
        args[0] = "clang++"
    else:
        args[0] = "clang"
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
    #ast = subprocess.check_output(args + "-Xclang -ast-dump=json -fsyntax-only".split())
    proc_args = args + "-Xclang -ast-dump=json -fsyntax-only".split()
    ast_proc = subprocess.run(proc_args, capture_output=True, encoding="utf-8")
    ast = ast_proc.stdout
    if ast_proc.returncode != 0:
        sys.stderr.write("="*78 + "\n")
        err_msg = ("Clang encountered an error!\n" +
            "Command line:\n" +
            "cd " + get_compile_dir(compile_cmd) + "\n" +
            shlex.join(proc_args) + "\n" +
            "Error message:\n" + ast_proc.stderr + "\n")
        os.chdir(cur_dir)
        raise EarException(err_msg)

    subprocess.check_output(args + "-Xclang -disable-O0-optnone -g -S -O0 -fno-inline -emit-llvm -o".split() + [ll_outfile])
    os.chdir(cur_dir)
    print_progress("Finished running Clang.  JSON AST size: %d characters." % len(ast))
    return ast

def get_compile_dir(compile_cmd):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    test_dir = script_dir + "/test"
    compile_dir = compile_cmd['directory']
    if re.match("^[$]TEST_DIR\\b", compile_dir):
        compile_dir = compile_dir.replace("$TEST_DIR", test_dir, 1)
    return compile_dir

def autogen_compile_cmd(source_pathname):
    source_basename = os.path.basename(source_pathname)
    source_dir = os.path.dirname(os.path.realpath(source_pathname))
    return (
        [
            {
                "arguments": ["cc", "-c", source_basename],
                "directory": source_dir,
                "file": source_basename
            }
        ]
    )

def get_compile_cmd_for_source_file(source_file, compile_cmds_file, base_dir):
    if compile_cmds_file in [None, "autogen"]:
        compile_commands = autogen_compile_cmd(source_file)
    else:
        compile_commands = read_json_file(compile_cmds_file)
    if (not base_dir) and len(compile_commands) > 1:
        raise Exception("Oops, this line shouldn't be reachable anymore!")
    source_file = os.path.realpath(source_file)
    skipped_files = []
    for cmd in compile_commands:
        compile_dir = get_compile_dir(cmd)
        cur_file = os.path.realpath(os.path.join(compile_dir, cmd['file']))
        if source_file != cur_file:
            skipped_files.append(cur_file)
            continue
        if base_dir:
            if not cur_file.startswith(base_dir + "/"):
                raise Exception("Error: Source file %r is not in the base dir %r" % (cur_file, base_dir))
        return cmd
    err_msg = (("Error: source file %r not found in compile commands!\n" % source_file) +
        ("Files available in compile commands: %r" % skipped_files))
    print(err_msg)
    raise Exception(err_msg)

def run_ear_for_cmd(cmd, ast_file, base_dir, ll_outfile):
    ast1 = run_clang_parse(cmd, ll_outfile)
    print_progress("Parsing JSON AST...")
    ast_json = json.loads(ast1, object_pairs_hook=OrderedDict)
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

    print_progress("Converting AST to JSON string...")
    ast2 = json.dumps(ast_json, indent=2) + "\n"
    print_progress("Condensing JSON...")
    ast2 = condense_json_int_pairs(ast2)
    print_progress("Writing AST to file...")
    with open(ast_file, 'w') as outfile:
        outfile.write(ast2)

def write_ear_output_for_cmd(cmd, ast_file, base_dir):
    cache_dir = os.getenv('parser_cache')
    if cache_dir and not cache_dir.startswith("/"):
        print("ERROR: environment variable 'parser_cache' must be an absolute path!")
        cache_dir = None
    compile_dir = os.path.realpath(get_compile_dir(cmd))
    base_dir = os.path.realpath(base_dir or compile_dir)
    ast_file = os.path.realpath(ast_file)
    ll_outfile = get_ast_file_base(ast_file) + ".ll"
    if (not cache_dir) or not os.path.isdir(cache_dir):
        if os.getenv('parser_cache_verbose'):
            print("No cache dir")
        return run_ear_for_cmd(cmd, ast_file, base_dir, ll_outfile)
    cur_file = os.path.realpath(os.path.join(compile_dir, cmd['file']))
    hashval = hashlib.sha256(repr([cur_file, cmd]).encode("utf-8")).digest().hex()[:24]
    cache_base_name = os.path.splitext(os.path.basename(cmd["file"]))[0]
    cache_ast_file = cache_dir + "/" + cache_base_name + "." + hashval + ".ear-out.json"
    cache_ll_file  = cache_dir + "/" + cache_base_name + "." + hashval + ".ll"
    script_dir = os.path.dirname(os.path.realpath(__file__))
    okay_cache = (
        is_nonzero_file(cache_ast_file) and
        is_nonzero_file(cache_ll_file) and
        is_newer_file(cache_ast_file, cur_file) and
        is_newer_file(cache_ast_file, __file__) and
        (not is_newer_file(cache_ast_file, cache_ll_file)))
    if okay_cache:
        if os.getenv('parser_cache_verbose'):
            print("Using cached ear output for " + cmd["file"])
        shutil.copy(cache_ast_file, ast_file)
        shutil.copy(cache_ll_file, ll_outfile)
    else:
        if os.getenv('parser_cache_verbose'):
            print("Generating ear output for " + cmd["file"])
        run_ear_for_cmd(cmd, ast_file, base_dir, ll_outfile)
        shutil.copy(ast_file, cache_ast_file)
        shutil.copy(ll_outfile, cache_ll_file)


def run_ear_for_source_file(source_file, compile_cmds_file=None, ast_file=None, base_dir=None):
    if os.getenv('acr_emit_invocation'):
        print("ear.py -s {}{}{}{}".format(
            source_file,
            f" -c {compile_cmds_file}" if compile_cmds_file is not None else "",
            f" -o {ast_file}" if ast_file is not None else "",
            f" -b {base_dir}" if base_dir is not None else ""))
    assert(ast_file != None)
    if base_dir:
        base_dir = os.path.realpath(base_dir)
    cmd = get_compile_cmd_for_source_file(source_file, compile_cmds_file, base_dir)
    write_ear_output_for_cmd(cmd, ast_file, base_dir)

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
    parser.add_argument('-o', "--ast-file", type=str, dest="ast_file",
        required=True, help="Filename for output AST file, must end in '.ear-out.json'")
    parser.add_argument('-s', "--source-file", type=str, dest="source_file",
        required=True, help="Source '.c' file")
    parser.add_argument('-c', "--compile-commands", type=str, dest="compile_cmds_file",
        help="The compile_comands.json file produced by Bear")
    parser.add_argument('-b', "--base-dir", type=str, dest="base_dir",
        help="Base directory of the project")
    cmdline_args = parser.parse_args()
    return cmdline_args

def main():
    cmdline_args = parse_args()
    run_ear_for_source_file(**vars(cmdline_args))

if __name__ == "__main__":
    main()
