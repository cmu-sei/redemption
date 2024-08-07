#!/bin/sh

# To use this script, rename it to 'gcc' and put it in your $PATH ahead of /usr/bin/gcc

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

ARGS=$*
CLANG_ARGS=`echo $ARGS | perl -p -e 's/-fmacro-prefix-map=[^ ]*//g;'`
PROCESSED_ARGS=`echo $CLANG_ARGS | perl -p -e 's/-MT .*?\.lo//g; s/-o .*?\.[do]\s/ /g;  s/-MM //g; s/-x [^ ]* / /g;'`
REAL_SRC=`echo $ARGS | perl -p -e 's/(.*) ([^ ]*)\.c(.*|$)/\2/;'`
echo "In directory: " `pwd`
echo "Compiler args are: " $ARGS
/usr/bin//rosecheckers $PROCESSED_ARGS
/usr/bin/g++ $ARGS
