# Redemption project simple Gitlab demo

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

 1. Create a project token, it must be able to write to the repository and read the container registry.
 2. Create a CI variable containing this token. (I called it `REDEMPTION_TOKEN`)

The SEI internal site for creating variables was:

https://gitlab.sandbox.labz.s-box.org/sei-svoboda/redemption/-/settings/ci_cd

 3. Create a CI variable containing the name of the Redemption Docker image.
 
For the SEI internal variable this was:

    REDEMPTION_IMAGE=registry.sandbox.labz.s-box.org/sei-svoboda/redemption:distrib

 4. Create a CI variable containing the URL of the codebase (minus the protocol prefix).
 
For the SEI internal variable this was:

    CODEBASE_URL=gitlab.sandbox.labz.s-box.org/sei-svoboda/redemption.git

The [`create-pull-request.sh` script](CI/create-pull-request.sh) and [Makefile](Makefile) will need these variables.


 5. To publish the redemption container to Gitlab:

Use Docker to tag the Redemption `distrib` container as `$DEMPTION_IOMAGE`. Then execute the following commands (which are based on `$DEMPTION_IOMAGE`

```sh
docker login registry.sandbox.labz.s-box.org -u sei-svoboda --password ${REDEMPTION_TOKEN}
docker push registry.sandbox.labz.s-box.org/sei-svoboda/redemption:distrib
```

## To run the demo:

Make some trivial change in [the source code](src/test_errors.c).

Bring up the [pipeline URL](https://gitlab.sandbox.labz.s-box.org/sei-svoboda/redemption/-/pipelines); it is  good to watch as Gitlab does its work:

Then commit and push your trivial changes.

When Gitlab is done, you should receive email announcing a merge request (MR) that has been assigned to you.

The MR contains the suggested repairs.  There are currently 4 null-pointer repairs it suggests.

There are two ways you can 'reject' a repair:

 1. Gitlab has a Web IDE, showing diffs. Clicking on the light-bulb icon brings up a `Revert this change` option, then you can commit your changes.
 2. Gitlab can accept suggestions (just like Bamboo). Must manually construct a reversion.
 
