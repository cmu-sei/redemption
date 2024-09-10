# This file builds enough tools into a Linux distro to be useful for
# general software building.

# To build, use this command in directory above this one:
# docker  build -f dockerfiles/focal.prereq.dockerfile  -t ghcr.io/cmu-sei/redemption-prereq:focal  .

# To correct the time zone, run:
# dpkg-reconfigure tzdata

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

FROM ubuntu:focal

# Apt packages
RUN apt-get update \
    && apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
         clang make autoconf zip wget curl git gnupg ca-certificates tzdata \
         software-properties-common \
    && apt-get --purge -y autoremove \
    && apt-get clean

# Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa -y

RUN apt-get update \
    && apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
         python3.11 python3.11-distutils \
        && apt-get --purge -y autoremove \
    && apt-get clean
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Pip
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python \
    && pip install --upgrade pip \
    && pip install pytest pyyaml


# # Other packages
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
         bear sqlite3 po4a iputils-ping iputils-tracepath patchutils \
         ninja-build lld zlib1g-dev libtinfo-dev libxml2-dev lsb-release \
         cmake \
        && apt-get --purge -y autoremove \
    && apt-get clean

#####################################################################
#
# add certificates required before cloning
#
#####################################################################

# The latest Cmake
# RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null \
#     && apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main" \
#     && apt-get update \
#     && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
#          kitware-archive-keyring \
#     && rm /etc/apt/trusted.gpg.d/kitware.gpg \
#     && apt-get update  \
#         && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends \
#          cmake \
#     && apt-get --purge -y autoremove \
#     && apt-get clean


# if you receive any git-related errors due to certs then add your
# org's certs here
COPY cert/* /usr/local/share/ca-certificates/
RUN /usr/sbin/update-ca-certificates

#####################################################################
#
# modified clang based on 15.0.7
#
#####################################################################
RUN mkdir /opt/clang && \
    git clone --depth=1 --branch llvmorg-15.0.7 https://github.com/llvm/llvm-project.git /opt/clang

# modified AST traverser required to be compiled into clang. this file exists within
# the redemption code base
COPY /code/clang/*.h /opt/clang/clang/include/clang/AST/
COPY /code/clang/*.cpp /opt/clang/clang/lib/AST/

RUN mkdir /opt/clang/build && \
    cmake -G Ninja -S/opt/clang/llvm -B/opt/clang/build -DLLVM_ENABLE_PROJECTS="clang;lldb" -DLLVM_ENABLE_RUNTIMES="libcxx;libcxxabi" -DLLVM_USE_LINKER=lld -DLLVM_BUILD_TESTS=OFF -DLLVM_TARGETS_TO_BUILD="X86" -DLLVM_BUILD_EXAMPLES=OFF -DLLVM_INCLUDE_EXAMPLES=OFF -DLLVM_LIBDIR_SUFFIX=64 -DCMAKE_BUILD_TYPE=Release
RUN ninja -C /opt/clang/build
RUN ln -s /opt/clang/build/bin/opt /opt/clang/build/bin/opt-15
ENV PATH=/opt/clang/build/bin:$PATH

# clang is built in /opt/clang/build/bin

CMD ["/bin/bash"]

# code/acr/SortedCollection.py was manually downloaded from
#   https://code.activestate.com/recipes/577197-sortedcollection/
#   License: MIT
