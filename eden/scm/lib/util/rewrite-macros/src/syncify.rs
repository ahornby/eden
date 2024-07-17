/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This software may be used and distributed according to the terms of the
 * GNU General Public License version 2.
 */

extern crate proc_macro;

use crate::prelude::*;

pub(crate) fn syncify(attr: TokenStream, mut tokens: TokenStream) -> TokenStream {
    let debug = !attr.find_all(parse("debug")).is_empty();
    tokens
        .replace_all(parse(".await"), parse(""))
        .replace_all(parse(".boxed()"), parse(""))
        .replace_all(parse("async move"), parse(""))
        .replace_all(parse("async"), parse(""))
        .replace_all(parse("#[tokio::test]"), parse("#[test]"))
        .replace_all(parse("__::block_on(___g1)"), parse("___g1"));

    // Apply customized replaces.
    let matches = attr.find_all(parse("[___g1] => [___g2]"));
    if debug {
        eprintln!("{} customized replaces", matches.len());
    }
    for m in matches {
        let pat = m.captures.get("___g1").unwrap();
        let replace = m.captures.get("___g2").unwrap();
        tokens.replace_all_raw(pat, replace);
    }

    // `cargo expand` can also be used to produce output.
    if debug {
        eprintln!("output: [[[\n{}\n]]]", unparse(&tokens));
    }

    tokens
}
