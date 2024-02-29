# Brain Architecture
## Copyright
<legal>
'Redemption' Automated Code Repair Tool
Copyright 2023, 2024 Carnegie Mellon University.
NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
INFRINGEMENT.
Licensed under a MIT (SEI)-style license, please see License.txt or
contact permission@sei.cmu.edu for full terms.
[DISTRIBUTION STATEMENT A] This material has been approved for public
release and unlimited distribution.  Please see Copyright notice for
non-US Government use and distribution.
This Software includes and/or makes use of Third-Party Software each
subject to its own license.
DM23-2165
</legal>

## ASTContext

The `ASTContext` is a wrapper for an AST object.  It behaves just as if
it is the existing dictionary/sequence mapping we currently use to
represent JSON objects.  But adds several facilities to make it more
useful for navigating the AST.

* The `ASTContext` maintains a history of the path used to reach any
  particular node, which can be traced by using its `parent()` method.
  
* The `ASTContext` allows direct access to global information via
  Python's attribute mechanism.

* The `ASTContext` contains methods that more easily access AST-specific
  information from the tree, such as line/column information.

## Alert Objects

An `Alert` object contains both the alert information from the
existing JSON alert format and the logic for locating and remediating
an alert.

## Repair Algorithm

First, walk through the AST, building an interval list.  Next, go to
each alert and find its location in the interval list.  This results
in a node or list of nodes, which are then passed to the alert's
`attempt_repair` and `attempt_patch` methods.

The intent is for this to always result in a node that is a suitable
locus from which the alert can locate the relevant AST node that it
needs to operate upon.

In the current version, some added complications have been added to
this to replicate the old brain behavior as closely as possible.  In
particular, it currently makes a distinction between an exact line/col
range beginning match and a match that only occurs in the middle of an
interval.  In the former case, we individually handle all matching
intervals, from largest to smallest, allowing overwrites as in the Old
Method.



