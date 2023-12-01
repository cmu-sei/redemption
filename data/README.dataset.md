# Dataset Data Documentation

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

This includes all data needed to replicate and validate our frequency analysis of static analysis (SA) alerts produced using open-source SA tools on several OSS codebases. It includes instructions how to get and run the SA tools, a Dockerfile to conveniently get and use the SA tools, raw SA tool output, parsed SA data and aggregate analyses, and SA data augmented with CERT rule and CWE data.

This data is referenced in our paper "Using Automated Code Repair to Fight Back the Deluge of False Positives" (not yet published at time of this dataset publication).

What follows is the dataset file structure and instructions to generate the data.

Use Docker version 20 or greater.

## File structure

`data.publication`: top level directory
  `README.md`: instructions and information
  `Dockerfile.rosecheckers`: for conveniently constructing a container to use with codebases and tools (NOTE: Do not use clang-tidy from this container, it is an older version than what we used.)
  `Dockerfile.redemption`: for conveniently contstructing a container to use with clang-tidy version 15
  `codebases.yml`: information about the codebases including download location, version, and compilation instructions
  `paper/oss_frequency.csv`: table 
  `paper/tables`: tables
  `data`: data
  `code/analysis`: static analysis tool outputs
  `LICENSE.txt`: license
  `ABOUT`: per-file markings

## Setup

First, build both Docker containers. Then run the first one.

``` shell
docker build -f Dockerfile.rosecheckers -t data_container .
docker run -it --rm -v ${PWD}:/host -v ${PWD}/datasets:/datasets  -w /host data_container bash
```

``` shell
docker build -f Dockerfile.redemption  -t clang_tidy_data_container .
docker run -it --rm -v ${PWD}:/host -v ${PWD}/datasets:/datasets  -w /host clang_tidy_data_container bash
```

All remaining instructions pertain to inside the `data_container` (the first container), *except* for the instructions for `clang_tidy`. Those instructions are to be done inside the `clang_tidy_data_container` (the second container).

The `codebases.yml` file contains information about where to download and build the three codebases (dos2unix, git, zeek). The container supports `git` and `wget`.

Both Dockerfiles create a shared-volume directory `/datasets` within the container where you will put your downloads of all the specified codebases. That new directory is accessible outside the container as `datasets` located in the base directory.

We provide detailed instructions for reproducing the data pertaining to dos2unix. For git and zeek, you can reproduce them using the general guidance from `codebases.yml`, as well as documentation on the static analysis tools, which live in the locations: `/host/data/$TOOL/$TOOL.md`.

For `dos2unix`, after doing a `wget` to get the specified version of `dos2unix`, you should move that into a different directory, as follows: `mkdir /datasets/dos2unix; mv /datasets/dos2unix-7.4.3/* /datasets/dos2unix`.

For each tool, you may need to install additional dependencies...see the `codebases.yml` file for info. For dos2unix, this is just the `po4a` package:

``` shell
apt update
apt install po4a
```

## Creating raw SA tool outputs

There are already raw output files in `data/$TOOL/$CODEBASE/$TOOL.txt` (or `.xml`), such as `data/cppcheck/dos2unix/cppcheck.xml`. These instructions describe how to recreate them for dos2unix.

### `compile_commands.json`

This is a file that contains information about a codebase's build process. This file is required by `clang-tidy` and can also be used by `cppcheck` (though not required), You can create it yourself for each project, or you can use the `data/compile_command.${TOOL}.json` files in this directory. 

The file is created by a utility called `bear` that lives in each container. There's a different version of `bear` in each container, so if you run it you will need to run it separately as specified below, immediately prior to running `clang-tidy` or `cppcheck` in that container. You should prepend `bear` to your project's build command for building with clang.  The `codebases.yml` file contains instructions for generating this file for each tool...look under the `clang-tidy` heading. To use `bear`, run it in the base directory for the codebase.

Note 1: The dos2unix `compile_commands.json` will differ slightly from the provided file, in that the filepaths in the provided file start with `/datasets/dos2unix-7.4.3` but the filepaths in your file will start `/datasets/dos2unix`. If you had left the files in `/datasets/dos2unix-7.4.3`, the `compile_commands.json` file would be exactly the same as provided here. However, to match the provided static analysis output files' paths for the steps below, you should move the files as directed above.

Note 2: Assuming you clone the `git` repository into the `/datasets` directory on the container also, there will be a slight difference. Filepaths output from `bear` for `git` in the provided `.json` file will start with `/oss` instead of `/datasets`, but that should be the only difference in your `bear` output.

### Clang-tidy

Output from this tool lives in the `data/clang-tidy/${CODEBASE}/clang-tidy.txt` files.

The `codebases.yml` file contains instructions for generating output for each tool. For these, you must use the `bear` utility (in `clang_tidy_data_container`) to create a `compile_commands.json` file.  In the container `clang_tidy_data_container`, you should run the following commands from the `/datasets/dos2unix` directory.

``` shell
make clean
bear -- make DOS2UNIX_AUTHOR=nobody CC=clang dos2unix
clang-tidy -checks='*' querycp.c  dos2unix.c  common.c  > clang-tidy.txt
```

The `clang-tidy` SA tool runs quickly on dos2unix.

For more information see `data/clang-tidy/Clang-tidy.md`.

Note: These raw output files may have slight differences from the provided files (in some cases timestamps or file paths). The important thing is that the alerts are the same, which you'll observe when you convert to `.tsv` files (next step below, after running all the static analysis tools).

### Cppcheck

Output from this tool lives in the `data/cppcheck/${CODEBASE}/cppcheck.xml` files.

For dos2unix, do NOT run `bear` first. Instead, run these commands:

``` shell
cppcheck --enable="all" --language="c" --force --xml ${PWD} 2> cppcheck.xml
grep -v ccls-cache cppcheck.xml > foo ; mv foo cppcheck.xml
```

For git and zeek, you should run the specified `bear` command and then the specified `cppcheck` command from the `/datasets/${CODEBASE}` directory.

For example, to run the `bear` command for `git`, run the following commands from the `/datasets/git` directory. (Note that this bear command does not include  `--`)

``` shell
make clean
bear make PAGER_ENV=dummy CC=clang git
```

The actual Cppcheck command will be something like this:

``` shell
cppcheck --enable="all" --force --xml  --project=compile_commands.json  2> cppcheck.xml
```

Running `cppcheck` on dos2unix took about 90 minutes to complete on our powerful testing machine, despite it only analyzing 3 C files. Similarly, running `cppcheck` on zeek took 8 days.

For more information see `data/cppcheck/Cppcheck.md`.

### Rosecheckers

Output from this tool lives in the `rosecheckers/${CODEBASE}/rosecheckers.txt` files.

You can substitute  `/host/code/analysis/my-gcc.sh` for GCC to run Rosecheckers analysis while building the code. Use the `-k` argument with `make` so that it does not error out prematurely. The example below includes a `make clean` so that dos2unix will rebuild as required.

``` shell
make clean
make DOS2UNIX_AUTHOR=nobody  CC=/host/code/analysis/my-gcc.sh  dos2unix  > rosecheckers.txt  2>&1
perl -p -i -e 's@/datasets/dos2unix@@;'  rosecheckers.txt
```

The `Rosecheckers` SA tool runs fast, taking only seconds to run on dos2unix.

For more information see `data/rosecheckers/CERT-Rosecheckers.md`.

### Converting SA tool output to alerts (.tsv) files

Output from this process lives in the `${TOOL}/${CODEBASE}/${TOOL}.tsv` files.

For each SA tool, there is a parsing script in `/host/code/analysis/${TOOL}_oss2tsv.py` that generates a TSV (tab-separated values) file of alerts from raw SA tool output.

For example, for dos2unix and `clang_tidy`, run these commands:

``` shell
cd /datasets/dos2unix
python3 /host/code/analysis/clang_tidy_oss2tsv.py clang-tidy.txt clang-tidy.tsv
```

Ensure the first line of the TSV file has the following headers:

    Checker\tPath\tLine\tMessage

Add that line, using a `sed` command as in the following example for `clang-tidy`:

``` shell
sed -i  '1i Checker\tPath\tLine\tMessage' clang-tidy.tsv
```

### Associating SA tool output with CERT rules

Output from this process lives in the `${TOOL}/${CODEBASE}/${TOOL}.csv` files.

This process associates each alert with a CERT guideline associated with it, or NONE if no guideline qualifies. Run the SQLite interpreter (`sqlite3`).

``` sql
.mode tabs
.header on
.import clang-tidy.tsv Data
.mode csv
.import /host/code/analysis/checkers.csv  Checkers
.output clang-tidy.csv
SELECT * FROM Data, Checkers WHERE Data.Checker = Checkers.checker;
.exit
```

For `dos2unix`, the resulting `.csv` files should be exactly the same as those provided in `/host/data/${TOOL}/${CODEBASE}/${TOOL}.csv` except that `clang-tidy.csv` filepaths differ in that they begin with `/host`.

### Constructing CERT rule pivot tables

Output from this process lives in the `data/${TOOL}/${CODEBASE}/${TOOL}_pivot.csv` files.

In this process you create a pivot table from the CSV file, with rules for rows, and the cells have a count of lines or alerts (which should produced the same value).

## Creating frequency tables

### Excerpt of Per-CERT-Rule Alert Counts and Related Data for Tools and Codebases Used

The raw table lives in `data/all_alerts.csv`. The table in the paper has a subset of these columns and rows (all rows removed lacked 'yes' in the Repairable column).

The table in `all_alerts.csv` is effectively an SQL-style join between all of the pivot tables. It also joins the CERT guideline info, which is available at `/host/code/analysis/cert_rules.2016.tsv`.  Each 'rank' column was created by sorting the table by decreasing numeric order on the appropriate column, and then numbering the first 10 rows (that had the highest numbers).  The Repairable column was filled in by hand.

### `EXP34-C.csv` and `shorter.EXP34-C.csv`

These CSV files have data used for null-pointer alert analysis.

The `EXP34-C.csv` file was created from the various non-pivot csv files, with the Error and Verdict columns' data added manually. We also added a `Codebase` and `Tool` columns to reflect the codebase and tool involved.

The raw table lives in `EXP34-C.csv`. The table in the paper, `shorter.EXP34-C.csv`, has a subset of these columns and rows. (Due to space limits, not all rows could be included in the paper. All rows removed lacked '???' in the Error column)

### `accolade.csv`

The `accolade.csv` file contains SEI generated data for this project. It contains CERT Guidelines ranked by effort worthiness for this project.

The raw table lives in `accolade.csv`. Tables in the paper contain this data reformatted to fit the page (`PRIMARY CERT GUIDELINES RANKED BY EFFORT WORTHINESS`, `OTHER CERT GUIDELINES RANKED BY EFFORT WORTHINESS`, and `SECONDARY CERT GUIDELINES RANKED BY EFFORT WORTHINESS`).

