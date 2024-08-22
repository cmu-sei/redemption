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

import pytest
import sys

sys.path.append('/host/code/acr')
from brainstem import combine_qual_details

def test_empty_node():
    node = {}
    assert combine_qual_details(node) == []

def test_node_with_no_qualDetails():
    node = {
        "key1": "value1",
        "key2": {
            "key3": "value3"
        },
        "key4": [
            {"key5": "value5"},
            "value6"
        ]
    }
    assert combine_qual_details(node) == []

def test_node_with_top_level_qualDetails():
    node = {
        "qualDetails": ["detail1", "detail2"]
    }
    assert combine_qual_details(node) == ["detail1", "detail2"]

def test_node_with_nested_qualDetails():
    node = {
        "key1": {
            "qualDetails": ["detail1"]
        },
        "key2": {
            "key3": {
                "qualDetails": ["detail2", "detail3"]
            }
        }
    }
    assert combine_qual_details(node) == ["detail1", "detail2", "detail3"]

def test_node_with_mixed_qualDetails():
    node = {
        "qualDetails": ["detail1"],
        "key1": {
            "qualDetails": ["detail2"]
        },
        "key2": {
            "key3": {
                "qualDetails": ["detail3", "detail4"]
            }
        },
        "key4": [
            {"qualDetails": ["detail5"]},
            "value6",
            {"key5": {"qualDetails": ["detail6"]}}
        ]
    }
    assert combine_qual_details(node) == ["detail1", "detail2", "detail3", "detail4", "detail5", "detail6"]

def test_node_with_empty_qualDetails():
    node = {
        "qualDetails": [],
        "key1": {
            "qualDetails": []
        },
        "key2": {
            "key3": {
                "qualDetails": []
            }
        },
        "key4": [
            {"qualDetails": []},
            "value6",
            {"key5": {"qualDetails": []}}
        ]
    }
    assert combine_qual_details(node) == []
