# Using a Continuous Integration (CI) pipeline to test the Redemption tool

<legal></legal>  

To achieve Continuous Integration (CI) and Continuous Deployment (CD) of our Redemption Tool, we have [Atlassian Bamboo](https://www.atlassian.com/software/bamboo) and [Bitbucket](https://bitbucket.org/product) available internally at SEI. We would also like to publish the tool as OSS to [Github](https://github.com/). 

While the tool itself is open-source, we also maintain some private files that should not be published. Likewise, clients may ask us for private extensions to the tool, again which should not be published on Github.  Furthermore, the tool has a Git history of about 1 year, which contains private and public files, so we do not want to mirror the entire current Bitbucket repository.

Our current approach is to split off a public Bitbucket repository, which contains the material that eventually gets pushed to Github.  The push operations are done as part of the CI/CD process.  The old Bitbucket repository becomes the repository just for private internal files (including future proprietary work).

Our priorities are as follows:

 * It should always be possible to fast forward from the GitHub repo to the public Bitbucket repo.
 * It should be relatively easy for developers to commit and push improvements to development branches.
 * If a sensitive file gets added into a development branch in the public Bitbucket repo, it should not be published to Github. It should be reviewed and removed from the branch before the branch gets squash-merged into the main branch. The squash-merge guarantees that any file that gets deleted without appearing in the main branch [never](https://stackoverflow.com/questions/59869948/how-does-git-squash-deal-with-deleted-files) gets pushed to Github. (Note Github provides [tactics](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) for purging sensitive files that get published, but I'd like to avoid this if possible.)
 * It should be easy to accept external patches or PRs submitted via Github .
 * It should use a non-awkward directory structure, that can host both public & private files
 * Continuous Delivery...that is the process of publishing bugfixes should be as painless as possible. Since we already have a process for reviewing bugfixes and features (via PRs), then ideally publishing should be accompanied with merging any development PR into main.
* Any given file should have only one history, rather than existing with parallel histories in both the public and private repositories
* To avoid unnecessary difficulty for external users, we should not force push to the main branch on Github
  
I now think that the goal of a non-awkward dir structure is incompatible with the proper handling of public vs private files. The former strategy of using manifest vs denylist files did a good job of filtering sensitive files, but meant that the public Git repo cannot fast-forward to the public Bitbucket repo, since the Github repo must lack the denylist or any files in it.  We could use Git branches to address the public vs private problem, but branches can easily lead to confusion and files getting leaked onto the wrong branch.  For now, for the private repo we will employ some process to load a container from the public repo with the private files it needs.

## Current Plan

The build process creates a tarball and a Docker container for distributing the Redemption tool.  Bamboo build steps:

### Build process:

1. Initial Git checkout (from public repo)
2. Build 'prereq' Docker container (which includes just prereqs to run Redemption).  `build_prereq.sh`
3. Cleanup (remove all files not known to Git, must be done in container).  `git_cleanup.sh`
4. Run 'update_markings.py' pytests. `update_markings_tests.sh`
5. Validate all pytest results.
5. Cleanup (remove all files not in Git).  `manifest_cleanup.sh`

### Deliver process

1. Build distribution tarball  `create_dist.sh`
2. Build 'redemption.distrib' Docker container.  `build_distrib.sh`
3. If in 'main' branch, push contents to Github repo

Artifacts: Zip file & redemption.distrib container.

### Test process

1. Build 'redemption.test' Docker container  `build_test.sh`
2. Run remaining pytests: code/acr/test and data/test in redemption.test container  `run_tests.sh`
3. Validate all pytest results.
4. Final cleanup (again, remove everything not in Git)  `manifest_cleanup.sh`
