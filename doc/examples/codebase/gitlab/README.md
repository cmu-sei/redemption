# Redemption project codebase Gitlab demo

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


## Setup

 1. Create a project in Gitlab; it should contain the contents of this directory, including the `Makefile`, `README.md` (this file), the `.gitlab-ci.yml` file, and the `src` subdirectory (as well as everything else). For the SEI, the site was:
 
https://gitlab.sandbox.labz.s-box.org/sei-svoboda/redemption_codebase

If you create your own Gitlab project, the internal site will be specific to to you.

 2. Create a project token, it must be able to write to the repository and read the container registry.

The token should have a human-readable name, this name will be used to email users when CI has auto-generated merge requests. We called it `Redemption Code Repair Agent`.

 3. Create a CI variable containing this token. (I called it `REDEMPTION_TOKEN`)

The SEI internal site for creating variables was:

https://gitlab.sandbox.labz.s-box.org/sei-svoboda/redemption_codebase/-/settings/ci_cd

If you create your own Gitlab project, the internal site will be specific to you.

 4. Create a CI variable containing the name of the Redemption Docker image.
 
For the SEI internal variable this was:

    REDEMPTION_IMAGE=registry.sandbox.labz.s-box.org/sei-svoboda/redemption:superscript

(For now, this is distinct from the `distrib` image, so gitlab runs latest image)

 5. Create a CI variable containing the URL of the codebase (minus the protocol prefix).
 
For the SEI internal variable this was:

    CODEBASE_URL=gitlab.sandbox.labz.s-box.org/sei-svoboda/redemption_codebase.git

The [`create-pull-request.sh` script](CI/create-pull-request.sh) and [Makefile](Makefile) will need these variables.

 6. To publish the redemption container to Gitlab:

Use Docker to tag the Redemption `distrib` container as `$DEMPTION_IMAGE`. Then execute the following commands (which are based on `$REDEMPTION_IMAGE`.)

```sh
docker login registry.sandbox.labz.s-box.org -u sei-svoboda --password ${REDEMPTION_TOKEN}
docker push registry.sandbox.labz.s-box.org/sei-svoboda/redemption:distrib
```

Note the token should be the same token you pushed any pre-existing docker images (currently, the 'simple' token).

 7. We are using the `dos2unix` codebase, version 7.5.2. It is freely available from [dos2unix.sourceforge.io/](https://sourceforge.net/projects/dos2unix/files/dos2unix/7.5.2/dos2unix-7.5.2.tar.gz/download).  For this demo, you should download `dos2unix-7.5.2`, unpack it, and place its contents in the `src` sub-directory. You could use these commands:
 
```sh
tar xzf dos2unix-7.5.2.tar.gz 
cp -r dos2unix-7.5.2/* src
rm -rf dos2unix-7.5.2
```

## To run the demo:

Make some trivial change in [the source code](src/test_errors.c).

Bring up the [pipeline URL](https://gitlab.sandbox.labz.s-box.org/sei-svoboda/redemption_codebase/-/pipelines); it is good to watch as Gitlab does its work:

Then commit and push your trivial changes.

When Gitlab is done, you should receive email announcing a merge request (MR) that has been assigned to you.

The MR contains the suggested repairs.  There are currently 4 null-pointer repairs it suggests.

There are two ways you can 'reject' a repair:

 1. Gitlab has a Web IDE, showing diffs. Clicking on the light-bulb icon brings up a `Revert this change` option, then you can commit your changes.
 2. Gitlab can accept suggestions (just like Bamboo). Must manually construct a reversion.
 
