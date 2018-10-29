  $ . $TESTDIR/library.sh

  $ hook_test_setup $TESTDIR/hooks/no_buck_managed_project_files.lua \
  >   no_buck_managed_project_files PerChangeset \
  >   "bypass_commit_string=\"@ignore-buck-managed-project-files\""

Trying to commit a harmless file should pass
  $ hg up -q 0
  $ mkdir -p fbobjc fbandroid fbobjc
  $ echo "sometext" >> fbobjc/newfile
  $ echo "sometext" >> fbandroid/newfile
  $ hg ci -Aqm 1
  $ hgmn push -r . --to master_bookmark
  remote: * DEBG Session with Mononoke started with uuid: * (glob)
  pushing rev ca2644f9351a to destination ssh://user@dummy/repo bookmark master_bookmark
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  added 1 changesets with 0 changes to 0 files
  server ignored bookmark master_bookmark update
  remote: * DEBG Session with Mononoke started with uuid: * (glob)

Trying to commit bad xcode project with BUCK file in the same commit
  $ hg up -q 0
  $ mkdir -p fbobjc/foo/project1.xcodeproj
  $ echo "stuff" > fbobjc/foo/project1.xcodeproj/project.pbxproj
  $ cat >> fbobjc/foo/project1.xcodeproj/BUCK <<EOF
  > xcode_project_config(
  >     (anything)
  >     project_name = 'project1'
  >     (anything)
  > )
  > EOF
  $ hg ci -Aqm 1
  $ hgmn push -r . --to master_bookmark
  remote: * DEBG Session with Mononoke started with uuid: * (glob)
  pushing rev af4117a7dc84 to destination ssh://user@dummy/repo bookmark master_bookmark
  searching for changes
  remote: * ERRO Command failed, remote: true, error: hooks failed: (glob)
  remote: no_buck_managed_project_files for af4117a7dc845b3c165b8c30e68c104fdfefb27c: The Xcode project at fbobjc/foo/project1.xcodeproj/project.pbxproj is automatically generated by Buck. You should NOT commit changes to it. Add fbobjc/foo/project1.xcodeproj/project.pbxproj to .gitignore and .hgignore and 'git rm' it and try again. If you're sure of the implications and want to commit a Buck-generated project, add @ignore-buck-managed-project-files to a your commit message., root_cause: ErrorMessage {
  remote:     msg: "hooks failed:\nno_buck_managed_project_files for af4117a7dc845b3c165b8c30e68c104fdfefb27c: The Xcode project at fbobjc/foo/project1.xcodeproj/project.pbxproj is automatically generated by Buck. You should NOT commit changes to it. Add fbobjc/foo/project1.xcodeproj/project.pbxproj to .gitignore and .hgignore and \'git rm\' it and try again. If you\'re sure of the implications and want to commit a Buck-generated project, add @ignore-buck-managed-project-files to a your commit message."
  remote: }, backtrace: , session_uuid: * (glob)
  abort: stream ended unexpectedly (got 0 bytes, expected 4)
  [255]

Trying to commit bad xcode project with bypass and BUCK file in the same commit
  $ hg ci --amend -qm "@ignore-buck-managed-project-files"
  $ hgmn push -r . --to master_bookmark
  remote: * DEBG Session with Mononoke started with uuid: * (glob)
  pushing rev 0ca8a2a8d0bf to destination ssh://user@dummy/repo bookmark master_bookmark
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  added 1 changesets with 0 changes to 0 files
  server ignored bookmark master_bookmark update

Verify we got the changes
  $ hgmn up master_bookmark
  remote: * DEBG Session with Mononoke started with uuid: * (glob)
  4 files updated, 0 files merged, 0 files removed, 0 files unresolved
  $ hg log -r "::."
  changeset:   0:426bada5c675
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     A
  
  changeset:   1:112478962961
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     B
  
  changeset:   2:26805aba1e60
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     C
  
  changeset:   4:a0cd5f904db6
  parent:      2:26805aba1e60
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     1
  
  changeset:   7:bb1b66da4693
  tag:         tip
  bookmark:    default/master_bookmark
  hoistedname: master_bookmark
  parent:      4:a0cd5f904db6
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     @ignore-buck-managed-project-files
  






Trying to modify the bad xcode project
  $ echo "stuff2" > fbobjc/foo/project1.xcodeproj/project.pbxproj
  $ hg ci -Aqm 1
  $ hgmn push -r . --to master_bookmark
  remote: * DEBG Session with Mononoke started with uuid: * (glob)
  pushing rev 6a3ec7562d66 to destination ssh://user@dummy/repo bookmark master_bookmark
  searching for changes
  remote: * ERRO Command failed, remote: true, error: hooks failed: (glob)
  remote: no_buck_managed_project_files for 6a3ec7562d661a4fd9701b0ad18b7236e2edf6e9: The Xcode project at fbobjc/foo/project1.xcodeproj/project.pbxproj is automatically generated by Buck. You should NOT commit changes to it. Add fbobjc/foo/project1.xcodeproj/project.pbxproj to .gitignore and .hgignore and 'git rm' it and try again. If you're sure of the implications and want to commit a Buck-generated project, add @ignore-buck-managed-project-files to a your commit message., root_cause: ErrorMessage {
  remote:     msg: "hooks failed:\nno_buck_managed_project_files for 6a3ec7562d661a4fd9701b0ad18b7236e2edf6e9: The Xcode project at fbobjc/foo/project1.xcodeproj/project.pbxproj is automatically generated by Buck. You should NOT commit changes to it. Add fbobjc/foo/project1.xcodeproj/project.pbxproj to .gitignore and .hgignore and \'git rm\' it and try again. If you\'re sure of the implications and want to commit a Buck-generated project, add @ignore-buck-managed-project-files to a your commit message."
  remote: }, backtrace: , session_uuid: * (glob)
  abort: stream ended unexpectedly (got 0 bytes, expected 4)
  [255]

Trying to modify the bad xcode project with bypass
  $ hg ci --amend -qm "@ignore-buck-managed-project-files"
  $ hgmn push -r . --to master_bookmark
  remote: * DEBG Session with Mononoke started with uuid: * (glob)
  pushing rev 9713957ca577 to destination ssh://user@dummy/repo bookmark master_bookmark
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  added 0 changesets with 0 changes to 0 files
  server ignored bookmark master_bookmark update

Verify we got the changes
  $ hg log -r "::."
  changeset:   0:426bada5c675
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     A
  
  changeset:   1:112478962961
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     B
  
  changeset:   2:26805aba1e60
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     C
  
  changeset:   4:a0cd5f904db6
  parent:      2:26805aba1e60
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     1
  
  changeset:   7:bb1b66da4693
  parent:      4:a0cd5f904db6
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     @ignore-buck-managed-project-files
  
  changeset:   9:9713957ca577
  tag:         tip
  bookmark:    default/master_bookmark
  hoistedname: master_bookmark
  parent:      7:bb1b66da4693
  user:        test
  date:        Thu Jan 01 00:00:00 1970 +0000
  summary:     @ignore-buck-managed-project-files
  





