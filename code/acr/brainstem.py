
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
from make_run_clang import read_json_file
from dataclasses import dataclass

import json

###############################################################################
#
# Utilize Clang Modifications
#
###############################################################################

@dataclass
class FunctionStruct:
    realType: str
    isIntegralType: bool
    isVoidType: bool
    isPointerType: bool
    isSigned: bool
    isFloatingType: bool

# moves through all the qualDetails to combine them into a
# single array
def combine_qual_details(node):
    combined_details = []

    def recursive_collect(details_node):
        if 'qualDetails' in details_node:
            combined_details.extend(details_node['qualDetails'])
        for key, value in details_node.items():
            if isinstance(value, dict):
                recursive_collect(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        recursive_collect(item)

    recursive_collect(node)
    return combined_details

def get_deepest_qual_type(node):
    def recursive_search(current_node, current_depth):
        if 'qualType' in current_node and isinstance(current_node['qualType'], dict):
            # There is a nested qualType, dive deeper
            return recursive_search(current_node['qualType'], current_depth + 1)
        elif 'type' in current_node and isinstance(current_node['type'], dict):
            # There is a nested type, dive deeper
            return recursive_search(current_node['type'], current_depth + 1)
        else:
            # No more nested qualType or type, return this node and depth
            return current_node, current_depth

    result_node, depth = recursive_search(node, 0)
    return result_node

# the return type may be nested
def get_function_return_type(node):

    # a referencedDecl may not contain returnTypeDetail
    # despite containing FunctionDecl
    # "referencedDecl": {
    # "id": "0x556a9629d560",
    # "kind": "FunctionDecl",
    # "name": "puts",
    # "type": {
    #     "qualType": "int (const char *)"
    #   }
    # }
    if "returnTypeDetail" not in node:
        return None

    qual_details = combine_qual_details(node["returnTypeDetail"])
    return_type = FunctionStruct(
        isIntegralType="integer" in qual_details,
        isVoidType="void" in qual_details,
        isPointerType="ptr" in qual_details,
        isSigned="signed" in qual_details,
        isFloatingType="fpp" in qual_details,
        realType=get_deepest_qual_type(node["returnTypeDetail"])
    )

    return return_type

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

###############################################################################
#
# Utilize Unmodified Clang
#
###############################################################################

brainstem_pointer_regex = re.compile(r"(?:\*|\(\*\)\(.*\)(?: ?[a-z_]+)*)$", re.I)

# Legacy: uses unmodified version of clang
def get_function_return_type_legacy(node):
    t = node["type"]["qualType"]
    return t[0:t.find("(")].strip()

# Legacy: uses unmodified version of clang
def is_integral_type_legacy(t):
    return t in ["int", "unsigned int"]

# Legacy: uses unmodified version of clang
def is_void_legacy(t):
    return t == "void"

# Legacy: uses unmodified version of clang
def is_pointer_type_legacy(t):
    return bool(brainstem_pointer_regex.search(t))

###############################################################################
#
# The Brainstem class 
#
# will switch between the unmodified and modified 
# depending on what characteristics are found in the AST
###############################################################################

class Brainstem(AstVisitor):
    def __init__(self):
        AstVisitor.__init__(self)
        self.error_handling_db = dict()

    def visit_FunctionDecl(self, node):
        self.handle_functions(node)
    def visit_CXXMethodDecl(self, node):
        self.handle_functions(node)
    def handle_functions(self, node):
        d = dict()
        d["name"] = node["name"]

        # assumes the modified version of clang
        # we need to run a check to ensure AST compatibility.
        return_type = get_function_return_type(node)

        # verify node contains a return result
        if return_type is None:
            self.handle_function_legacy(node)
            return

        self._return_exps = list()

        self.visitdefault(node)

        return_others = list()
        if len(self._return_exps) > 0:
            return_last = self._return_exps.pop(-1)
            if len(self._return_exps) > 0:
                return_others = self._return_exps

        error_handler = None
        if return_type.isPointerType and "0" in return_others:
            error_handler = "return NULL"
        elif return_type.isIntegralType:
            if "-1" in return_others:
                error_handler = "return -1"
            elif "0" in return_others:
                error_handler = "return 0"
        if error_handler is not None:
            d["error_handler"] = error_handler

        self.error_handling_db[node['id']] = d

    def visit_ReturnStmt(self, node):
        if "inner" in node:
            expr = identify_expr(node["inner"][0])
        else:
            expr = None
        self._return_exps.append(expr)

    def handle_function_legacy(self, node):
        """
        Will attempt to provide some information based on the hacks that were in place
        before the Clang AST output was modified. This should only be called whenever 
        the other handle_function function fails.
        """
        if "inner" not in node:
            return
        
        d = dict()
        d["name"] = node["name"]

        return_type = get_function_return_type(node)
        self._return_exps = list()

        self.visitdefault(node)

        return_others = list()
        if len(self._return_exps) > 0:
            return_last = self._return_exps.pop(-1)
            if len(self._return_exps) > 0:
                return_others = self._return_exps

        error_handler = None
        if is_pointer_type_legacy(return_type) and "0" in return_others:
            error_handler = "return NULL"
        if is_integral_type_legacy(return_type) and "0" in return_others:
            error_handler = "return 0"
        if is_integral_type_legacy(return_type) and "-1" in return_others:
            error_handler = "return -1"
        if is_void_legacy(return_type) and None in return_others:
            error_handler = "return"
        if error_handler is not None:
            d["error_handler"] = error_handler

        self.error_handling_db[node['id']] = d

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
