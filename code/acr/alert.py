
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

from collections import OrderedDict
import os
import re
from util import get_dict_path, AstVisitor, read_file_range

class Alert(OrderedDict):
    """A Redemption alert.

    An Alert is fundamentally an ordered dictionary.  This dictionary
    represents the JSON information for the alert.

    The main interfaces for an alert are the attempt_repair and
    attempt_patch methods.  attempt_repair is called with an AST node.
    If the repair attempt succeeds it should return the AST node
    associated with the repair, otherwise it should return None.
    attempt_patch is called on Alerts for which attempt_repair
    succeeded.  It should modify the JSON dictionary to apply an
    appropriate patch.  Data can be transmitted between the repair and
    patch processes by storing that data in attributes on the Alert
    instance.
    """

    def __init__(self, val):
        super().__init__(val)

    def attempt_repair(self, context):
        raise NotImplementedError

    def attempt_patch(self, context):
        raise NotImplementedError

    @staticmethod
    def get_decl_of_var(node):
        if node["kind"] == "VarDecl":
            return node
        if node["kind"] != "DeclRefExpr":
            return None
        decl_id = node.get("referencedDecl",{}).get("prevId")
        if not decl_id:
            return None
        decl_node = node.var_decls_by_id.get(decl_id)
        if not decl_node:
            return None
        return decl_node

class NullAlert(Alert):
    """An alert that will not repair anything"""

    def attempt_repair(self, context):
        return None

    def attempt_patch(self, context):
        return False


class EXP33_C(Alert):
    """An alert that handles EXP33_C repairs"""

    def attempt_repair(self, context):
        def get_uninit_var_name(alert):
            message = alert.get("message","")
            m = re.match("variable '([^']*)' is not initialized", message)
            if m:
                return m.group(1)
            m = re.match("Uninitialized variable: (.*)", message)
            if m:
                return m.group(1)
            return None
        var = get_uninit_var_name(self)
        if var is None:
            return None
        decl_node = self.get_decl_of_var(context)
        if decl_node is None or decl_node.get("name") != var:
            return None
        self.decl_node = decl_node
        self["ast_id"] = decl_node['id']
        return context

    def attempt_patch(self, context):
        # Create the patch
        init_val = "0"
        if self.decl_node["type"]["qualType"].endswith("*"):
            if self['file'].endswith(".cpp"):
                init_val = "nullptr"
            else:
                init_val = "NULL"
        elif self.decl_node["type"].get("desugaredQualType","").startswith(("struct","union")):
            init_val = "{}"
        try:
            loc = self.decl_node["loc"]
            byte_end = loc['offset'] + loc['tokLen']
        except KeyError:
            self["why_skipped"] = "AST node is missing VarDecl location information"
            self["patch"] = []
            return False
        edit = [self['file'], [
            [byte_end, byte_end, " = " + init_val]]]
        self["patch"] = [edit]
        return True

class MSC12_C(Alert):

    enable_msc12 = (os.getenv('REPAIR_MSC12') or "").lower() != "false"

    def try_deadinit_var_repair(self, node):
        message = self.get("message","")
        m = re.match("^Redundant initialization for '([^']*)'.*", message)
        if not m:
            return False
        decl_node = self.get_decl_of_var(node)
        if not decl_node:
            return False
        self.decl_node = decl_node
        self.repair_algo = "repair_deadinit_var"
        return True

    def attempt_repair(self, context):
        if not self.enable_msc12:
            self["ast_id"] = context['id']
            context.mark_skipped_alert(
                self,
                "Repair of MSC12-C is disabled; set env var REPAIR_MSC12=true to enable it.")
            return None
        # TODO: This probably shouldn't happen here, but is kept for
        # comparison purposes
        self.repair_algo = "msc12c"
        macro_file = get_dict_path(context, 'range', 'begin', 'spellingLoc', 'file')
        if macro_file is not None and macro_file.endswith("/assert.h"):
            context.mark_skipped_alert(self, "False positive: inside an assert")
            return None
        if self.try_deadinit_var_repair(context):
            self["ast_id"] = context['id']
            return context
        if self.get("checker", "").startswith("uselessAssignment"):
            if context["kind"] != "DeclRefExpr":
                return None
            self.decl_node = context.parent(True)
            if (self.decl_node["kind"] != "BinaryOperator"
                or not self.decl_node["opcode"].startswith("=")):
                return None
            self.repair_algo = "del_unused_asgn"
            self["ast_id"] = context['id']
            return context
        return None

    def attempt_patch(self, context):
        algo = self.repair_algo
        if algo == "repair_deadinit_var":
            try:
                filename = self.decl_node["range"]["file"]
                begin_offset = self.decl_node.get_begin()['offset']
                end = self.decl_node.get_end()
                end_offset = end["offset"] + end["tokLen"]
            except KeyError:
                self["why_skipped"] = "KeyError"
                self["patch"] = []
                return False
            decl_text = read_file_range(filename, begin_offset, end_offset)
            m = re.search(b"( *=)", decl_text)
            if not m:
                self["why_skipped"] = "No assignment '=' found!"
                self["patch"] = []
                return False
            del_start = begin_offset + m.span()[0]
            edit = [self['file'], [[del_start, end_offset, ""]]]
            self["patch"] = [edit]
            return self.decl_node
        elif algo == "del_unused_asgn":
            asgn = self.decl_node
            try:
                del_begin = self.decl_node.get_begin()["offset"]
                del_end = asgn["inner"][1].get_begin()["offset"]
            except KeyError:
                self["why_skipped"] = "KeyError"
                self["patch"] = []
                return False
            edit = [self['file'], [[del_begin, del_end, "(void) "]]]
            self["patch"] = [edit]
        else:
            return False


class EXP34_C(Alert):

    def get_error_handler_at_cursor(self, context):
        fn_decl_node = context.find_through_parents("FunctionDecl")
        try:
            eh = context.error_handling_db[fn_decl_node["id"]]["error_handler"]
            return eh
        except:
            return None

    def find_dereference_locus(self, node):
        def match_dereference(node):
            match node:
                case ({'kind': "UnaryOperator", "opcode": "*"}
                      | {'kind': "ArraySubscriptExpr"}
                      | {'kind': "MemberExpr", "isArrow": _}):
                    return (None, node)
            return False
        self.context = node.find_through_descendants(match_dereference)
        return self.context is not None

    def attempt_repair(self, context):
        match self:
            case None:
                return None
            case {'patch': _} if not self.whole_expr:
                return None
            case {'tool': 'rosecheckers', 'ast_id': _} if getattr(
                    self, 'saved_whole_expr', False):
                return None
        message = self.get("message","")
        m = re.match("Null pointer passed to ([0-9]+).. parameter", message)
        if m:
            if context.get("kind") != "CallExpr":
                return None
            param_ordinal = int(m.group(1))
            self.context = context["inner"][param_ordinal]
        elif not self.whole_expr:
            if not self.find_dereference_locus(context):
                return None
        else:
            self.context = context
        self["ast_id"] = self.context['id']
        self.handle_error = self.get_error_handler_at_cursor(self.context)
        self.saved_whole_expr = self.whole_expr
        return self.context

    @staticmethod
    def is_expr_of_ptr_type(ast_node):
        return ast_node["type"]["qualType"].endswith("*")

    def attempt_patch(self, context):
        if self.whole_expr:
            ptr_subexpr = self.context
        elif self.context.get('opcode') == '*':
            ptr_subexpr = self.context['inner'][0]
        elif self.context["kind"] == "ArraySubscriptExpr":
            ptr_subexpr = self.context["inner"][0]
            if (not self.is_expr_of_ptr_type(ptr_subexpr)
                and self.is_expr_of_ptr_type(self.context["inner"][1])):
                ptr_subexpr = self.context["inner"][1]
        elif self.context["kind"] == "MemberExpr" and self.context.get("isArrow"):
            ptr_subexpr = self.context["inner"][0]
        else:
            raise Exception("Unrecognized node passed to add_null_check, and whole_expr isn't true.")

        byte_start = ptr_subexpr.get_begin()['offset'] - 1
        end = ptr_subexpr.get_end()
        byte_end = end['offset'] + end['tokLen']
        if self.handle_error is not None:
            closer = ", " + self.handle_error + ")"
        else:
            closer = ")"
        edit = [self['file'], [
            [byte_start+1, byte_start+1, "null_check("],
            [byte_end, byte_end, closer]]]
        self["patch"] = [edit]

class CWE_476(EXP34_C):
    # Currently an exact duplicate of EXP34_C
    pass

class CWE_561(MSC12_C):
    # Currently an exact duplicate of MSC12_C
    pass


rule_list = {
    "CWE-476": CWE_476,
    "CWE-561": CWE_561,
    "EXP33-C": EXP33_C,
    "EXP34-C": EXP34_C,
    "MSC12-C": MSC12_C
}


def alert_from_dict(json_alert):
    rule = json_alert.get("rule")
    cls = rule_list.get(rule, NullAlert)
    return cls(json_alert)
