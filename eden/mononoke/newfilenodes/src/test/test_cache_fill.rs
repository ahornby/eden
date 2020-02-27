/*
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This software may be used and distributed according to the terms of the
 * GNU General Public License version 2.
 */

use anyhow::Error;
use context::CoreContext;
use fbinit::FacebookInit;
use filenodes::{FilenodeInfo, PreparedFilenode};
use mercurial_types_mocks::nodehash::{ONES_CSID, ONES_FNID};
use mononoke_types::RepoPath;
use mononoke_types_mocks::repo::REPO_ZERO;
use tokio_preview as tokio;

use super::util::{build_reader_writer, build_shard};
use crate::local_cache::{test::HashMapCache, LocalCache};
use crate::remote_cache::test::{make_test_cache, wait_for_filenode, wait_for_history};

fn filenode() -> FilenodeInfo {
    FilenodeInfo {
        filenode: ONES_FNID,
        p1: None,
        p2: None,
        copyfrom: None,
        linknode: ONES_CSID,
    }
}

#[fbinit::test]
async fn test_filenode_fill(fb: FacebookInit) -> Result<(), Error> {
    let ctx = CoreContext::test_mock(fb);
    let (mut reader, writer) = build_reader_writer(vec![build_shard()?]);

    reader.local_cache = LocalCache::Test(HashMapCache::new());
    reader.remote_cache = make_test_cache();

    let path = RepoPath::file("file")?;
    let info = filenode();

    writer
        .insert_filenodes(
            &ctx,
            REPO_ZERO,
            vec![PreparedFilenode {
                path: path.clone(),
                info: info.clone(),
            }],
            false,
        )
        .await?;

    // A local miss should fill the remote cache:
    reader
        .get_filenode(&ctx, REPO_ZERO, &path, info.filenode)
        .await?;
    wait_for_filenode(&reader.remote_cache, &path, info.filenode).await?;

    // A local hit should not fill the remote cache:
    reader.remote_cache = make_test_cache();
    reader
        .get_filenode(&ctx, REPO_ZERO, &path, info.filenode)
        .await?;
    let r = wait_for_filenode(&reader.remote_cache, &path, info.filenode).await;
    assert!(r.is_err());

    Ok(())
}

#[fbinit::test]
async fn test_history_fill(fb: FacebookInit) -> Result<(), Error> {
    let ctx = CoreContext::test_mock(fb);
    let (mut reader, writer) = build_reader_writer(vec![build_shard()?]);

    reader.local_cache = LocalCache::Test(HashMapCache::new());
    reader.remote_cache = make_test_cache();

    let path = RepoPath::file("file")?;
    let info = filenode();

    writer
        .insert_filenodes(
            &ctx,
            REPO_ZERO,
            vec![PreparedFilenode {
                path: path.clone(),
                info: info.clone(),
            }],
            false,
        )
        .await?;

    // A local miss should fill the remote cache:
    reader
        .get_all_filenodes_for_path(&ctx, REPO_ZERO, &path)
        .await?;
    wait_for_history(&reader.remote_cache, &path).await?;

    // A local hit should not fill the remote cache:
    reader.remote_cache = make_test_cache();
    reader
        .get_all_filenodes_for_path(&ctx, REPO_ZERO, &path)
        .await?;
    let r = wait_for_history(&reader.remote_cache, &path).await;
    assert!(r.is_err());

    Ok(())
}
