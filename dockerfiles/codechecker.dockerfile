# This file installs CodeChecker

# To build, use this command in directory above this one:
# docker  build -f Dockerfile.codechecker  -t ghcr.io/cmu-sei/redemption-codechecker  .

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


FROM ghcr.io/cmu-sei/redemption-prereq

# Apt packages
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
         pipx python3-dev python3-psutil g++ libpcre3-dev jq \
    && apt-get --purge -y autoremove \
    && apt-get clean

RUN pipx install codechecker && pipx inject codechecker setuptools \
    && jq '.runtime.analyzers["clang-tidy"] = "clang-tidy-16"' < /root/.local/share/pipx/venvs/codechecker/share/codechecker/config/package_layout.json > package_layout.json \
    && mv package_layout.json /root/.local/share/pipx/venvs/codechecker/share/codechecker/config/

ENV PATH=/root/.local/bin:$PATH

# Cppcheck 2.9
RUN wget https://github.com/danmar/cppcheck/archive/refs/tags/2.9.tar.gz \
    && tar xzf 2.9.tar.gz \
    && rm 2.9.tar.gz \
    && cd cppcheck-2.9 \
    && mkdir /usr/share/cppcheck \
    && make MATCHCOMPILER=yes FILESDIR=/usr/share/cppcheck HAVE_RULES=yes install \
    && cd .. \
    && rm -rf cppcheck-2.9

CMD ["/bin/bash"]
