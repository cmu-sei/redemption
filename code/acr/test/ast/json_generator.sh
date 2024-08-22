#!/bin/bash
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

# docker example : ./json_generator.sh . c
# nhr dev example: 
#   ./json_generator.sh . c /c/Precision/projects/llvm-project/build/MinSizeRel/bin

# Directory containing source files
SOURCE_DIR=$1
# File extension to match
EXTENSION=$2

# use the default modified clang in docker version
# unless the user specifies a different one
CLANG=/opt/clang/build/bin
CLANG_OPT=$3

POSTFIX=""
POSTFIX_OPT=$4

if [ -n "$CLANG_OPT" ]; then
  echo "clang: $CLANG_OPT"
else
  echo "default clang: $CLANG"
  CLANG_OPT=$CLANG
fi

if [ -n "$POSTFIX_OPT" ]; then
  echo "postfix: $POSTFIX_OPT"
else
  echo "postfix: n/a"  
fi

# Iterate over each file with the specified extension
for file in "$SOURCE_DIR"/*."$EXTENSION"; do
  # Check if the file exists
  if [ -f "$file" ]; then
    # Extract file name without extension
    filename=$(basename "$file" .$EXTENSION)
    # Run clang command using the specified clang version
    $CLANG_OPT/clang -fsyntax-only -Xclang -ast-dump=json "$file" > "$SOURCE_DIR"/"$filename""$POSTFIX_OPT".json

    # use the unmodified version
    # clang -fsyntax-only -Xclang -ast-dump=json "$file" > "$SOURCE_DIR"/"$filename"-orig.json
    echo "Generated JSON file for $file"
  fi
done
