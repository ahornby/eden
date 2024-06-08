# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License found in the LICENSE file in the root
# directory of this source tree.

  $ . "${TEST_FIXTURES}/library.sh"

  $ BLOB_TYPE="blob_sqlite" default_setup
  hg repo
  o  C [draft;rev=2;26805aba1e60]
  │
  o  B [draft;rev=1;112478962961]
  │
  o  A [draft;rev=0;426bada5c675]
  $
  blobimporting
  starting Mononoke
  cloning repo in hg client 'repo2'

Push single empty commit
  $ hg up -q "min(all())"
  $ echo 1 > 1 && hg add 1 && hg ci -m 1
  $ hg revert -r .^ 1
  $ hg commit --amend
  $ hg show
  commit:      4d5799789652
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  description:
  1
  
  
  
  $ hgmn push -r . --to master_bookmark
  pushing rev 4d5799789652 to destination mononoke://$LOCALIP:$LOCAL_PORT/repo bookmark master_bookmark
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  updating bookmark master_bookmark

Push empty and non-empty commit in a stack
  $ hg up -q "min(all())"
  $ echo 1 > 1 && hg add 1 && hg ci -m 1
  $ echo 2 > 2 && hg add 2 && hg ci -m 2
  $ hg revert -r .^ 2
  $ hg commit --amend
  $ hgmn push -r . --to master_bookmark
  pushing rev 22c3c2036561 to destination mononoke://$LOCALIP:$LOCAL_PORT/repo bookmark master_bookmark
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  updating bookmark master_bookmark

Push stack of empty commits
  $ hgmn up -q tip
  $ echo 1 > 11 && hg add 11 && hg ci -m emptystack1
  $ hg revert -r .^ 11
  $ hg commit --amend
  $ echo 1 > 111 && hg add 111 && hg ci -m emptystack2
  $ hg revert -r .^ 111
  $ hg commit --amend
  $ hgmn push -r . --to master_bookmark
  pushing rev aeb4783bffb3 to destination mononoke://$LOCALIP:$LOCAL_PORT/repo bookmark master_bookmark
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  updating bookmark master_bookmark
