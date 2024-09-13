#!/bin/sh

# To be called after containers are built

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


docker run --rm  -v ${PWD}:/host  --workdir /host  ghcr.io/cmu-sei/redemption-prereq \
       rm junit.basic.xml junit.oss.xml junit.clang.xml
echo cleaned

docker run --rm  -v ${PWD}:/host  --workdir /host/code/acr/test  ghcr.io/cmu-sei/redemption-prereq \
       pytest --verbose --junit-xml=junit.basic.xml
echo basic pytest done

docker run --rm  -v ${PWD}:/host  --workdir /host/code/acr/test/ast  ghcr.io/cmu-sei/redemption-prereq \
       pytest --verbose --junit-xml=junit.clang.xml -s ast_comparer.py --config scenarios.json
echo clang pytest done

docker run --rm  -v ${PWD}:/host  --workdir /host/code/acr/test/ast  ghcr.io/cmu-sei/redemption-prereq \
       pytest --verbose --junit-xml=junit.clang.xml -s ast_comparer.py --config scenarios_legacy_ast.json
echo clang pytest done

docker run --rm  -v ${PWD}:/host  --workdir /host/data/test  ghcr.io/cmu-sei/redemption-test \
       pytest --verbose --junit-xml=junit.oss.xml
echo oss pytest done
