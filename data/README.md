# Automated Code Repair Data

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

This is the data used by this project.
Much of this data is referenced in our paper "Using Automated Code Repair to Fight Back the Deluge of False Positives".
See the `README.dataset.md` file for details about that data.

## About the Dataset

The dataset will be a Zip file with the following directory contents:

`data.publication`
  `README.md`: use `data/README.dataset.md`
  `Dockerfile.rosecheckers`: for conveniently constructing a container to use with codebases and tools (NOTE: Do not use clang-tidy from this container, it is an older version than what we used.)
  `Dockerfile.redemption`: for conveniently contstructing a container to use with clang-tidy version 15
  `codebases.yml`
  `data`: `redemption/data` directory minus some files noted below
  `paper/oss_frequency.csv`: table `redemption/paper/oss_frequency.csv`
  `paper/tables`: `redemption/paper/tables` directory minus some `redemption/paper` files noted below
  `code/analysis`: from the `redemption/code/analysis` directory, only include the following files: `cert_rules.2016.tsv`, checkers.csv, `my-gcc.sh`, `my-g++.sh`, `{clang_tidy,cppcheck,rosecheckers}_oss2tsv.py`
  `LICENSE.txt`: license `redemption/License.dataset.txt`
  `ABOUT`: per-file markings `redemption/ABOUT.dataset`

## Other Files

These are files and directories not included in the published dataset.

### `accolade.zeek4.csv`

The `accolade.zeek4` file contains info relevant to Zeek v4, which came from our collaborator; it is CUI-derived data, so it should not be published.
It contains CUI-derived data. Writeup said the following:

header: "CERT Guidelines Ranked by Effort Worthiness for This Project"

The raw table lives in `accolade.csv`. The tables in the paper contain this data reformatted to fit the page.

This table was generated manually based on the "Excerpt of Per-CERT-Rule Alert Counts and Related Data for Tools and Codebases Used}" table. Each rule that had a non-empty rank column was added to this table. This table also does coalesce information about zeek4 from our collaborator's data (which is CUI and not provided).

### `zeek4` directory

Data related to `zeek4`. CUI...comes from Brandon.

### `zeek5` directory

Data related to `zeek5`. CUI...comes from Brandon.

### `scan-build` directory

Data related to the `scan-build` SA tool. Format similar to `clang-tidy`, `rosecheckers`, `cppcheck`. `Scan-build` turned out to be less useful than `clang-tidy`.

### `test` directory

Data and scripts related to testing our ACR tool on git and zeek. Not useful for our paper.

### `join_pivot.sql`

I?IRC I used this script to join some of the pivot tables when creating `all_alerts.csv`.

### Latex and IEEE -specific files

We exclude Latex, IEEE, and figure files that were used for the paper from the dataset release. From the `redemption/paper` directory, the dataset excludes files `accolade.org`, `IEEEtran.bst`, `IEEEtran.cls`, `makefile`, `mathmode-spacing.tex`, `paper.md`, `paper.tex`, `refs.bib`, plus it excludes all files from the `redemption/figs` directory.

### Delete these files from the dataset for publication

Since the one `README` file needed is in the top-level directory of the publication dataset, you should make sure these files are deleted from the publication dataset: `data/README.md` and `data/README.dataset.md`
