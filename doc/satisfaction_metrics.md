# Satisfaction Metrics

<legal>  
'Redemption' Automated Code Repair Tool  
  
Copyright 2023 Carnegie Mellon University.  
  
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

The goal of this project is to satisfactorily repair one-half (50%) of all SA alerts.

We have decided that repairing 80% of alerts in each bucket (where a bucket represents a SA tool on a codebase) that we strive to repair should work, based on our past SCALe audit data. Due to resource limitations, we elected to repair 3 CERT rules for FY23 and 7 more rules for FY24 for a total of 10 rules.

To repair 50% of all alerts, we need to pick 10 rules that cover 62.5% of all alerts. This means repairing 80% of 62.5% of alerts == repairing 50% of alerts.

## Redemption Example Statistics

We currently have buckets based on repairing two codebases (git, zeek5) with three SA tools (cppcheck, clang-tidy, CERT rosecheckers).

As you can see from the [satisfaction statistics](./satisfaction_stats.csv), the 10 rules that we elected to fix yield the following percentages for each bucket of repaired alerts to total alerts. We also computed how much benefit we would get from repairing the "next 7 CERT rules", for a total of 17 rules repaired.

| Code  | Tool         | Top 10 % | Top 17 % |
|-------|--------------|----------|----------|
| git   | cppcheck     | 68.1     | 80.7     |
| zeek5 | cppcheck     | 64.6     | 72.2     |
| git   | clang-tidy   | 65.6     | 70.7     |
| zeek5 | clang-tidy   | 52.3     | 56.3     |
| git   | rosecheckers | 23.5     | 38.1     |
| zeek5 | rosecheckers | 14.8     | 42.7     |

Clearly rosecheckers has lower ratios than the other SA tools. But this means that if we ignore rosecheckers, the repair ratios for clang-tidy and cppcheck average to 62.65%, just slightly greater than the 62.5% we need to repair 50% of alerts.

We can also see that repairing the 11th-to-17th rules will have less of an impact than repairing the top 10. Still they will have some impact, and would be worthwhile if we had the available effort.  In future work, we can consider repairing these rules, although it would probably be worthwhile to redo this analysis for the code + tool buckets suggested by future collaborators.

## Generalizing the Analysis

We can apply this analysis to any codebase + SA tool pair that a collaborator might suggest.  We simply run the SA tool on the codebase, and map its alerts to CERT rules.  Ideally, the 10 rules we support would tackle >=62.5% of alerts. If they do not, we could perhaps add repairs for more rules to reach 62.5% of alerts.
