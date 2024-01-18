
# <legal>
# 'Redemption' Automated Code Repair Tool
# 
# Copyright 2023 Carnegie Mellon University.
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
import subprocess

from util import *
from is_indep import is_indep_of_cond_directives
from brainstem import Brainstem

class Brain(AstVisitor):
    def __init__(self, ast):
        AstVisitor.__init__(self)
        self.alerts_by_line = None
        self.alerts_by_lc = None
        self.preproc_db = ast["preproc_db"]
        self.base_dir = ast["base_dir"]
        self.compile_dir = ast["compile_dir"]
        self.uninit_vars = {}
        self.var_decls_by_id = {}
        self.enable_msc12 = ((os.getenv('REPAIR_MSC12') or "").lower() != "false")

        brainstem = Brainstem();
        brainstem.visit(ast)
        self.error_handling_db = brainstem.error_handling_db

    def check_repairability(self, alert, node):
        # Note: We need to check in_macro_at_{start,end} before calling
        # is_indep_of_cond_directives since
        # is_indep_of_cond_directives throws a KeyError if inside a macro.
        def in_base_dir(pathname):
            return pathname.startswith(self.base_dir + "/")
        if not in_base_dir(self.file_name):
            mark_skipped_alert(alert, "Outside of base_dir")
            return
        if not is_indep_of_macros(node, alert):
            return
        if not is_indep_of_cond_directives(node, self.preproc_db[self.file_name]):
            mark_skipped_alert(alert, "Contains preprocessor directives")
            return

    def previsit(self, node):
        if node["kind"] == "VarDecl":
            self.var_decls_by_id[node["id"]] = node
        def get_node_begin_col(node):
            try:
                return node["range"]["begin"]["col"]
            except:
                pass
            try:
                return node["range"]["begin"]["expansionLoc"]["col"]
            except:
                pass
            return None
        def get_node_loc_col(node):
            try:
                return node["loc"]["col"]
            except:
                return None
        col = get_node_begin_col(node)
        if col is None:
            return
        try:
            alerts_by_rule_id = self.alerts_by_lc[self.file_name][self.cur_line][col]
        except KeyError:
            return
        ###
        alert = alerts_by_rule_id.get("EXP33-C")
        if not alert:
            try:
                alert = self.alerts_by_lc[self.file_name][self.cur_line][get_node_loc_col(node)]["EXP33-C"]
            except:
                pass
        if alert:
            if self.try_uninit_var_repair(node, alert):
                alert["ast_id"] = node['id']
                self.check_repairability(alert, node)
        #
        alert = alerts_by_rule_id.get("MSC12-C")
        def try_msc12():
            alert["ast_id"] = node['id']
            if not self.enable_msc12:
                alert["repair_algo"] = ["skip", {"why": ["Repair of MSC12-C is disabled; set env var REPAIR_MSC12=true to enable it."]}]
                return
            alert["repair_algo"] = ["msc12c", {}]
            
            try:
                macro_file = node['range']['begin']['spellingLoc']['file']
            except KeyError:
                macro_file = None
            if macro_file and macro_file.endswith("/assert.h"):
                mark_skipped_alert(alert, "False positive: inside an assert")
                return
            if self.try_deadinit_var_repair(node, alert):
                self.check_repairability(alert, node)
                return
            if alert.get("checker", "").startswith("uselessAssignment"):
                if node["kind"] != "DeclRefExpr":
                    return
                asgn = self.node_stack[-2]
                if asgn["kind"] != "BinaryOperator" or not asgn["opcode"].startswith("="):
                    return
                self.check_repairability(alert, node)
                if is_skipped_alert(alert):
                    return
                alert["repair_algo"] = ["del_unused_asgn", {"asgn_id":asgn["id"]}]
                return
                
            self.check_repairability(alert, node)

        if alert:
            try_msc12()
        ###
        alert = alerts_by_rule_id.get("EXP34-C")
        if alert:
            self.try_null_ptr_repair(node, alert, whole_expr=True)

    def get_alert_at_cursor(self, alert_rule_id):
        try:
            alert = self.alerts_by_line[self.file_name][self.cur_line][alert_rule_id]
        except KeyError:
            alert = None
        return alert

    def get_error_handler_at_cursor(self):
        fn_decl_node = self.get_enclosing_function()
        try:
            eh = self.error_handling_db[fn_decl_node["id"]]["error_handler"]
            error_handler = {"handle_error": eh}
        except:
            error_handler = dict()
        return error_handler

    def get_decl_of_var(self, node):
        if node["kind"] == "VarDecl":
            return node
        if node["kind"] != "DeclRefExpr":
            return None
        decl_id = node.get("referencedDecl",{}).get("prevId")
        if not decl_id:
            return None
        decl_node = self.var_decls_by_id.get(decl_id)
        if not decl_node:
            return None
        return decl_node

    def try_uninit_var_repair(self, node, alert):
        def get_uninit_var_name(alert):
            message = alert.get("message","")
            m = re.match("variable '([^']*)' is not initialized", message)
            if m:
                return m.group(1)
            m = re.match("Uninitialized variable: (.*)", message)
            if m:
                return m.group(1)
            return None
        var = get_uninit_var_name(alert)
        if var:
            decl_node = self.get_decl_of_var(node)
            if not decl_node:
                return False
            alert["repair_algo"] = ["initialize_var", {"decl_id": decl_node["id"]}]
            return True
        else:
            return False

    def try_deadinit_var_repair(self, node, alert):
        def get_deadinit_var_name(alert):
            message = alert.get("message","")
            m = re.match("^Redundant initialization for '([^']*)'.*", message)
            if m:
                return m.group(1)
            return None
        var = get_deadinit_var_name(alert)
        if var:
            decl_node = self.get_decl_of_var(node)
            if not decl_node:
                return False
            alert["repair_algo"] = ["repair_deadinit_var", {"decl_id": decl_node["id"]}]
            return True
        else:
            return False

    def try_null_ptr_repair(self, node, alert=None, whole_expr=False):
        if alert is None:
            alert = self.get_alert_at_cursor("EXP34-C")
        match alert:
            case None:
                return
            case {'repair_algo': [_, _]} if not whole_expr:
                return
            case {'tool': 'rosecheckers',
              'repair_algo': ['add_null_check', {"whole_expr": True}]}:
                # If we've already repaired this as a whole_expr, stop
                return
        message = alert.get("message","")
        m = re.match("Null pointer passed to ([0-9]+).. parameter", message)
        if m:
            if node.get("kind") != "CallExpr":
                return
            param_ordinal = int(m.group(1))
            node = node["inner"][param_ordinal]
        kwargs = self.get_error_handler_at_cursor()
        kwargs["whole_expr"] = whole_expr
        alert["ast_id"] = node['id']
        alert["repair_algo"] = ["add_null_check", kwargs]
        self.check_repairability(alert, node)

    def visit_UnaryOperator(self, node):
        if node['opcode'] == '*':
            self.try_null_ptr_repair(node)
        self.visitdefault(node)

    def visit_ArraySubscriptExpr(self, node):
        self.try_null_ptr_repair(node)
        self.visitdefault(node)

    def visit_MemberExpr(self, node):
        if node["isArrow"]:
            self.try_null_ptr_repair(node)
        self.visitdefault(node)

    def get_enclosing_function(self):
        for node in reversed(self.node_stack):
            if isinstance(node, dict) and node["kind"] == "FunctionDecl":
                return node;
        return None

    def parse_alerts(self, alerts_filename):
        self.alert_list = read_json_file(alerts_filename)
        self.alerts_by_line = {}
        self.alerts_by_lc = {}
        cur_alert_id = 1
        for a in self.alert_list:
            if not a['file'].startswith("/"):
                # Relative pathnames in the Alerts file are considered to be
                # relative to the base_dir.
                a['file'] = os.path.join(self.base_dir, a['file'])
            a['file'] = os.path.realpath(a['file'])
            (filename, line, col, rule)  = (a['file'], int(a['line']), int(a.get("column",-1)), a['rule'])
            a["alert_id"] = cur_alert_id
            cur_alert_id += 1
            val = set_dict_path(self.alerts_by_line, filename, line, rule, a)
            if not val is a:
                mark_skipped_alert(a, f"Duplicate of alert_id={val['alert_id']}")
            if col:
                val = setdefault_dict_path(self.alerts_by_lc, filename, line, col, rule, a)
                if not val is a:
                    mark_skipped_alert(a, f"Duplicate of alert_id={val['alert_id']}")

    def fixup_nulldom_info(self):
        def fixup(cur_deref):
            [filename, [line, col]] = cur_deref
            if not filename.startswith("/"):
                filename = os.path.join(self.compile_dir, filename)
            filename = os.path.realpath(filename)
            return (filename, (line, col))
        self.nulldom_info = dict((fixup(cur_deref), info) for [cur_deref, info] in self.nulldom_info)

    def map_nulldom_locs_to_alerts(self):
        self.fixup_nulldom_info()
        self.nulldom_loc_to_alert = {}
        self.alert_id_to_nulldom_loc = {}
        for (cur_deref, info) in self.nulldom_info.items():
            (filename, (line, col)) = cur_deref
            try:
                # TODO: Use column number here once we start using column numbers in alerts.
                alert = self.alerts_by_line[filename][line]["EXP34-C"]
            except KeyError:
                continue
            self.nulldom_loc_to_alert.setdefault(cur_deref, []).append(alert)
            self.alert_id_to_nulldom_loc.setdefault(alert["alert_id"], []).append(cur_deref)

    def get_dominating_fixed_alert(self, cur_alert):
        nulldom_locs = self.alert_id_to_nulldom_loc.get(cur_alert["alert_id"], [])
        if len(nulldom_locs) != 1:
            return None
        dominating_derefs = self.nulldom_info[nulldom_locs[0]].get("derefs", [])
        filename = nulldom_locs[0][0]
        for dom_deref in dominating_derefs:
            dom_alerts = self.nulldom_loc_to_alert.get((filename, tuple(dom_deref)), ())
            # Each nulldom location should be mapped to at most one null-pointer alert.
            # If it is mapped to multiple alerts, check that each alert is repairable.
            ret = None
            for dom_alert in dom_alerts:
                if dom_alert["repair_algo"] == []:
                    ret = None
                    break
                else:
                    ret = dom_alert
            if ret:
                return ret
        return None

    def get_dominating_null_checks(self, cur_alert):
        nulldom_locs = self.alert_id_to_nulldom_loc.get(cur_alert["alert_id"], [])
        if len(nulldom_locs) != 1:
            return None
        dominating_checks = self.nulldom_info[nulldom_locs[0]].get("null_checks", [])
        return dominating_checks

    def mark_already_checked_null_alerts(self):
        for cur_alert in self.alert_list:
            if cur_alert["rule"] == "EXP34-C":
                dom_checks = self.get_dominating_null_checks(cur_alert)
                if dom_checks:
                    mark_skipped_alert(cur_alert, "Dominated by the following nullness checks (identified by (line, col) pairs): %s" % dom_checks)


    def mark_dependent_alerts(self):
        for cur_alert in self.alert_list:
            if cur_alert["rule"] == "EXP34-C":
                dom_alert = self.get_dominating_fixed_alert(cur_alert)
                if dom_alert:
                    mark_skipped_alert(cur_alert, "Dominated by alert %d" % dom_alert["alert_id"])


def build_NullDom_if_necessary():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    nulldom_cpp = script_dir + "/llvm/nulldom.cpp"
    libNullDom  = script_dir + "/llvm/libNullDom.so"
    if is_nonzero_file(libNullDom) and is_newer_file(libNullDom, nulldom_cpp):
        return libNullDom
    cur_dir = os.getcwd()
    os.chdir(script_dir + "/llvm")
    ast = subprocess.run(["cmake", "."])
    ast = subprocess.run(["make"])
    os.chdir(cur_dir)
    return libNullDom

def cleanup_json(s):
    s = re.sub("(^|\n)#[^\n]*", "\n", s)
    s = re.sub("],([\n ]*\\])", "]\\1", s)
    return s

def get_nulldom_info(ll_file):
    nulldom_so = build_NullDom_if_necessary()
    nulldom_info = subprocess.check_output(
        ("opt-15 -enable-new-pm=0 -load " + nulldom_so +
        " -mem2reg -sroa -domtree -nulldom -disable-output").split() + [ll_file])
    nulldom_info = nulldom_info.decode("utf-8")
    nulldom_filename = os.path.splitext(ll_file)[0] + ".nulldom.json"
    with open(nulldom_filename, 'w') as outfile:
        outfile.write(nulldom_info)
    nulldom_info = json.loads(cleanup_json(nulldom_info))
    return nulldom_info


def in_macro_at_start(ast):
    return ("spellingLoc" in ast['range']['begin'])

def in_macro_at_end(ast):
    return ("spellingLoc" in ast['range']['end'])

def mark_skipped_alert(alert, reason):
    match alert:
        case {"repair_algo": ["skip", kwargs]}:
            kwargs["why"].append(reason)
        case _:
            alert["repair_algo"] = ["skip", {"why": [reason]}]

def is_skipped_alert(alert):
    match alert:
        case {"repair_algo": ["skip", _]}:
            return True
        case _:
            return False

def is_indep_of_macros(node, alert):
    ret = True
    if in_macro_at_start(node):
        mark_skipped_alert(alert, "In a macro expansion at beginning of expression")
        ret = False
    if in_macro_at_end(node):
        mark_skipped_alert(alert, "In a macro expansion at end of expression")
        ret = False
    return ret

def parse_args():
    parser = argparse.ArgumentParser(description='Repairs source-code AST')
    parser.add_argument("ast_file", type=str, help="Clang AST from the Ear module (in JSON format)")
    parser.add_argument('-o', type=str, metavar="OUTPUT_FILE", dest="output_filename", required=True, help="Output filename")
    parser.add_argument('-a', type=str, metavar="ALERTS_FILE", dest="alerts_filename", required=True, help="Static-analysis alerts")
    cmdline_args = parser.parse_args()
    return cmdline_args


def main():
    cmdline_args = parse_args()
    run(**vars(cmdline_args))

def run(ast_file, alerts_filename, output_filename, skip_dom=False):
    if os.getenv('acr_emit_invocation'):
        print(f"brain.py -o {output_filename} -a {alerts_filename} {ast_file}")
    ll_file = get_ast_file_base(ast_file) + ".ll"
    ast = read_json_file(ast_file)
    brain = Brain(ast)
    brain.parse_alerts(alerts_filename)
    brain.nulldom_info = get_nulldom_info(ll_file)
    brain.map_nulldom_locs_to_alerts()
    brain.visit(ast)
    if not skip_dom:
        brain.mark_dependent_alerts()
        brain.mark_already_checked_null_alerts()
    with open(output_filename, 'w') as outfile:
        outfile.write(json.dumps(brain.alert_list, indent=2) + "\n")

if __name__ == "__main__":
    main()
