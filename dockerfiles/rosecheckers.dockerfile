# This file builds enough tools into a Linux distro to be useful for
# general software building.

# To build, use this command in directory above this one:
# docker  build -f Dockerfile.rosecheckers  -t ghcr.io/cmu-sei/redemption-rosebud  .

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


FROM ghcr.io/cmu-sei/cert-rosecheckers/rosebud:latest

# Apt packages
RUN apt update \
    && DEBIAN_FRONTEND=noninteractive apt -y install --no-install-recommends \
         pkg-config software-properties-common tzdata build-essential \
    && apt --purge -y autoremove \
    && apt clean
# Python3 (pip)
RUN apt update \
    && DEBIAN_FRONTEND=noninteractive apt -y install --no-install-recommends \
        python3-pip python3-dev python3-pytest \
    && apt --purge -y autoremove \
    && apt clean
RUN pip3 install --no-cache-dir --upgrade pip
# Misc others
RUN apt update \
    && DEBIAN_FRONTEND=noninteractive apt -y install --no-install-recommends \
        autoconf automake libtool \
        bash-completion \
        clang-8 clang-tools clang-tidy llvm-8 llvm-8-dev \
        cmake git \
        zip unzip \
        wget curl \
        inetutils-ping sqlite3 \
        ctags bear gettext \
    && apt --purge -y autoremove \
    && apt clean
RUN cp /usr/bin/clang-8 /usr/bin/clang && \
    ln -s /usr/include/llvm-8/llvm /usr/include && \
    ln -s /usr/include/llvm-c-8/llvm-c /usr/include
ENV clang=/usr/bin/clang-8
ENV llvm_dis=/usr/bin/llvm-dis-8
ENV llvm_opt=/usr/bin/opt-8

# Meson / ninja
RUN python3 -m pip install --upgrade pip && \
    pip3 install meson ninja GitPython pyaml && \
    add-apt-repository ppa:rmescandon/yq && \
    apt install yq

# Cppcheck 2.9
RUN wget https://github.com/danmar/cppcheck/archive/refs/tags/2.9.tar.gz \
    && tar xzf 2.9.tar.gz \
    && rm 2.9.tar.gz \
    && cd cppcheck-2.9 \
    && mkdir /usr/share/cppcheck \
    && make MATCHCOMPILER=yes FILESDIR=/usr/share/cppcheck HAVE_RULES=yes install \
    && cd .. \
    && rm -rf cppcheck-2.9

# COPY bashrc.sh /root/.bashrc

RUN mkdir /datasets

WORKDIR /host

CMD ["/bin/bash"]
