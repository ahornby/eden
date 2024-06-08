# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License found in the LICENSE file in the root
# directory of this source tree.

  $ . "${TEST_FIXTURES}/library.sh"

setup configuration
  $ export EMIT_OBSMARKERS=1
  $ setup_common_config
  $ cd $TESTTMP

setup common configuration
  $ cat >> $HGRCPATH <<EOF
  > [ui]
  > ssh="$DUMMYSSH"
  > EOF

setup repo
  $ hg init repo-hg
  $ cd repo-hg
  $ setup_hg_server
  $ drawdag <<EOF
  > C
  > |
  > B
  > |
  > A
  > EOF

create master bookmark
  $ hg bookmark master_bookmark -r tip

blobimport them into Mononoke storage and start Mononoke
  $ cd ..
  $ blobimport repo-hg/.hg repo

start mononoke
  $ start_and_wait_for_mononoke_server
Clone the repo
  $ hgclone_treemanifest ssh://user@dummy/repo-hg repo2 --noupdate --config extensions.remotenames= -q
  $ cd repo2
  $ setup_hg_client
  $ cat >> .hg/hgrc <<EOF
  > [extensions]
  > pushrebase =
  > remotenames =
  > EOF

Push commits that will be obsoleted
  $ hg up -q "min(all())"
  $ echo 1 > 1 && hg add 1 && hg ci -m 1
  $ echo 2 > 2 && hg add 2 && hg ci -m 2
  $ log -r "all()"
  @  2 [draft;rev=4;0c67ec8c24b9]
  │
  o  1 [draft;rev=3;a0c9c5791058]
  │
  │ o  C [public;rev=2;26805aba1e60] default/master_bookmark
  │ │
  │ o  B [public;rev=1;112478962961]
  ├─╯
  o  A [public;rev=0;426bada5c675]
  $
  $ hgmn push -r . --to master_bookmark
  pushing rev 0c67ec8c24b9 to destination mononoke://$LOCALIP:$LOCAL_PORT/repo bookmark master_bookmark
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  updating bookmark master_bookmark
  2 files updated, 0 files merged, 0 files removed, 0 files unresolved
  $ log -r "all()"
  @  2 [public;rev=6;dc31470c8386] default/master_bookmark
  │
  o  1 [public;rev=5;c2e526aacb51]
  │
  o  C [public;rev=2;26805aba1e60]
  │
  o  B [public;rev=1;112478962961]
  │
  o  A [public;rev=0;426bada5c675]
  $

Push commits that will not be obsoleted
  $ hg up -q dc31470c8386
  $ echo 3 > 3 && hg add 3 && hg ci -m 3
  $ log -r "all()"
  @  3 [draft;rev=7;6398085ceb9d]
  │
  o  2 [public;rev=6;dc31470c8386] default/master_bookmark
  │
  o  1 [public;rev=5;c2e526aacb51]
  │
  o  C [public;rev=2;26805aba1e60]
  │
  o  B [public;rev=1;112478962961]
  │
  o  A [public;rev=0;426bada5c675]
  $
  $ hgmn push -r . --to master_bookmark
  pushing rev 6398085ceb9d to destination mononoke://$LOCALIP:$LOCAL_PORT/repo bookmark master_bookmark
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  updating bookmark master_bookmark
  $ log -r "all()"
  @  3 [public;rev=7;6398085ceb9d] default/master_bookmark
  │
  o  2 [public;rev=6;dc31470c8386]
  │
  o  1 [public;rev=5;c2e526aacb51]
  │
  o  C [public;rev=2;26805aba1e60]
  │
  o  B [public;rev=1;112478962961]
  │
  o  A [public;rev=0;426bada5c675]
  $
