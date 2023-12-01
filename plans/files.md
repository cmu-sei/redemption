# How Files are Organized in This Project

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

All of the files in your local redemption directory can be partitioned as follows:

## Files not known to Git

The `git status` command will list all files that Git does not know about. (If Git knows nothing about all of the files in a directory, it will list that directory as unknown.)

## Files that Git intentionally ignores

The `.gitignore` file contains glob patterns to indicate all files ignored by Git.

## Files known to Git

You can browse these files at the appropriate Bitbucket location:
https://bitbucket.cc.cert.org/bitbucket/projects/REM/repos/redemption/browse

One thing our software should contain is a manifest file. This is merely a listing of every file in our codebase that should go into a release. It can therefore also be used to identify files that are not part of the software.  We could also have multiple manifest files if we make multiple releases including different subsets of files.

The following command creates a manifest listing every file in the directory, excluding files in .git:

(All commands should be executed in the top-level `redemption` directory)

```shell
find . -path ./.git -prune -o -type f -print | LC_ALL=C sort > manifest.txt
```

The file can then be manually edited in any text editor.

If you edit the file, please re-sort the file. While not strictly necessary, keeping the file sorted will help keep it organized as well as preventing duplicate files.

Consequently all the files in Git can be partitioned as follows:

#### Files not in the manifest

These files do not get released.

To list every file in your local `redemption` directory that is not in the manifest:

```shell
find . -path ./.git -prune -o -type f \( -exec grep -Fqx '{}' manifest.txt \; -o -print \)
```

This includes all files not known to Git. For files known to Git, execute this command after checking out a fresh copy of the project.

To remove every file in your local `redemption` directory that is not in the manifest:

```shell
find . -path ./.git -prune -o -type f \( -exec grep -Fqx '{}' manifest.txt \; -o -execdir rm '{}' \; \)
```

#### Files in the manifest

These files do get released. They also get tested by our CI system.

Most of the files that are human-readable must be adorned with copyright statements. This is accomplished by the `update_copyright.py` script.  Each file that needs a copyright must have the following tags: `<legal></legal>`. These tags should be 'commented-out' using the file's convention for comments. The update_copyright script injects the current copyright test inside these `<legal>` tags. The copyright text lives in the `ABOUT` file.

If you create a new human-readable file, you should endow it with `<legal></legal>` tags, near the top of the file. Generally, the tags should go after the title, or after a comment indicating what the file is.

Consequently all the files in the manifest can be partitioned as follows:

##### Non-human-readable files

These files are indicated by their suffix (.e.g. `jpeg`, `mp3`, etc)

##### Files with legal tags

The `grep` command can tell you which files have `<legal>` tags.

##### Files that need not contain legal tags

The `update_copyright.py` script currently lists a set of files that could (in theory) have `<legal>` tags but do not need them.

##### Files that should have legal tags but don't

If a file is human-readable, lacks `<legal>` tags, and is not listed as exempt from `<legal>` tags, this is an error. To see which files should have `<legal>` tags but don't, use this command:

```shell
python3 ./update_copyright.py -w
```
