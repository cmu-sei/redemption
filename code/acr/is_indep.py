
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

import bisect

def is_indep_of_cond_directives(ast_node, preproc_list):
    begin = ast_node["range"]["begin"]["offset"]
    end = ast_node["range"]["end"]["offset"]
    return not are_any_in_range(begin, end, preproc_list)

def are_any_in_range(begin, end, preproc_locs):
    index = bisect.bisect_right(preproc_locs, begin)
    if index == len(preproc_locs):
        return False
    x = preproc_locs[index]
    if x < begin:
        return False
    if x > end:
        return False
    return True

def test_in_range():
    L = [20, 40, 60]
    assert(are_any_in_range(7, 11, L) == False)
    assert(are_any_in_range(17, 21, L) == True)
    assert(are_any_in_range(27, 31, L) == False)
    assert(are_any_in_range(37, 41, L) == True)
    assert(are_any_in_range(47, 51, L) == False)
    assert(are_any_in_range(57, 61, L) == True)
    assert(are_any_in_range(67, 71, L) == False)

if __name__ == "__main__":
    test_in_range()
