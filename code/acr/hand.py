
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

class Hand(AstVisitor):
    def __init__(self):
        AstVisitor.__init__(self)
        self.alerts_by_ast_id = None
        self.seen_files = set()
        self.missing_ast_alerts = []
        self.var_decls_by_id = {}

    def previsit(self, node):
        if node["kind"] == "VarDecl":
            self.var_decls_by_id[node["id"]] = node
        self.seen_files.add(self.file_name)

    def visitdefault(self, node):
        if 'id' in node:
            for alert in self.alerts_by_ast_id[node['id']]:
                (func_name, kwargs) = alert["repair_algo"]
                fn_repair = getattr(Hand, func_name)
                fn_repair(self, node, alert, **kwargs)
        return dict([(k, self.visit(v)) for (k,v) in node.items()])

    def add_null_check(self, node, alert, whole_expr=False, handle_error=None):
        if whole_expr:
            ptr_subexpr = node
        elif node.get('opcode') == '*':
            ptr_subexpr = node["inner"][0]
        elif node["kind"] == "ArraySubscriptExpr":
            ptr_subexpr = node["inner"][0]
            if not is_expr_of_ptr_type(ptr_subexpr) and is_expr_of_ptr_type(node["inner"][1]):
                ptr_subexpr = node["inner"][1]
        elif node["kind"] == "MemberExpr" and node["isArrow"]:
            ptr_subexpr = node["inner"][0]
        else:
            raise Exception("Unrecognized node passed to add_null_check, and whole_expr isn't true.")
        byte_start = ptr_subexpr['range']['begin']['offset'] - 1
        byte_end = ptr_subexpr['range']['end']['offset'] + ptr_subexpr['range']['end']['tokLen']

        if handle_error is not None:
            closer = ", " + handle_error + ")"
        else:
            closer = ")"
        edit = [self.file_name, [
            [byte_start+1, byte_start+1, "null_check("],
            [byte_end, byte_end, closer]]]
        alert["patch"] = [edit]

    def initialize_var(self, node, alert, decl_id):
        node = self.var_decls_by_id.get(decl_id)
        init_val = "0"
        if node["type"]["qualType"].endswith("*"):
            if self.file_name.endswith(".cpp"):
                init_val = "nullptr"
            else:
                init_val = "NULL"
        elif node["type"].get("desugaredQualType","").startswith(("struct","union")):
            init_val = "{}"
        try:
            byte_end = node['range']['end']['offset'] + node['range']['end']['tokLen']
        except KeyError:
            alert["why_skipped"] = "AST node is missing range offset information"
            alert["patch"] = []
            return
        edit = [self.file_name, [
            [byte_end, byte_end, " = " + init_val]]]
        alert["patch"] = [edit]

    def del_unused_asgn(self, node, alert, asgn_id):
        asgn = self.node_stack[-2]
        assert(asgn["id"] == asgn_id)
        try:
            del_begin = node["range"]["begin"]["offset"]
            del_end = asgn["inner"][1]["range"]["begin"]["offset"]
        except KeyError:
            alert["why_skipped"] = "KeyError"
            alert["patch"] = []
            return
        edit = [self.file_name, [[del_begin, del_end, "(void) "]]]
        alert["patch"] = [edit]

    def repair_deadinit_var(self, node, alert, decl_id):
        node = None
        decl_node = self.var_decls_by_id.get(decl_id)
        try:
            filename = decl_node["range"]["file"]
            begin_offset = decl_node["loc"]["offset"]
            end_offset = decl_node["range"]["end"]["offset"] + decl_node["range"]["end"]["tokLen"]
        except KeyError:
            alert["why_skipped"] = "KeyError"
            alert["patch"] = []
            return
        decl_text = read_file_range(filename, begin_offset, end_offset)
        m = re.search(b"( *=)", decl_text)
        if not m:
            alert["why_skipped"] = "No assignment '=' found!"
            alert["patch"] = []
        del_start = begin_offset + m.span()[0]
        edit = [self.file_name, [[del_start, end_offset, ""]]]
        alert["patch"] = [edit]

    def msc12c(self, node, alert):
        alert["why_skipped"] = "not implemented yet"
        alert["patch"] = []

    def skip(self, node, alert, why):
        alert["why_skipped"] = why
        alert["patch"] = []

    def parse_alerts(self, alerts_filename):
        self.alert_list = read_json_file(alerts_filename)
        self.alerts_by_ast_id = defaultdict(lambda: list())
        for cur_alert in self.alert_list:
            ast_id = cur_alert.get('ast_id')
            if ast_id:
                self.alerts_by_ast_id[ast_id].append(cur_alert)
            else:
                self.missing_ast_alerts.append(cur_alert)
                cur_alert["patch"] = []

def is_expr_of_ptr_type(ast_node):
    return ast_node["type"]["qualType"].endswith("*")

def parse_args():
    parser = argparse.ArgumentParser(description='Repairs source-code AST')
    parser.add_argument("ast_file", type=str, help="Clang AST, as modified by the Brain module (in JSON format)")
    parser.add_argument('-o', type=str, metavar="OUTPUT_FILE", dest="output_filename", required=True, help="Output filename")
    parser.add_argument('-a', type=str, metavar="ALERTS_FILE", dest="alerts_filename", required=True, help="Static-analysis alerts")
    cmdline_args = parser.parse_args()
    return cmdline_args


def main():
    cmdline_args = parse_args()
    run(**vars(cmdline_args))

def run(ast_file, alerts_filename, output_filename, warn_missing=False):
    if os.getenv('acr_emit_invocation'):
        print(f"hand.py -o {output_filename} -a {alerts_filename} {ast_file}")
    ast = read_json_file(ast_file)
    hand = Hand()
    env_warn_missing = os.getenv('acr_warn_unlocated_alerts')
    if env_warn_missing:
        if env_warn_missing.lower() == "true":
            warn_missing = True
        elif env_warn_missing.lower() == "false":
            warn_missing = False
        else:
            print("Bad value for environment variable 'acr_warn_unlocated_alerts'!")
    hand.warn_missing = warn_missing
    hand.parse_alerts(alerts_filename)
    hand.visit(ast)
    if warn_missing:
        missing_files = set()
        for cur_alert in hand.missing_ast_alerts:
            if cur_alert["file"] in hand.seen_files:
                print("Warning: Missing ast_id for alert %r!" % cur_alert.get("alert_id"))
            else:
                missing_files.add(cur_alert["file"])
        if missing_files:
            print("Unseen files with alerts: " + repr(list(sorted(missing_files))))

    with open(output_filename, 'w') as outfile:
        outfile.write(json.dumps(hand.alert_list, indent=2) + "\n")

if __name__ == "__main__":
    main()
