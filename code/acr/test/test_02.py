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
import shlex
import difflib
import re
sys.path.append('..')
import ear, brain, glove, end_to_end_acr, sup
import test_runner
from util import *
from make_run_clang import read_json_file
from pprint import pprint
import difflib
import string

def read_whole_file(filename):
    with open(filename, 'r') as the_file:
        return the_file.read()

def read_whole_file_as_bytes(filename):
    with open(filename, 'rb') as the_file:
        return the_file.read()

def delete_refIds(s):
    return re.sub('"refId": "[A-Za-z0-9]*"', '"refId": ""', s)

def delete_ids(s):
    s = re.sub('"id": "[A-Za-z0-9]*"', '"id": ""', s)
    s = re.sub('"ast_id": [0-9]*', '"ast_id": ""', s)
    s = re.sub('"refId": "[A-Za-z0-9]*"', '"refId": ""', s)
    return s

def delete_ids_and_filenames(s):
    s = re.sub('"id": "[A-Za-z0-9]*"', '"id": ""', s)
    s = re.sub('"refId": "[A-Za-z0-9]*"', '"refId": ""', s)
    s = re.sub('"ast_id": [0-9]*', '"ast_id": ""', s)
    s = re.sub('"file": "[^"]*"', '"file": ""', s)
    s = re.sub('"base_dir": "[^"]*"', '"compile_dir": ""', s)
    s = re.sub('"compile_dir": "[^"]*"', '"compile_dir": ""', s)
    s = relativize_paths(s)
    if not s.endswith("\n"):
        s += "\n"
    return s

def relativize_paths(s):
    s = re.sub('"/.*/test\\b', '"test', s)
    return s

def cmp_file_normalize(file1, file2, fn_norm=None):
    if (fn_norm is None):
        fn_norm = lambda x: x
    def norm_base(s):
        s = re.sub("[$]BASE[/]", "/host/code/acr/test/", s)
        if os.getenv('acr_ignore_ast_id') == "true":
            s = delete_ids(s)
        else:
            # ALWAYS delete the refIds in the comparison
            s = delete_refIds(s)
        return s
    fc1 = fn_norm(norm_base(read_whole_file(file1)))
    fc2 = fn_norm(norm_base(read_whole_file(file2)))

    # ignore whitespace when performing comparisons
    mapping = {ord(c): None for c in string.whitespace}
    ret = (fc1.translate(mapping) == fc2.translate(mapping))

    if ret is False:
        print("Normalized files differ: %s != %s" % (file1, file2))

        # NOTE: useful snippets and output for debugging unit tests
        
        # NOTE: using file1 and file2 loaded in a difftool enables fast debugging
        # with open("_expected.json", "w+") as w1:
        #     w1.write(fc1)
        # with open("_actual.json", "w+") as w2:
        #     w2.write(fc2)
        
        # NOTE: useful for diffing on the CLI, unless the diffs become too large
        # d = difflib.Differ()
        # diffs = list(d.compare(fc1.splitlines(keepends=True), fc2.splitlines(keepends=True)))
        # pprint(diffs)
        
        # NOTE: very detailed output for non-equal sequence matching
        # delta = difflib.SequenceMatcher(None, fc1, fc2)
        # for tag, i1, i2, j1, j2 in delta.get_opcodes():
        #     if (tag != "equal"):
        #         print('{:7}   a[{}:{}] --> b[{}:{}] {!r:>8} --> {!r}'.format(
        #             tag, i1, i2, j1, j2, fc1[i1:i2], fc2[j1:j2]))

    return ret
    # TODO: report a diff if the comparison fails

# TODO: make a temp dir instead of using "out" in current directory;
# see https://docs.pytest.org/en/6.2.x/fixture.html

def test_ear_03():
    os.system("rm -f test/out/simple_null_check.ear-out.json")
    cur_dir = os.getcwd()
    os.chdir("..")
    try:
        ear.run_ear_for_source_file(
            ast_file="test/out/simple_null_check.ear-out.json",
            source_file="test/simple_null_check.c",
            compile_cmds_file="test/simple_null_check_compile_cmds.json")
    finally:
        os.chdir(cur_dir)
    assert cmp_file_normalize("simple_null_check.ear-out.answer.json", "out/simple_null_check.ear-out.json", delete_ids_and_filenames)
    test_runner.cleanup("simple_null_check.c", out_location="out", step_dir="out", additional_files="out/simple_null_check.ear-out.json")
    pass

def test_brain_03():
    #os.system("python3 ../brain.py --no-patch -o out/simple_null_check.brain-out.json -a simple_null_check.alerts.json simple_null_check.ear-out.answer.json")
    os.system("rm -f out/simple_null_check.brain-out.json")
    brain.run(ast_file="simple_null_check.ear-out.answer.json", alerts_filename="simple_null_check.alerts.json", output_filename="out/simple_null_check.brain-out.json")
    assert cmp_file_normalize("simple_null_check.brain-out.answer.json", "out/simple_null_check.brain-out.json", relativize_paths)
    test_runner.cleanup("simple_null_check.c", out_location="out", step_dir="out", additional_files="out/simple_null_check.brain-out.json")

def test_glove_03():
    os.system("rm -f out/simple_null_check.c")
    #os.system("python3 ../glove.py simple_null_check.hand-out.answer.json -o out")
    glove.run(edits_file="simple_null_check.brain-out.answer.json", output_dir="out", comp_dir=".")
    assert cmp_file_normalize("simple_null_check.repaired.answer.c", "out/simple_null_check.c")
    test_runner.cleanup("simple_null_check.c", out_location="out", step_dir="out", additional_files="out/acr.h out/simple_null_check.c")

def test_end_to_end_test():
    if(os.path.exists("out")):
        step_dir_prev_existed = True
    else:
        step_dir_prev_existed = False
    os.system("mkdir -p out")
    os.system("rm -f out/simple_null_check.c")
    source_file="test/simple_null_check.c"
    compile_commands="autogen"
    alerts="test/simple_null_check.alerts.json"
    out_src_dir="test/out"

    cur_dir = os.getcwd()
    os.chdir("..")
    try:
        end_to_end_acr.run(
            source_file=source_file,
            compile_commands=compile_commands,
            alerts=alerts,
            step_dir=out_src_dir,
            out_src_dir=out_src_dir)
    finally:
        os.chdir(cur_dir)
    assert cmp_file_normalize("test_e2e_02.repaired.c", "out/simple_null_check.c")
    fixed_c_file = out_src_dir+"/"+source_file
    test_runner.cleanup(source_file, out_location=out_src_dir, step_dir="out", additional_files="out/test02.ast.json out/simple_null_check.repairs.json out/simple_null_check.c out/acr.h")
    test_runner.dir_final_cleanup("out/header_in_subdir", step_dir_prev_existed=step_dir_prev_existed)

def test_CWE_476_test():
    if(os.path.exists("out")):
        step_dir_prev_existed = True
    else:
        step_dir_prev_existed = False
    os.system("mkdir -p out")
    os.system("rm -f out/simple_null_check.c")
    source_file="test/simple_null_check.c"
    compile_commands="autogen"
    alerts="test/simple_null_check.CWE-476.alerts.json"
    out_src_dir="test/out"

    cur_dir = os.getcwd()
    os.chdir("..")
    try:
        end_to_end_acr.run(
            source_file=source_file,
            compile_commands=compile_commands,
            alerts=alerts,
            step_dir=out_src_dir,
            out_src_dir=out_src_dir)
    finally:
        os.chdir(cur_dir)
    assert cmp_file_normalize("test_e2e_02.repaired.c", "out/simple_null_check.c")
    fixed_c_file = out_src_dir+"/"+source_file
    test_runner.cleanup(source_file, out_location=out_src_dir, step_dir="out", additional_files="out/test02.ast.json out/simple_null_check.repairs.json out/simple_null_check.c out/acr.h")
    test_runner.dir_final_cleanup("out/header_in_subdir", step_dir_prev_existed=step_dir_prev_existed)

def test_ear_04():
    os.system("rm -f test/out/preproc_parser_1.ear-out.json")
    ast_file="test/out/preproc_parser_1.ear-out.json"
    source_file="test/preproc_parser_1.c"
    compile_cmds_file="test/preproc_parser_1_compile_cmds.json"
    cur_dir = os.getcwd()
    os.chdir("..")
    try:
        ear.run_ear_for_source_file(
            ast_file=ast_file,
            source_file=source_file,
            compile_cmds_file=compile_cmds_file)
    finally:
        os.chdir(cur_dir)
    assert cmp_file_normalize("preproc_parser_1.ear-out.answer.json", "out/preproc_parser_1.ear-out.json", delete_ids_and_filenames)
    test_runner.cleanup(source_file, out_location="out", step_dir="out", additional_files="out/preproc_parser_1.ear-out.json")
    pass


def test_e2e_06a():
    if(os.path.exists("out")):
        step_dir_prev_existed = True
    else:
        step_dir_prev_existed = False
    os.system("mkdir -p out")
    os.system("rm -f out/header_null_ptr*.*")
    #os.system("cd ..; python3 end_to_end_acr.py test/header_null_ptr.c test/header_null_ptr_compile_cmds.json test/header_null_ptr.alerts.json -o test/out/header_null_ptr.repairs.json --ast-dir test/out --repaired-src test/out")
    source_file="test/header_null_ptr.c"
    compile_commands="autogen"
    alerts="test/header_null_ptr.alerts.json"
    out_src_dir="test/out"
    repair_includes_mode=False

    cur_dir = os.getcwd()
    os.chdir("..")
    try:
        end_to_end_acr.run(
            source_file=source_file,
            compile_commands=compile_commands,
            alerts=alerts,
            step_dir=out_src_dir,
            out_src_dir=out_src_dir,
            repair_includes_mode=repair_includes_mode)
    finally:
        os.chdir(cur_dir)
    assert(not os.path.exists("out/header_null_ptr.h"))
    files_to_delete = ["out/header_null_ptr.ast.json", "out/acr.h", "out/header_null_ptr.repairs.json"]
    for x in files_to_delete:
        test_runner.cleanup(source_file, out_location=out_src_dir, step_dir=out_src_dir, repair_includes_mode=repair_includes_mode, additional_files=x)
    test_runner.dir_final_cleanup("out/header_in_subdir", step_dir_prev_existed=step_dir_prev_existed)


def test_e2e_06b():
    if(os.path.exists("out")):
        step_dir_prev_existed = True
    else:
        step_dir_prev_existed = False
    os.system("mkdir -p out")
    os.system("rm -f out/header_null_ptr*.*")
    source_file="test/header_null_ptr.c"
    compile_commands="autogen"
    alerts="test/header_null_ptr.alerts.json"
    step_dir="test/out"
    out_src_dir="test/out"
    repair_includes_mode=True
    os.system("cp header_null_ptr.c header_null_ptr.h out/")
    cur_dir = os.getcwd()
    os.chdir("..")
    try:
        end_to_end_acr.run(
            source_file=source_file,
            compile_commands=compile_commands,
            alerts=alerts,
            step_dir=step_dir,
            out_src_dir=out_src_dir,
            repair_includes_mode=repair_includes_mode)
    finally:
        os.chdir(cur_dir)
    assert cmp_file_normalize("header_null_ptr.repaired.answer.h", "out/header_null_ptr.h")

    test_runner.cleanup(source_file, out_location=out_src_dir, step_dir=step_dir, repair_includes_mode=repair_includes_mode, additional_files="out/header_null_ptr.h out/header_null_ptr.c")
    os.chdir("..")
    test_runner.cleanup(source_file, out_location=out_src_dir, step_dir=step_dir, repair_includes_mode=repair_includes_mode)
    test_runner.dir_final_cleanup(step_dir, step_dir_prev_existed=step_dir_prev_existed)
    os.chdir(cur_dir)

def test_07():
    out_ast_file = "out/preproc_parser_2.ear-out.json"
    source_filename = "preproc_parser_2.c"
    source_file_contents = read_whole_file_as_bytes(source_filename)
    os.system("rm -f " + out_ast_file)
    ear.run_ear_for_source_file(
        ast_file=out_ast_file,
        source_file=source_filename)
    assert cmp_file_normalize("preproc_parser_2.ear-out.answer.json", out_ast_file, relativize_paths)
    ast = read_json_file(out_ast_file)
    def get_single_value(d):
        view = d.values()
        assert(len(view) == 1)
        return [x for x in view][0]
    preproc_db = get_single_value(ast['preproc_db'])
    comments = get_single_value(ast['comments_db'])
    assert(len(preproc_db) > 0)
    assert(len(comments) > 0)
    for i in preproc_db:
        assert(source_file_contents[i:i+1] == b"#")
    for (start, end) in comments:
        is_valid_comment = (
            (source_file_contents[start:start+2] == b"/*" and source_file_contents[end-2:end] == b"*/") or
            (source_file_contents[start:start+2] == b"//" and source_file_contents[end-1:end] == b"\n"))
        assert(is_valid_comment)
    test_runner.cleanup(source_filename, out_location="out", step_dir="out", additional_files="out/preproc_parser_2.ear-out.json")

def test_e2e_013():
    os.system("rm -f out/macros_near_null_checks*.*")
    #os.system("cd ..; ./end_to_end_acr.py --repaired-src test/out --step-dir test/out test/macros_near_null_checks.c autogen test/macros_near_null_checks.alerts.json")
    source_file="test/macros_near_null_checks.c"
    compile_commands="autogen"
    alerts="test/macros_near_null_checks.alerts.json"
    step_dir="test/out"
    out_src_dir="test/out"
    cur_dir = os.getcwd()
    os.chdir("..")
    try:
        end_to_end_acr.run(
            source_file=source_file,
            compile_commands=compile_commands,
            alerts=alerts,
            step_dir=step_dir,
            out_src_dir=out_src_dir)
    finally:
        os.chdir(cur_dir)
    assert cmp_file_normalize("macros_near_null_checks.brain-out.json",  "out/macros_near_null_checks.brain-out.json")
    assert cmp_file_normalize("macros_near_null_checks.repaired.c",     "out/macros_near_null_checks.c")
    test_runner.cleanup(source_file, out_location=out_src_dir, step_dir=step_dir, additional_files="out/macros_near_null_checks.* out/acr.h")

def test_e2e_arrow_null_01():
    if(os.path.exists("out")):
        step_dir_prev_existed = True
    else:
        step_dir_prev_existed = False
    os.system("rm -f out/arrow_null_01*.*")
    source_file="arrow_null_01.c"
    compile_commands="autogen"
    alerts="arrow_null_01.alerts.json"
    step_dir="out"
    out_src_dir="out"
    end_to_end_acr.run(
        source_file=source_file,
        compile_commands=compile_commands,
        alerts=alerts,
        step_dir=step_dir,
        out_src_dir=out_src_dir)
    assert cmp_file_normalize("arrow_null_01.repaired.c", "out/arrow_null_01.c")
    print("source_file: ", source_file)
    fixed_c_file = out_src_dir+"/"+source_file
    print("fixed_c_file: ", fixed_c_file)
    test_runner.cleanup(source_file, out_location=out_src_dir, test_results_filepath=fixed_c_file, step_dir=step_dir)
    test_runner.dir_final_cleanup(out_src_dir, step_dir_prev_existed=step_dir_prev_existed)

def test_header_in_subdir_a():
    os.system("rm -rf out/header_in_subdir out/header_in_subdir.c")
    os.system("mkdir out/header_in_subdir")
    step_dir_prev_existed = False
    compile_commands="autogen"
    alerts="header_in_subdir.alerts.json"
    source_file="header_in_subdir.c"
    step_dir="out"
    out_src_dir="out"
    repair_includes_mode=True
    end_to_end_acr.run(
        compile_commands=compile_commands,
        alerts=alerts,
        source_file=source_file,
        step_dir=step_dir,
        out_src_dir=out_src_dir,
        repair_includes_mode=repair_includes_mode)
    assert cmp_file_normalize("header_in_subdir.repaired.c", "out/header_in_subdir.c")
    assert cmp_file_normalize("header_in_subdir.repaired.h", "out/header_in_subdir/header.h")
    fixed_c_file = out_src_dir+"/"+source_file
    test_runner.cleanup(source_file, out_location=out_src_dir, test_results_filepath=fixed_c_file, step_dir=step_dir, repair_includes_mode=repair_includes_mode)
    test_runner.dir_final_cleanup("out/header_in_subdir", False)


def test_header_in_subdir_b():
    os.system("rm -rf out/header_in_subdir")
    os.system("cp -rp header_in_subdir.c header_in_subdir out/")
    compile_commands="autogen"
    alerts="header_in_subdir.alerts.json"
    source_file="out/header_in_subdir.c"
    step_dir="out"
    base_dir="out"
    repair_includes_mode=True
    repair_in_place=True
    end_to_end_acr.run(
        compile_commands=compile_commands,
        alerts=alerts,
        source_file=source_file,
        step_dir=step_dir,
        base_dir=base_dir,
        repair_includes_mode=repair_includes_mode,
        repair_in_place=repair_in_place)
    assert cmp_file_normalize("header_in_subdir.repaired.c", "out/header_in_subdir.c")
    assert cmp_file_normalize("header_in_subdir.repaired.h", "out/header_in_subdir/header.h")
    fixed_c_file = source_file
    test_runner.cleanup(source_file, out_location=step_dir, test_results_filepath=fixed_c_file, step_dir=step_dir, repair_includes_mode=repair_includes_mode, repair_in_place=repair_in_place, base_dir=base_dir)
    test_runner.dir_final_cleanup("out/header_in_subdir", False)

def test_super01_normal():
    os.system("rm -f out/super01*.*")
    compile_cmds_file="super01_compile_cmds.json"
    alerts="super01.alerts.json"
    step_dir="out"
    base_dir="."
    combined_brain_out="out/super01.combined-brain.json"
    sup.run(
        compile_cmds_file=compile_cmds_file,
        alerts=alerts,
        step_dir=step_dir,
        base_dir=base_dir,
        combined_brain_out=combined_brain_out)

    assert cmp_file_normalize("super01.normal.combined-brain.json", "out/super01.combined-brain.json")
    test_runner.cleanup(base_dir, out_location=step_dir, test_results_filepath="out", step_dir=step_dir, base_dir=base_dir, additional_files="out/super01*.*")

def test_super01_smell_check():
    os.system("rm -f out/super01*.*")
    # This test injects a modified version of the brain-module output,
    # to test that conflicting repairs are detected.
    compile_cmds_file="super01_compile_cmds.json"
    alerts="super01.alerts.json"
    step_dir="out"
    base_dir="."
    combined_brain_out="out/super01.combined-brain.json"
    inject_brain_output=True
    os.system("cp super01b.tu1.brain-out.smell_check.json out/super01b.tu1.brain-out.json")
    sup.run(
        compile_cmds_file=compile_cmds_file,
        alerts=alerts,
        step_dir=step_dir,
        base_dir=base_dir,
        combined_brain_out=combined_brain_out,
        inject_brain_output=True)
    
    assert cmp_file_normalize("out/super01.combined-brain.json", "super01.smell-check.combined-brain.json")
    test_runner.cleanup(base_dir, out_location=step_dir, test_results_filepath="out", step_dir=step_dir, base_dir=base_dir, additional_files="out/super01*.*")

def test_super01_bothstars():
    os.system("rm -f out/super01*.*")
    # This test injects a modified version of the brain-module output,
    # to test that the conflicting-repair detector isn't too aggressive.
    compile_cmds_file="super01_compile_cmds.json"
    alerts="super01.alerts.json"
    step_dir="out"
    base_dir="."
    combined_brain_out="out/super01.combined-brain.json"
    inject_brain_output=True
    os.system("cp super01a.tu0.brain-out.bothstars.json out/super01a.tu0.brain-out.json")
    sup.run(
        compile_cmds_file=compile_cmds_file,
        alerts=alerts,
        step_dir=step_dir,
        base_dir=base_dir,
        combined_brain_out=combined_brain_out,
        inject_brain_output=inject_brain_output)
    
    assert cmp_file_normalize("out/super01.combined-brain.json", "super01.bothstars.combined-brain.json")
    test_runner.cleanup(base_dir, out_location=step_dir, test_results_filepath="out", step_dir=step_dir, base_dir=base_dir, additional_files="out/super01*.*")

def test_dom_null_derefs():
    os.system("rm -f out/dom_null_derefs*.*")
    alerts="dom_null_derefs.alerts.json"
    step_dir="out"
    base_dir="."
    end_to_end_acr.run(
        source_file="dom_null_derefs.c",
        compile_commands="autogen",
        alerts=alerts,
        step_dir=step_dir,
        out_src_dir=step_dir)
    
    assert cmp_file_normalize("dom_null_derefs.nulldom.json", "out/dom_null_derefs.nulldom.json")
    assert cmp_file_normalize("dom_null_derefs.brain-out.json", "out/dom_null_derefs.brain-out.json")
    if os.getenv('pytest_keep') != "true":
        os.system("rm -f out/dom_null_derefs*.*")

def test_already_repaired():
    os.system("rm -f out/already_repaired_null_01.*")
    alerts="already_repaired_null_01.alerts.json"
    step_dir="out"
    base_dir="."
    end_to_end_acr.run(
        source_file="already_repaired_null_01.c",
        compile_commands="autogen",
        alerts=alerts,
        step_dir=step_dir,
        out_src_dir=step_dir)
    assert cmp_file_normalize("already_repaired_null_01.brain-out.json", "out/already_repaired_null_01.brain-out.json")
    if os.getenv('pytest_keep') != "true":
        os.system("rm -f out/already_repaired_null_01.*")

def test_in_range():
    import is_indep
    is_indep.test_in_range()

def test_uninit_variable_clangtidy_false_positive():
    os.system("rm -f out/uninit_variable_clangtidy_fp*.*")
    alerts="uninit_variable_clangtidy_fp.alerts.json"
    step_dir="out"
    base_dir="."
    end_to_end_acr.run(
        source_file="uninit_variable_clangtidy_fp.c",
        compile_commands="autogen",
        alerts=alerts,
        step_dir=step_dir,
        out_src_dir=step_dir)
    assert cmp_file_normalize("uninit_variable_clangtidy_fp.brain-out.json", "out/uninit_variable_clangtidy_fp.brain-out.json")
    if os.getenv('pytest_keep') != "true":
        os.system("rm -f out/uninit_variable_clangtidy_fp*.*")

def test_already_repaired_null_01():
    os.system("rm -f out/already_repaired_null_01.*")
    alerts="already_repaired_null_01.alerts.json"
    step_dir="out"
    base_dir="."
    end_to_end_acr.run(
        source_file="already_repaired_null_01.c",
        compile_commands="autogen",
        alerts=alerts,
        step_dir=step_dir,
        out_src_dir=step_dir)
    assert cmp_file_normalize("already_repaired_null_01.brain-out.json", "out/already_repaired_null_01.brain-out.json")
    if os.getenv('pytest_keep') != "true":
        os.system("rm -f out/already_repaired_null_01.*")
