# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2.

from __future__ import absolute_import

import socket

from sapling import error

from . import httpsservice, localservice, saplingremoteapiservice


def get(ui, repo=None):
    servicetype = ui.config("commitcloud", "servicetype")
    if servicetype == "local":
        return localservice.LocalService(ui)
    elif servicetype == "remote":
        return httpsservice.HttpsCommitCloudService(ui)
    elif servicetype == "saplingremoteapi" or servicetype == "edenapi":
        fallbackcfg = ui.config("commitcloud", "fallback")
        fallback = (
            localservice.LocalService(ui)
            if fallbackcfg == "local"
            else httpsservice.HttpsCommitCloudService(ui)
        )
        return saplingremoteapiservice.SaplingRemoteAPIService(
            ui,
            repo,
            fallback,
        )
    else:
        msg = "Unrecognized commitcloud.servicetype: %s" % servicetype
        raise error.Abort(msg)


def makeclientinfo(repo, syncstate):
    hostname = repo.ui.config("commitcloud", "hostname", socket.gethostname())
    return {
        "hostname": hostname,
        "reporoot": repo.root,
        "version": syncstate.version,
    }
