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

import os
import shutil
import argparse

# a helper script for copying working files from host to docker-ready folder
# and then copying from this directory into docker (from inside the container)
# for rebuilding clang without having to completely build from scratch

# USAGES:
# python3 copy.py --from-base=C:/Precision/projects/llvm-project --to-dir=.
# python3 copy.py --from-dir=. --to-base=/opt/clang

# List of predetermined header and implementation files
header_files = [
    'ASTNodeTraverser.h',
    'TextNodeDumper.h',
    'JSONNodeDumper.h' 
]

implementation_files = [
    'TextNodeDumper.cpp',
    'JSONNodeDumper.cpp'
]

# Fixed paths
header_path = 'clang/include/clang/AST'
implementation_path = 'clang/lib/AST'

def copy_from_base(base_directory, destination_directory):
    # Copy header files
    for file_name in header_files:
        src_path = os.path.join(base_directory, header_path, file_name)
        dest_path = os.path.join(destination_directory, file_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")
        else:
            print(f"File {src_path} does not exist")

    # Copy implementation files
    for file_name in implementation_files:
        src_path = os.path.join(base_directory, implementation_path, file_name)
        dest_path = os.path.join(destination_directory, file_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")
        else:
            print(f"File {src_path} does not exist")

def copy_to_base(source_directory, base_directory):
    # Copy header files
    for file_name in header_files:
        src_path = os.path.join(source_directory, file_name)
        dest_path = os.path.join(base_directory, header_path, file_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")
        else:
            print(f"File {src_path} does not exist")

    # Copy implementation files
    for file_name in implementation_files:
        src_path = os.path.join(source_directory, file_name)
        dest_path = os.path.join(base_directory, implementation_path, file_name)
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")
        else:
            print(f"File {src_path} does not exist")

def main():
    parser = argparse.ArgumentParser(description='Copy predetermined files to/from a base directory.')
    parser.add_argument('--from-base', type=str, help='Base directory to copy files from.')
    parser.add_argument('--to-dir', type=str, help='Destination directory to copy files to.')
    parser.add_argument('--from-dir', type=str, help='Source directory to copy files from.')
    parser.add_argument('--to-base', type=str, help='Base directory to copy files to.')

    args = parser.parse_args()

    if args.from_base and args.to_dir:
        copy_from_base(args.from_base, args.to_dir)
    elif args.from_dir and args.to_base:
        copy_to_base(args.from_dir, args.to_base)
    else:
        print("Invalid arguments. Use --from-base and --to-dir OR --from-dir and --to-base.")

if __name__ == "__main__":
    main()
