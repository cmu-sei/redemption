#!/bin/sh

# To be called after containers are built

# <legal>
# 'Redemption' Automated Code Repair Tool
# 
# Copyright 2023 Carnegie Mellon University.
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


docker run --rm  -v ${PWD}:/host  --workdir /host  docker.cc.cert.org/redemption/prereq \
       rm junit.basic.xml junit.oss.xml ; \
       echo cleaned

docker run --rm  -v ${PWD}:/host  --workdir /host/code/acr/test  docker.cc.cert.org/redemption/prereq \
       pytest --junit-xml=junit.basic.xml ; \
       echo basic pytest done

docker run --rm  -v ${PWD}:/host  --workdir /host/data/test  docker.cc.cert.org/redemption/test \
       pytest --junit-xml=junit.oss.xml ; \
       echo oss pytest done
