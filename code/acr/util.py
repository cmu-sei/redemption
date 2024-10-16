
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

import sys, os, re, pdb, argparse, json, traceback
import time
import gzip
from pathlib import Path

__all__ = ['json', 'stop', 'read_whole_file', 'read_file_range', 'get_dict_path', 'set_dict_path', 'setdefault_dict_path', 'print_progress', 'set_progress_prefix', 'condense_json_int_pairs', 'strip_filename_extension', 'get_ast_file_base', 'is_nonzero_file', 'is_newer_file', 'AstVisitor']

stop = pdb.set_trace

def read_whole_file(filename, mode_mod=""):
    if Path(filename).suffix == ".gz":
        fn_open = gzip.open
    else:
        fn_open = open
    with fn_open(filename, 'r'+mode_mod) as the_file:
        return the_file.read()

def read_file_range(filename, begin_offset, end_offset):
    with open(filename, 'rb') as file:
        file.seek(begin_offset)
        return file.read(end_offset - begin_offset)

def get_dict_path(dictionary, *keys, default=None):
    """Return the value for a list of keys in a recursive dictionary.

    If a key does not exist, return the value of 'default'.
    """
    try:
        for key in keys:
            dictionary = dictionary[key]
        return dictionary
    except KeyError:
        return default

def set_dict_path(dictionary, *args):
    """Set a value for a list of keys in a recursive dictionary.

    When a key does not exist, create a dictionary for it.  The last
    value in 'args' is the value to set.  Returns the value that was set.
    """
    keys = args[:-1]
    value = args[-1]
    for key in keys[:-1]:
        dictionary = dictionary.setdefault(key, dict())
    dictionary[keys[-1]] = value
    return value

def setdefault_dict_path(dictionary, *args):
    """Set a value for a list of keys in a recursive dictionary if it is not already set.

    If a value already exists, return it.  Otherwise, set as in 'set_dict_path'.
    """
    keys = args[:-1]
    value = args[-1]
    for key in keys[:-1]:
        dictionary = dictionary.setdefault(key, dict())
    return dictionary.setdefault(keys[-1], value)

env_var__show_progress = (os.getenv('acr_show_progress') == "true")
program_start_time = time.time()

def print_progress(msg):
    if env_var__show_progress:
        elapsed_time = time.time() - program_start_time
        prefix = print_progress.prefix or ""
        print("[%6.2f sec] %s%s" % (elapsed_time, prefix, msg))

def set_progress_prefix(value):
    print_progress.prefix = value

set_progress_prefix(None)

def condense_json_int_pairs(s):
    return re.sub("(\n *)\\[\n *([0-9]+),\n *([0-9]+)\n *\\]", "\\1[\\2, \\3]", s, re.MULTILINE)

def strip_filename_extension(filename):
    return os.path.splitext(filename)[0]

def get_ast_file_base(ast_file):
    # TODO: some test files are still using the old command-line arguments; fix this.
    #assert ast_file.endswith(".ear-out.json"), ast_file
    is_okay = re.search("[.][^.]*[.]json(.gz)?$", ast_file)
    if not is_okay:
        traceback.print_stack()
        sys.stderr.write("\nBad filename: %r\n" % ast_file)
        sys.stderr.write("Expecting something like: 'path/foo.ear-out.json'\n")
        sys.exit(1)
    ast_file_base = ast_file
    ast_file_base = re.sub("[.]answer[.]json(.gz)?$", ".json", ast_file_base)
    ast_file_base = re.sub("[.][^.]*[.]json(.gz)?$", "", ast_file_base)
    return ast_file_base

def is_nonzero_file(filename):
    return (os.path.isfile(filename) and os.path.getsize(filename) > 0)

def is_newer_file(file1, file2):
    return os.path.getmtime(file1) > os.path.getmtime(file2)

# NOTE: when subclassing this pattern, if you create a visitor method,
# such as visit_FunctionDecl, then this visitor will no longer visit
# subnodes of any such node.  If you want the visitor to still visit
# these subnodes, your visitor method should invoke:
#
#           self.visitdefault(node)
#
# Clearly, you can put this in the middle of your function, in order
# to do stuff both before and after visiting subnodes.
class AstVisitor(object):
    def __init__(self):
        self.node_stack = []
        self.func_name = None
        self.file_name = None
        self.cur_line = None
        self.src = None

    def previsit(self, node):
        pass

    def visit(self, node):
        match node:
            case [*_]:
                return [self.visit(x) for x in node]
            case None:
                return node
            case {'kind': node_type}:
                #print("Visiting " + node_type)
                fn_visit = getattr(type(self), "visit_" + node_type,
                    lambda _, x: self.visitdefault(x))

                loc_file = None

                match node:
                    case {'range': {'file': f}} | {'loc': {'file': f}}:
                        loc_file = f

                if loc_file:
                    #old_file = self.file_name
                    self.file_name = loc_file
                    #print("filename: " + loc_file)

                #old_line = None
                match node:
                    case {"range": {"begin": ({"line": line}
                                              | {"expansionLoc": {"line": line}})}}:
                        self.cur_line = line

                self.node_stack.append(node)
                try:
                    self.previsit(node)
                    ret = fn_visit(self, node)
                finally:
                    self.node_stack.pop()

                return ret

            case _:
                return node

    def visitdefault(self, node):
        return dict([(k, self.visit(v)) for (k,v) in node.items()])
