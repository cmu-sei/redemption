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

# This script creates 2 .csv "tables". First table shows ratio of satisfactory
# alerts to all audited alerts as fraction, second table provides that as a
# percent ratio. Run this script in directory `redemption.public/data/test`
# with no arguments. The script gathers alert totals and satisfaction ratio
# data and outputs the two .csv `tables`.

divider=" , "
for chart in {1..2}
do
    echo "table "$chart
    for rule in EXP33-C EXP34-C MSC12-C
    do
	for codebase in git zeek
	do
	    for tool in clang-tidy 	 cppcheck 	 rosecheckers
	    do
		#echo $codebase"."$tool"."$rule".alerts.json"
		if [ -f $codebase"."$tool"."$rule".alerts.json" ]; then 
		    sat1=$(grep "satisfactory\": \"true"  <$codebase"."$tool"."$rule".alerts.json" | wc	-l)
		    total1=$(grep "satisfactory\": \""  <$codebase"."$tool"."$rule".alerts.json" | wc	-l)
		    if [[ $chart -eq 2 ]]; then
			if [[ $total1 != 0 ]]; then 
			    x=$(bc <<< "scale=2; $sat1 / $total1")
			    echo -n "$x"$divider
			else
			    echo -n "0"$divider
			fi
		    else
			echo -n $sat1/$total1$divider
		    fi
		else
		    echo -n $divider
		fi
	    done
	done
	printf "\n"
    done
done
	      
