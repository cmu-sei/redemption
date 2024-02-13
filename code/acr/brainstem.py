
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

import sys, os, re, pdb, argparse, json
from collections import OrderedDict, defaultdict

from util import *

# FIXME: Ugly hack...we should be getting Clang to provide this info in the JSON
def get_function_return_type(node):
    t = node["type"]["qualType"]
    return t[0:t.find("(")].strip()

# FIXME: Ugly hack...we should be getting Clang to provide this info in the JSON
def is_integral_type(t):
    return t in ["int", "unsigned int"]

# FIXME: Ugly hack...we should be getting Clang to provide this info in the JSON
def is_void(t):
    return t == "void"

# FIXME: Ugly hack...we should be getting Clang to provide this info in the JSON
def is_pointer_type(t):
    return t.endswith("*")


# Identify integers and NULL
def identify_expr(node):
    if node["kind"] == "ImplicitCastExpr":
        return identify_expr(node["inner"][0])
    if node['kind'] == 'IntegerLiteral':
        return node["value"]
    if node["kind"] == "UnaryOperator" and node["opcode"] == "-" and \
       node["inner"][0]["kind"] == "IntegerLiteral":
      return "-" + identify_expr(node["inner"][0])
    return node

class Brainstem(AstVisitor):
    def __init__(self):
        AstVisitor.__init__(self)
        self.error_handling_db = dict()

    def visit_FunctionDecl(self, node):
        self.handle_functions(node)
    def visit_CXXMethodDecl(self, node):
        self.handle_functions(node)
    def handle_functions(self, node):
        if "inner" not in node:
            return
        d = dict();
        d["name"] = node["name"]
        return_type = get_function_return_type(node)
        self._return_exps = list();

        self.visitdefault(node)

        return_others = list()
        if len(self._return_exps) > 0:
            return_last = self._return_exps.pop(-1)
            if len(self._return_exps) > 0:
                return_others = self._return_exps

        error_handler = None
        if is_pointer_type(return_type) and "0" in return_others:
            error_handler = "return NULL"
        if is_integral_type(return_type) and "0" in return_others:
            error_handler = "return 0"
        if is_integral_type(return_type) and "-1" in return_others:
            error_handler = "return -1"
        if is_void(return_type) and None in return_others:
            error_handler = "return"
        if error_handler is not None:
            d["error_handler"] = error_handler

        self.error_handling_db[node['id']] = d

    def visit_ReturnStmt(self, node):
        if "inner" in node:
            expr = identify_expr(node["inner"][0])
        else:
            expr = None
        self._return_exps.append(expr)


def parse_args():
    parser = argparse.ArgumentParser(description='Produces error-handling strategies for each function in AST')
    parser.add_argument('ast_file', type=str, help="Clang AST from the Ear module (in JSON format)")
    parser.add_argument('-o', type=str, metavar="OUTPUT_FILE", dest="output_filename", required=True, help="Output filename")
    cmdline_args = parser.parse_args()
    return cmdline_args

def run(ast_file, output_filename):
    if os.getenv('acr_emit_invocation'):
        print(f"brainstem.py -o {output_filename} {ast_file}")
    ast = read_json_file(ast_file)
    brainstem = Brainstem()
    brainstem.visit(ast)
    with open(output_filename, 'w') as outfile:
        outfile.write(json.dumps(brainstem.error_handling_db, indent=2) + "\n")

if __name__ == "__main__":
    run(**vars(parse_args()))
