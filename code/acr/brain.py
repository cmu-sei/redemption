
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
import subprocess

from util import *
from make_run_clang import read_json_file
from is_indep import is_indep_of_cond_directives
from brainstem import Brainstem
from alert import alert_from_dict
from collections import namedtuple
from collections.abc import Mapping
from collections.abc import Sequence
from SortedCollection import SortedCollection
from itertools import takewhile

class ASTContext:
    """An ASTContext adds a path history to an dictionary.

    Speficially, an ASTContext acts just like an dictionary or a list,
    except that retrieving a value using get or __getitem__ will wrap
    any dictionary or list values in an ASTContext.  This wrapper
    keeps track of the parent dictionary of the value.  Calling parent
    on an ASTContext will return that parent dictionary, also wrapped
    as an ASTContext.
    """

    def __new__(cls, val, path=False, **kwds):
        if path:
            if isinstance(val[0], dict):
                inst = ASTMappingContext.__new__(ASTMappingContext, {}, **kwds)
            elif isinstance(val[0], list):
                inst = ASTSequenceContext.__new__(ASTSequenceContext, [], **kwds)
            else:
                return val[0]
            inst.path = val
            inst.name_proxy = kwds.get('name_proxy')
            return inst
        if isinstance(val, ASTContext):
            return val.__class__(val, **kwds)
        if isinstance(val, dict):
            return ASTMappingContext(val, **kwds)
        if isinstance(val, list):
            return ASTSequenceContext(val, **kwds)
        return val

    def __init__(self, val, path=False, name_proxy=None):
        self.name_proxy = name_proxy
        if isinstance(val, ASTContext):
            self.path = val.path
            if self.name_proxy is None:
                self.name_proxy = val.name_proxy
        elif path:
            self.path = val
        else:
            self.path = (val, None)

    def __getattr__(self, name):
        return getattr(self.name_proxy, name)

    def current(self):
        return self.path[0]

    def __len__(self):
        return len(self.current())

    def __iter__(self):
        for x in self.current():
            yield ASTContext((x, self.path), path=True, name_proxy=self.name_proxy)

    def __contains__(self, key):
        return key in self.current()

    def __repr__(self):
        return f"ASTContext({self.current()})"

    def parent(self, kind = False):
        """Return the parent ASTContext, or None if there is no parent.
        If kind is True, find the first ancestor that is a map that
        has a "kind" field.
        """
        current = self
        while True:
            val = current.path[1]
            if val is None:
                return None
            current = ASTContext(val, path=True, name_proxy=self.name_proxy)
            if not kind or "kind" in current:
                return current

    def parent_non_implicit_cast(self):
        """Return the first ancestor that has a kind that isn't ImplicitCastExpr."""
        current = self
        while True:
            current = current.parent(True)
            if current is None:
                return None
            if current['kind'] != "ImplicitCastExpr":
                return current

    def find_through_parents(self, kind_or_predicate):
        """Search through parents for a specific type of node.

        The first matching node can be the current node (self).

        If kind_or_predicate is a string, find the first
        node that has that kind.  If kind_or_predicate is a
        callable, find the first ancestor for which the result of
        calling the predicate with the node evaluates to truth.
        """
        current = self
        if callable(kind_or_predicate):
            check = kind_or_predicate
        else:
            check = lambda x: x.is_mapping() and x.get('kind') == kind_or_predicate
        while True:
            if check(current):
                return current
            val = current.path[1]
            if val is None:
                return None
            current = ASTContext(val, path=True, name_proxy=self.name_proxy)

    def traverse_descendants(self):
        """Return a generator for all this node's descendants.

        This will return all ASTContext nodes, in depth-traversal
        order, starting with self.
        """
        yield self
        if self.is_mapping():
            nodes = self.values()
        else:
            nodes = self
        for node in nodes:
            if isinstance(node, ASTContext):
                for val in node.traverse_descendants():
                    yield val

    def root(self):
        """Return the top parent."""
        (current, parent) = self.path
        while path is not None:
            (current, parent) = parent
        return ASTContext(val, path=True, name_proxy=self.name_proxy)

    def _get_lc(self, end):
        match self:
            case {'line': line, 'col': col, 'tokLen': toklen}:
                if end:
                    # In clang's AST, ranges are deliniated by tokens,
                    # not offsets.  These tokens have offsets and
                    # sizes.  To get the end of a range, you have to
                    # take the end token location and add the token
                    # length to that.
                    return (line, col + toklen)
                else:
                    return (line, col)
        return None

    def _get_range_part(self, part):
        try:
            rng = self.get("range")
        except AttributeError:
            return None
        if rng is None:
            return None
        val = rng[part]
        fn = rng.get('file')
        real = None
        atleastone = None
        for key in ['expansionLoc', 'spellingLoc']:
            sub = val.get(key)
            if sub is not None:
                atleastone = sub
                if fn is None or sub.get('file') == fn:
                    real = sub
        if real is None:
            return atleastone if atleastone is not None else val
        return real

    def get_begin(self):
        return self._get_range_part('begin')

    def get_end(self):
        return self._get_range_part('end')

    def get_begin_lc(self):
        n = self.get_begin()
        if n is None:
            return None
        return n._get_lc(False)

    def get_end_lc(self):
        n = self.get_end()
        if n is None:
            return None
        return n._get_lc(True)

    def __getitem__(self, key):
        return ASTContext((self.current()[key], self.path), path=True,
                          name_proxy=self.name_proxy)

    def __eq__(self, other):
        if isinstance(ASTContext, other):
            other = other.current()
        return self.current() == other

class ASTConcreteContext(ASTContext):

    def __new__(cls, *args, **kwds):
        return object.__new__(cls)

class ASTMappingContext(ASTConcreteContext, Mapping):

    def is_mapping(self):
        return True

class ASTSequenceContext(ASTConcreteContext, Sequence):

    def is_mapping(self):
        return False


class Brain(AstVisitor):

    Location = namedtuple('Location', ['file', 'begin', 'end', 'id'])

    def __init__(self, ast):
        super().__init__()
        self.intervals = []
        self.alerts_by_line = None
        self.alerts_by_lc = None
        self.preproc_db = ast["preproc_db"]
        self.base_dir = ast["base_dir"]
        self.compile_dir = ast["compile_dir"]
        self.var_decls_by_id = {}

        brainstem = Brainstem();
        brainstem.visit(ast)
        self.error_handling_db = brainstem.error_handling_db

    def mark_skipped_alert(self, alert, reason):
        match alert:
            case {"why_skipped": reasons}:
                if reason not in reasons:
                    reasons.append(reason)
            case _:
                alert["why_skipped"] = [reason]
        alert["patch"] = []

    def is_indep_of_macros(self, node, alert):
        ret = True
        if in_macro_at_start(node):
            self.mark_skipped_alert(alert, "In a macro expansion at beginning of expression")
            ret = False
        if in_macro_at_end(node):
            self.mark_skipped_alert(alert, "In a macro expansion at end of expression")
            ret = False
        return ret

    def check_repairability(self, alert, node):
        # Note: We need to check in_macro_at_{start,end} before calling
        # is_indep_of_cond_directives since
        # is_indep_of_cond_directives throws a KeyError if inside a macro.
        def in_base_dir(pathname):
            return pathname.startswith(self.base_dir + "/")
        filename = node["range"]["file"]
        if not in_base_dir(filename):
            self.mark_skipped_alert(alert, "Outside of base_dir")
            return
        if not self.is_indep_of_macros(node, alert):
            return
        if not is_indep_of_cond_directives(node, self.preproc_db[filename]):
            self.mark_skipped_alert(alert, "Contains preprocessor directives")
            return

    def previsit(self, node):
        if node["kind"] == "VarDecl":
            self.var_decls_by_id[node["id"]] = node

        match node:
            case {'range': {'file': filename, 'begin': _, 'end': _}}:
                begin = node.get_begin_lc()
                if begin is None:
                    return
                end = node.get_end_lc()
                if end is None:
                    return
                node_id = node.get("id", 0)
                if isinstance(node_id, str):
                    node_id = node.get("prevId", 0)
                self.intervals.append((self.Location(filename, begin, end, node_id), node))

    def parse_alerts(self, alerts_filename):
        alert_list = read_json_file(alerts_filename)
        self.alert_list = [alert_from_dict(x) for x in alert_list]
        self.alerts_by_line = {}
        self.alerts_by_lc = {}
        cur_alert_id = 1

        def add(alert, alert_list):
            rule = alert['rule']
            for a in alert_list:
                if a['rule'] == rule:
                    self.mark_skipped_alert(alert, f"Duplicate of alert_id={a['alert_id']}")
                    return False
            alert_list.append(alert)

        for a in self.alert_list:
            if not a['file'].startswith("/"):
                # Relative pathnames in the Alerts file are considered to be
                # relative to the base_dir.
                a['file'] = os.path.join(self.base_dir, a['file'])
            a['file'] = os.path.realpath(a['file'])
            # column is optional, so we use a.get() to retrieve it
            (filename, line, col, rule)  = (a['file'], int(a['line']), a.get("column"), a['rule'])
            a["alert_id"] = cur_alert_id
            cur_alert_id += 1
            val = setdefault_dict_path(self.alerts_by_line, filename, line, rule, a)
            if not val is a and col is None:
                self.mark_skipped_alert(a, f"Duplicate of alert_id={val['alert_id']}")
            if col is not None:
                val = setdefault_dict_path(self.alerts_by_lc, filename, line, int(col), rule, a)
                if not val is a:
                    self.mark_skipped_alert(a, f"Duplicate of alert_id={val['alert_id']}")

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
                if dom_alert["patch"] == []:
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
                    self.mark_skipped_alert(cur_alert, "Dominated by the following nullness checks (identified by (line, col) pairs): %s" % dom_checks)
                    cur_alert["shouldnt_fix"] = True


    def mark_dependent_alerts(self):
        for cur_alert in self.alert_list:
            if cur_alert["rule"] == "EXP34-C":
                dom_alert = self.get_dominating_fixed_alert(cur_alert)
                if dom_alert:
                    self.mark_skipped_alert(cur_alert, "Dominated by alert %d" % dom_alert["alert_id"])
                    cur_alert["shouldnt_fix"] = True

    @staticmethod
    def _key(item):
        # Sort nodes based on filename, start location, end location.
        # An extra 0 is placed before the end location, so we can
        # always find the end of a range of intervals that begins with
        # the same start location.
        loc, _ = item
        return (loc.file, loc.begin, (0, loc.end), -loc.id)

    def minimum_spanning(self, node, lc, filename):
        while node is not None:
            if node.is_mapping():
                fn = get_dict_path(node, "range", "file")
                if fn != filename:
                    return None
                begin = node.get_begin_lc()
                end = node.get_end_lc()
                if end is not None and begin is not None and begin <= lc and end > lc:
                    return node
            node = node.parent()

    def locate(self, filename, lc):
        try:
            if lc[1] == -1:
                # Handle the line-number only case.  In this case,
                # return the largest non-overlapping nodes that start
                # on that line.
                idx, (key, node) = self.intervals.find_ge((filename, lc, (1, None)))
                items = (self.intervals[i] for i in range(idx, len(self.intervals)))
                candidates = takewhile(lambda x: (x[0].file == filename
                                                  and x[0].begin[0] == lc[0]),
                                       items)
                first = next(candidates, None)
                if first is None:
                    return None
                nodes = [first]
                for (loc, node) in candidates:
                    end = nodes[-1][0].end
                    if loc.begin > end:
                        nodes.append((loc, node))
                    else:
                        begin = nodes[-1][0].begin
                        if loc.begin <= begin and loc.end >= end:
                            nodes[-1] = (loc, node)
                return ([x[1] for x in nodes], False)
            else:
                idx, (key, node) = self.intervals.find_le((filename, lc, (1, None)))
                if key.file != filename:
                    return None
                new_node = self.minimum_spanning(node, lc, filename)
                if new_node is node:
                    items = (self.intervals[i] for i in range(idx, 0, -1))
                    nodes = takewhile(lambda x: (x[0].file == filename
                                                      and x[0].begin == key.begin),
                                           items)
                    return ([x[1] for x in nodes], True)
                elif new_node is None:
                    return None
                else:
                    return ([new_node], False)
        except ValueError:
            return None

    def run(self, ast):
        self.visit(ast)
        self.intervals = SortedCollection(iterable=self.intervals, key=self._key)
        for a in self.alert_list:
            # If already "repaired", don't attempt to re-repair it.
            # This is primarily for alerts marked as "duplicates".
            if "patch" in a:
                continue
            # column is optional, so we use a.get() to retrieve it
            (filename, line, col)  = (a['file'], int(a['line']), int(a.get("column",-1)))
            lc = (line, col)
            nodes = self.locate(filename, lc)
            if nodes is not None:
                # To conform to the old brain behavior, if the lc from
                # the node matches the searched-for lc, consider this
                # a whole_expr.  For whole_exprs, we attempt to repair
                # each subexpr that matches the lc, allowing the last
                # repaired one to succeed.  This functionality is only
                # used by EXP34-C, and should be replaced by moving
                # this logic to the alert itself.  It currently is
                # here because the brain has to do less work to find
                # the matching intervals (nodes).
                nodes, whole_expr = nodes
                a.whole_expr = whole_expr
                nodes = a.filter_nodes(nodes)
                last_node = None
                for node in nodes:
                    repair_node = a.locate_repairable_node(node)
                    if repair_node is not None:
                        last_node = repair_node
                        self.check_repairability(a, repair_node)
                if last_node is not None and "why_skipped" not in a:
                    a.attempt_patch(last_node)

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

def run(ast_file, alerts_filename, output_filename):
    if os.getenv('acr_emit_invocation'):
        print("brain.py -o {} -a {} {}".format(
            output_filename, alerts_filename, ast_file))
    ll_file = get_ast_file_base(ast_file) + ".ll"
    ast = read_json_file(ast_file)
    brain = Brain(ast)
    brain.parse_alerts(alerts_filename)
    brain.nulldom_info = get_nulldom_info(ll_file)
    brain.map_nulldom_locs_to_alerts()
    brain.run(ASTContext(ast, name_proxy=brain))
    skip_dom=(os.getenv('acr_skip_dom') or "false").lower() == "true"
    for alert in brain.alert_list:
        alert.setdefault("patch", [])
    if not skip_dom:
        brain.mark_dependent_alerts()
        brain.mark_already_checked_null_alerts()
    with open(output_filename, 'w') as outfile:
        outfile.write(json.dumps(brain.alert_list, indent=2) + "\n")

if __name__ == "__main__":
    main()
