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

# This script gathers info about which state adjudicated alerts result in, A-G (or none of those, if its adjudication
# combined with Redemption tool processing results in an incorrect state).
# The script gathers alert totals per-state and satisfaction ratio data, for each of the
# OSS test permutations of {codebase, tool, rule} in our OSS test dataset.
# The ending data after the "****" line can be copy/pasted into our testing wiki page's "sample testing" table
# Prerequisite: Tests should have previously been run with `-e`, resulting in ".test.yml.alerts_info.json" files.
# Run this script in directory `redemption.public/data/test` with no arguments.

import os
import sys
import re
sys.path.append('../../code/acr')
from make_run_clang import read_json_file
from dataclasses import dataclass

rules = ["EXP33-C", "EXP34-C", "MSC12-C", "CWE-476", "CWE-561"]

sample_results = {}
# sample_results[rule][codebase][tool])
#sample_results{"rule": rule [codebase][tool])
# sample_results.setdefault(rule, {}).setdefault(codebase, {}).[tool] = [ratio_float, ratio_string, short_counts]

@dataclass
class CountStates():
    countA: int = 0
    countB: int = 0
    countC: int = 0
    countD: int = 0
    countE: int = 0
    countF: int = 0
    countG: int = 0
    count_errors: int = 0
    count_unmatched: int = 0 # unmatched don't match a state A-G

    def print_counts(self):
        print("countA: ", self.countA)
        print("countB: ", self.countB)
        print("countC: ", self.countC)
        print("countD: ", self.countD)
        print("countE: ", self.countE)
        print("countF: ", self.countF)
        print("countG: ", self.countG)
        print("count_unmatched: ", self.count_unmatched)
        print("count_errors: ", self.count_errors)

    def get_errors_and_unmatched(self):
        string_errors_and_unmatched = str(self.count_unmatched)+","+str(self.count_errors)
        return string_errors_and_unmatched

    def get_short_counts(self):
        string_all_state_counts = str(self.countA)+","+str(self.countB)+","+str(self.countC)+","+str(self.countD)+","+str(self.countE)+","+str(self.countF)+","+str(self.countG)
        return string_all_state_counts

    def get_ratio_string_float(self):
        sum_abc = self.countA + self.countB + self.countC
        sum_all = self.countA + self.countB + self.countC + self.countD + self.countE + self.countF + self.countG + self.count_unmatched
        if(sum_all != 0):
            float_ratio = (sum_abc/sum_all)*100
        else:
            float_ratio = 0.0
        string_ratio = str(sum_abc)+"/"+str(sum_all)
        return(float_ratio, string_ratio)

    def print_short_counts(self):
        print(self.countA, ",", self.countB, ",", self.countC, ",", self.countD, ",", self.countE, ",", self.countF, ",", self.countG, ",", self.count_unmatched)

    def print_ratio(self):
        sum_abc = self.countA + self.countB + self.countC
        sum_all = self.countA + self.countB + self.countC + self.countD + self.countE + self.countF + self.countG + self.count_unmatched
        print(str(sum_abc)+"/"+str(sum_all))
        if(sum_all != 0):
            ratio = sum_abc/sum_all
        else:
            ratio = 0.0
        print(ratio)
        if(ratio >= 0.8):
            print("GREEN")



alerts_brain_data_dir = "/host/data/test"
alerts_brain_data_end = ".test.yml.alerts_info.json"
alerts_file_end = ".alerts.json"
alerts_path_begin = "/oss/"
divider=" , "

pattern = re.compile(".*random.*")
pattern2 = re.compile(".*sample.*")
disqualified_random_pattern = re.compile(".*disqualified.*")

repairable_true_pattern = re.compile("true")
verdict_true_complex_pattern = re.compile("true|complex|true (complex)")
satisfactory_true_pattern = re.compile("true")
errors = 0

def pass_state(*, satisfactory, patch, verdict, is_fp, repairable, cs):
    print("satisfactory: ", satisfactory, "patch: ", patch, "verdict: ", verdict, "repairable: ", repairable, "is_fp: ", is_fp)
    r_tp = bool(repairable_true_pattern.match(repairable)) or "false"
    v_tcp = bool(verdict_true_complex_pattern.match(verdict)) or "false"
    s_tp = bool(satisfactory_true_pattern.match(satisfactory)) or "false"
    #switch_string = str(s_tp).lower()+"."+str(patch).lower()+"."+str(v_tcp).lower()+"."+str(r_tp).lower()+"."+str(is_fp).lower()
    switch_string = str(s_tp).lower()+"."+str(patch).lower()+"."+str(v_tcp).lower()
    # Other values not in case statements: str(r_tp).lower() and str(is_fp).lower()
    repairable_tp = str(r_tp).lower()
    is_false_positive = str(is_fp).lower()
    found_error = 0
    print("switch_string: ", switch_string)
    match switch_string:
      # "satisfactory.patch.verdict" is the key for the states case strings below.
      # (repairable,  is_fp)  are the additional fields to inspect. In-order: str(r_tp).lower() and str(is_fp).lower()
      case "true.true.true":
        if(repairable_tp == "false"):
          print("State A error, repairable field false. Mark `satisfaction` field false in alerts.json file, then rerun.");
          cs.count_errors += 1;
        cs.countA += 1;
        return "A"
      case "true.true.false":
        if((repairable_tp == "false") and (is_false_positive == "true")):
          print("State C error, is_false_positive: ", is_false_positive, "repairable_tp: ", repairable_tp);
          cs.count_errors += 1;
        cs.countC += 1;
        return "C"
      case "true.false.true":
        if((repairable_tp == "true") and (is_false_positive == "false")):
          print("Error, no matching pass state. Mark `satisfaction` field false in alerts.json file, then rerun this script. is_false_positive: ", is_false_positive, "repairable_tp: ", repairable_tp);
        cs.count_errors += 1;
        cs.count_unmatched += 1;
        return "Error, no matching pass state"
      case "true.false.false":
        if((repairable_tp == "true") and (is_false_positive == "false")):
            print("State B error, repairable field true and is_false_positive field false. Mark `satisfaction` field false in alerts.json file, after that the state will map to E. (Detail: It's repairable but no patch was done AND it's a false positive verdict but is_fp is false. It might have previously been marked satisfactory since code wasn't broken. By changing `satisfactory` to false, then we get state E ... OR, by changing `repairable` to false, we would get a different error message recommending another change which then results in state E.)");
            found_error = 1;
        else:
            if(repairable_tp == "true"):
                print("State B error, repairable_tp: ", repairable_tp);
                found_error = 1;
            if(is_false_positive == "false"):
                print("State B error, is_false_positive: ", is_false_positive);
                found_error = 1;
                if(repairable_tp == "false"):
                    print("Mark `satisfaction` field false in alerts.json file, then rerun this script. is_false_positive: ", is_false_positive, "repairable_tp: ", repairable_tp);
        if(found_error == 1):
            cs.count_errors += 1;
        cs.countB += 1;
        return "B"
      case "false.true.true":
        if(repairable_tp == "false"):
            print("State F error, repairable_tp: ", repairable_tp);
            cs.count_errors += 1;
        cs.countF += 1;
        return "F"
      case "false.true.false":
        cs.countG += 1;
        return "G"
      case "false.false.true":
        cs.countD += 1;
        return "D"
      case "false.false.false":
        if(is_false_positive == "true"):
            print("State E error, is_false_positive: ", is_false_positive);
            cs.count_errors += 1;
        cs.countE += 1;
        return "E"
      case _: cs.count_errors += 1; cs.count_unmatched += 1; return "Error, no matching pass state"

for rule in rules:
    for codebase in ["git", "zeek"]:
        for tool in ["clang-tidy", "cppcheck", "rosecheckers"]:
            file_prefix = codebase+"."+tool+"."+rule
            print(file_prefix+alerts_brain_data_end)
            alerts_brain_data_file = os.path.realpath(os.path.join(alerts_brain_data_dir, file_prefix+alerts_brain_data_end))
            if(os.path.exists(alerts_brain_data_file)):
                select_braindata = read_json_file(alerts_brain_data_file)
                # dictionary indexed per C filepath, indexed by rule, indexed by ALERT ID with list [patched, is_tp]

                print(file_prefix+alerts_file_end)
                alerts_filepath = os.path.realpath(os.path.join(alerts_brain_data_dir, file_prefix+alerts_file_end))
                if(os.path.isfile(alerts_filepath)):
                    # Now, need to determine for each test what type of pass, NOT sum for each alerts.json and test.yml file
                    # Gather alert.json data, then for that alert the test.yml.alerts_info.json data
                    # Then determine which pass_status. Store running totals of each type, plus lists of each (use alertID).
                    alerts_main_data = read_json_file(alerts_filepath)

                    # Iterate through the alerts list
                    id = 1
                    print("id reset to 1")
                    cs = CountStates()
                    for a in alerts_main_data:
                        count_this = 0
                        file = a["file"]
                        filepath = os.path.realpath(os.path.join(alerts_path_begin, codebase, file))
                        # Only analyze pass_status for adjudicated alerts
                        # So, only analyze "sample" and "random and sample" for MSC12-C alerts (NOT "disqualified sample")
                        if "randomness" in a:
                            # These fields only exist in the adjudicated alerts in alerts.json
                            randomness = a["randomness"]
                            repairable = a["repairable"]
                            verdict = a["verdict"]
                            satisfactory = a["satisfactory"]

                            if(rule == "MSC12-C"):
                                # if(msc12c_pattern.match(randomness)):
                                #     count_this = 1
                                if(pattern2.match(randomness)):
                                   print("matched sample for randomness")
                                   if(not disqualified_random_pattern.match(randomness)):
                                       count_this = 1
                            else:
                                if(pattern.match(randomness)):
                                    print("matched random for randomness")
                                    if(not disqualified_random_pattern.match(randomness)):
                                        count_this = 1
                                if(pattern2.match(randomness)):
                                   print("matched sample for randomness")
                                   if(not disqualified_random_pattern.match(randomness)):
                                       count_this = 1
                            if(count_this == 0):
                                id += 1
                                continue
                            else:
                                # Get additional fields for those alerts, from the other file
                                print("filepath: ", filepath, "rule: ", rule, "id: ", id)
                                try:
                                    this_brain_data = select_braindata[filepath][rule][str(id)]

                                except:
                                    print("wasn't able to access braindata, skipping this alert")
                                    continue
                                if(this_brain_data):
                                    print("this_brain_data is [patch, is_fp]: ", this_brain_data)
                                    patch = this_brain_data[0]
                                    is_fp = this_brain_data[1]
                                    state = pass_state(satisfactory=satisfactory, patch=patch, verdict=verdict,  is_fp=is_fp, repairable=repairable, cs=cs)
                                    print("state: ",state)
                                else:
                                    print("this_brain_data empty for this alert")

                        id += 1 # increment alert ID before next loop

                    print("For file: "+file_prefix+alerts_file_end)
                    cs.print_counts()
                    cs.print_short_counts()
                    cs.print_ratio()
                    all_state_counts = cs.get_short_counts()
                    this_float_ratio, this_string_ratio = cs.get_ratio_string_float()
                    errors_and_unmatched = cs.get_errors_and_unmatched()
                    print("tool: ", tool)
                    sample_results.setdefault(rule, {}).setdefault(codebase, {})[tool] = [this_float_ratio, this_string_ratio, all_state_counts, errors_and_unmatched]

print("**************************************************")
print("CAUTION: Counts below are wrong if there were any unmatched (count_unmatched) or other errors (count_errors). See details of such errors and possible fixes in output above, fix them, then rerun the script until no errors result.")

for rule in rules:
    print(rule)
    for codebase in ["git", "zeek"]:
        for tool in ["clang-tidy", "cppcheck", "rosecheckers"]:
            print(codebase+"."+tool+"."+rule)
            try:
                value_found1 = sample_results[rule][codebase][tool][0]
            except KeyError:
                print("No value_found_1")
                continue
            try:
                value_found2 = sample_results[rule][codebase][tool][1]
            except KeyError:
                print("No value_found_2")
                continue
            try: 
                value_found3 = sample_results[rule][codebase][tool][2]
            except KeyError:
                print("No value_found_3")
                continue
            try:
                info_found = sample_results[rule][codebase][tool][3]
            except KeyError:
                print("No info_found about unmatche and errors")
                continue
            print(str(value_found1)+"%  ("+str(value_found2)+")   [Per-state counts: "+value_found3+"] ")
            print("count_unmatched, count_errors: ", str(info_found))
    print("\n") # newline per rule

