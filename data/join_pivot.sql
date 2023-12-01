-- To use this script, you should have two files A.csv and B.csv, both should have a field named 'Rule'
-- <legal>
-- 'Redemption' Automated Code Repair Tool
-- 
-- Copyright 2023 Carnegie Mellon University.
-- 
-- NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING
-- INSTITUTE MATERIAL IS FURNISHED ON AN 'AS-IS' BASIS. CARNEGIE MELLON
-- UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
-- AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR
-- PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF
-- THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY
-- KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT
-- INFRINGEMENT.
-- 
-- Licensed under a MIT (SEI)-style license, please see License.txt or
-- contact permission@sei.cmu.edu for full terms.
-- 
-- [DISTRIBUTION STATEMENT A] This material has been approved for public
-- release and unlimited distribution.  Please see Copyright notice for
-- non-US Government use and distribution.
-- 
-- This Software includes and/or makes use of Third-Party Software each
-- subject to its own license.
-- 
-- DM23-2165
-- </legal>

.mode csv
.headers on
.import A.csv  A
.import B.csv  B
SELECT B.Rule, A.*, B.* FROM B LEFT JOIN A USING (Rule) UNION ALL SELECT A.Rule, A.*, B.* FROM A LEFT JOIN B USING (Rule) WHERE B.Rule IS NULL ;
