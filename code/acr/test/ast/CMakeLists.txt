# <legal>
# 'Redemption' Automated Code Repair Tool
# Copyright 2023, 2024 Carnegie Mellon University.
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
# INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
# UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
# AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
# PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
# THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
# KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
# INFRINGEMENT.
# Licensed under a MIT (SEI)-style license, please see License.txt or
# contact permission@sei.cmu.edu for full terms.
# [DISTRIBUTION STATEMENT A] This material has been approved for public
# release and unlimited distribution.  Please see Copyright notice for
# non-US Government use and distribution.
# This Software includes and/or makes use of Third-Party Software each
# subject to its own license.
# DM23-2165
# </legal>

# a quick way to output compile_commands.json for a test file
# cmake -DFILE_TO_COMPILE=test-file.c .

cmake_minimum_required(VERSION 3.21)

project(red-ast)

# force compile commands
set( CMAKE_EXPORT_COMPILE_COMMANDS ON )

# if there are includes, then you should make a proper project for your tests
add_executable( ${PROJECT_NAME} ${FILE_TO_COMPILE} )
