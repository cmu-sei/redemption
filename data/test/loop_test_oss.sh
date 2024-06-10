#!/bin/bash

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


# Run this script in directory redemption.public/data/test
# with no arguments. It will run tests using the test data, and will 
# create files with additional info about alerts.

# CAUTION: if you are saving intermediate files, the zeek files
# take a lot of disk space and you might run out of disk space.

# To save space and to do repairs of MSC12-C alerts, set these env variables:
export acr_gzip_ear_out=true
export REPAIR_MSC12=true

echo "running tests to create files with additional info about alerts"
for rule in EXP33-C EXP34-C MSC12-C CWE-476 CWE-561
do
    for codebase in git zeek
    do
	for tool in clang-tidy 	 cppcheck 	 rosecheckers
	do
	    echo $codebase"."$tool"."$rule".test.yml"
	    if [ -f $codebase"."$tool"."$rule".test.yml" ]; then 
		test_run=$(python3 test_oss.py -e $codebase"."$tool"."$rule".test.yml")
	    fi
	done
    done
    printf "\n"
done
	      
