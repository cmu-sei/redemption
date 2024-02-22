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

######################################################################
# Example usage:
#
# clang -Xclang -ast-dump -fsyntax-only -fno-color-diagnostics /host/code/acr/test/test_errors.c | python3 /host/code/analysis/extract_func_names_lines_clang.py > func_bounds.test_errors.json
######################################################################


import sys, re;
import json

# Skip fns declared in headers
line = ""
while re.search("\.c:", line) is None:
    line = sys.stdin.readline()
    if line == "":
        break

ast = "\n" + line + sys.stdin.read()

match = re.search(r".*[< ]([^ ]*.c):", ast, re.VERBOSE)
if match is not None:
    path = match.group(1)

pat = (
    r"""(\n[`|]-FunctionDecl(.*)
        (\n[| ][ ].*)*
        (\n[| ][ ])[`|]-CompoundStmt)
    """)

matches = re.findall(pat, ast, re.VERBOSE)

L = []
prev_start = -1
prev_end = -1
for m in matches:
    m2 = re.match(r"^.* <.*:(\d*):\d*, line:(\d*):\d*> .* ([^ ]*) '.*", m[1].strip())
    if m2 is not None:
        m3 = m2.group(1, 2, 3)
    else:
        m2 = re.match(r"^.*.c:(\d*):\d*> line:(\d*):\d*.* ([^ ]*) '.*", m[1].strip())
        if m2 is not None:
            m3 = m2.group(2, 1, 3)
        else:
            m2 = re.match(r".*<line:(\d*):\d*, col:\d*> col:\d* ?.*? ([^ ]*) '.*", m[1].strip())
            if m2 is not None:
                m3 = m2.group(1, 1, 2)
            else:
                sys.stderr.write("ERROR: " + m[1].strip() + "\n")
                m3 = None

    if m3:
        (start, end, func) = m3
        start = int(start)
        end = int(end)
        if start < prev_end:
            start = prev_end + 1
        cur_item = (path, start, end, func)
        L.append(cur_item)
        prev_start = start
        prev_end = end

if __name__ == "__main__":
    #print("# " + json.dumps(["filename", "start", "end", "func_name"]))
    json_lines = []
    for cur_item in L:
        json_lines.append(json.dumps(cur_item))
    print("[")
    print(",\n".join(json_lines))
    print("]")

