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
from brainstem import get_deepest_qual_type

def test_empty_node():
    node = {}
    assert get_deepest_qual_type(node) == {}

def test_node_with_no_qualType_or_type():
    node = {
        "key1": "value1",
        "key2": {
            "key3": "value3"
        }
    }
    assert get_deepest_qual_type(node) == node

def test_node_with_top_level_qualType():
    node = {
        "qualType": {"key": "value"}
    }
    assert get_deepest_qual_type(node) == {"key": "value"}

def test_node_with_nested_qualType():
    node = {
        "qualType": {
            "qualType": {
                "qualType": {"key": "value"}
            }
        }
    }
    assert get_deepest_qual_type(node) == {"key": "value"}

def test_node_with_mixed_qualType_and_type():
    node = {
        "qualType": {
            "type": {
                "qualType": {
                    "type": {"key": "value"}
                }
            }
        }
    }
    assert get_deepest_qual_type(node) == {"key": "value"}

def test_node_with_deepest_type():
    node = {
        "qualType": {
            "type": {
                "key": "value"
            }
        }
    }
    assert get_deepest_qual_type(node) == {"key": "value"}

def test_node_with_nested_non_dict_qualType():
    node = {
        "qualType": {
            "qualType": "value"
        }
    }
    assert get_deepest_qual_type(node) == {"qualType": "value"}

# To run these tests, use the following command in your terminal:
# pytest -v your_test_file.py
