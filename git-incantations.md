
# Some git incantations

See:
* http://nvie.com/posts/a-successful-git-branching-model/


## Create the develop branch

See:
* http://www.linux-pages.com/2011/05/how-to-create-a-brand-new-git-tracking-branch-from-scratch/

    git push origin master:develop
    git branch --track develop origin/develop

Also, to delete remote branch:

    git push origin --delete <branchName>


## Merge develop changes to master branch

When all tests pass, we can creare a new release on the master branch.

    $ git checkout master
    Switched to branch 'master'
    $ git merge --no-ff develop
    (Summary of changes)
    (Resolve conflicts as necessary, and rerun tests)

The --no-ff flag causes the merge to always create a new commit object, even if the merge could be performed with a fast-forward.


## Creating a feature branch

When starting work on a new feature, branch off from the develop branch.

    $ git checkout -b myfeature develop
    Switched to a new branch "myfeature"

Also, to create tracking copy in github:

    $ git push origin HEAD
    $ git branch --set-upstream myfeature origin/myfeature

Pushes to same-name branch at origin repo, and sets tracking status.


## Incorporating a finished feature on develop

Finished features may be merged into the develop branch definitely add them to the upcoming release:

    $ git checkout develop
    Switched to branch 'develop'
    $ git merge --no-ff myfeature
    Updating ea1b82a..05e9557
    (Summary of changes)
    $ git branch -d myfeature
    Deleted branch myfeature (was 05e9557).
    $ git push origin develop

The --no-ff flag causes the merge to always create a new commit object, even if the merge could be performed with a fast-forward.


## Release branches

May branch off from: develop Must merge back into: develop and master Branch naming convention: release-*

Creating a release branch

    $ git checkout -b release-1.2 develop
    Switched to a new branch "release-1.2"
    $ ./bump-version.sh 1.2
    Files modified successfully, version bumped to 1.2.
    $ git commit -a -m "Bumped version number to 1.2"
    [release-1.2 74d9424] Bumped version number to 1.2
    1 files changed, 1 insertions(+), 1 deletions(-)

Finishing a release branch

    $ git checkout master
    Switched to branch 'master'
    $ git merge --no-ff release-1.2
    Merge made by recursive.
    (Summary of changes)
    $ git tag -a 1.2

    $ git checkout develop
    Switched to branch 'develop'
    $ git merge --no-ff release-1.2
    Merge made by recursive.
    (Summary of changes)

    $ git branch -d release-1.2
    Deleted branch release-1.2 (was ff452fe).


## Reconnecting upstream branch

"So having done "git remote rm origin", how do I configure the git pull branches again?"

Looks like this does it:

    git remote add origin darcs.haskell.org:/srv/darcs/ghc.git
    git fetch origin
    git branch --set-upstream master origin/master

-- http://www.haskell.org/pipermail/ghc-devs/2013-February/000261.html


## Force current branch to be a copy of another

    git reset --hard <branch>
    git push --force

Note: this may lose history on the current branch.


## Create local copy of remote branch

    git checkout -b <branch> origin/<branch>

or (1.6.2)

    git checkout --track origin/<branch>

This automatically creates a tracking branch.

(See also "Reconnecting upstream branch" above.)


## Delete remote branch

    git push origin :<branch>

cf. general form of push:

    git push [remotename] [localbranch]:[remotebranch]

See: http://git-scm.com/book/en/Git-Branching-Remote-Branches


## Selective transfer files from one branch to another

See also:
* http://stackoverflow.com/questions/449541/how-do-you-merge-selective-files-with-git-merge
* http://jasonrudolph.com/blog/2009/02/25/git-tip-how-to-merge-specific-files-from-another-branch/

    git checkout newbranch
    git checkout oldbranch path
    git commit


## Selective transfer commits from one branch to another

See also:
* https://help.github.com/articles/interactive-rebase

    git checkout newbranch
    git merge oldbranch
    git rebase --interactive

Lauches an editor with a list of commits which can be dropeed, merged or otherwise tweaked.  Follow instructions untilk a clean result is obtained.

It is possible that a merge failure will prevent this process from being completely automatic. You will have to resolve any such merge failure and run:

    git rebase --continue

Another option is to bypass the commit that caused the merge failure with:

    git rebase --skip.

If you get lost in a tangle of conflicts, the whole operation can be abandoned by:

    git rebase --abort

