#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import re
import shutil
import typing

from .builder import BuilderBase

if typing.TYPE_CHECKING:
    from .buildopts import BuildOptions


class CargoBuilder(BuilderBase):
    def __init__(
        self,
        build_opts: "BuildOptions",
        ctx,
        manifest,
        src_dir,
        build_dir,
        inst_dir,
        build_doc,
        workspace_dir,
        manifests_to_build,
        loader,
        cargo_config_file,
    ) -> None:
        super(CargoBuilder, self).__init__(
            build_opts, ctx, manifest, src_dir, build_dir, inst_dir
        )
        self.build_doc = build_doc
        self.ws_dir = workspace_dir
        self.manifests_to_build = manifests_to_build and manifests_to_build.split(",")
        self.loader = loader
        self.cargo_config_file_subdir = cargo_config_file

    def run_cargo(self, install_dirs, operation, args=None) -> None:
        args = args or []
        env = self._compute_env(install_dirs)
        # Enable using nightly features with stable compiler
        env["RUSTC_BOOTSTRAP"] = "1"
        env["LIBZ_SYS_STATIC"] = "1"
        cmd = [
            "cargo",
            operation,
            "--workspace",
            "-j%s" % self.num_jobs,
        ] + args
        self._run_cmd(cmd, cwd=self.workspace_dir(), env=env)

    def build_source_dir(self):
        return os.path.join(self.build_dir, "source")

    def workspace_dir(self):
        return os.path.join(self.build_source_dir(), self.ws_dir or "")

    def manifest_dir(self, manifest):
        return os.path.join(self.build_source_dir(), manifest)

    def recreate_dir(self, src, dst) -> None:
        if os.path.islink(dst):
            os.remove(dst)
        elif os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)

    def recreate_linked_dir(self, src, dst) -> None:
        if os.path.islink(dst):
            os.remove(dst)
        elif os.path.isdir(dst):
            shutil.rmtree(dst)
        os.symlink(src, dst)

    def cargo_config_file(self):
        build_source_dir = self.build_dir
        if self.cargo_config_file_subdir:
            return os.path.join(build_source_dir, self.cargo_config_file_subdir)
        else:
            return os.path.join(build_source_dir, ".cargo", "config")

    def _create_cargo_config(self):
        cargo_config_file = self.cargo_config_file()
        cargo_config_dir = os.path.dirname(cargo_config_file)
        if not os.path.isdir(cargo_config_dir):
            os.mkdir(cargo_config_dir)

        if os.path.isfile(cargo_config_file):
            with open(cargo_config_file, "r") as f:
                print(f"Reading {cargo_config_file}")
                cargo_content = f.read()
        else:
            cargo_content = ""

        new_content = cargo_content
        if not "# Generated by getdeps.py" in cargo_content:
            new_content += """\
# Generated by getdeps.py
[build]
target-dir = '''{}'''

[profile.dev]
debug = false
incremental = false

""".format(
                self.build_dir.replace("\\", "\\\\")
            )

        # Point to vendored sources from getdeps manifests
        dep_to_git = self._resolve_dep_to_git()
        for _dep, git_conf in dep_to_git.items():
            if "cargo_vendored_sources" in git_conf:
                vendored_dir = git_conf["cargo_vendored_sources"].replace(
                    "\\", "\\\\"
                )
                override = f'[source."{git_conf["repo_url"]}"]\ndirectory = "{vendored_dir}"\n'
                if not override in cargo_content:
                    new_content += override

        if new_content != cargo_content:
            with open(cargo_config_file, "w") as f:
                print(f"Writing cargo config for {self.manifest.name} to {cargo_config_file}")
                f.write(new_content)

        if self.build_opts.fbsource_dir:
            # Point to vendored crates.io if possible
            try:
                from .facebook.rust import vendored_crates

                vendored_crates(self.build_opts.fbsource_dir, cargo_config_file)
            except ImportError:
                # This FB internal module isn't shippped to github,
                # so just rely on cargo downloading crates on it's own
                pass

        return dep_to_git

    def _prepare(self, install_dirs, reconfigure) -> None:
        build_source_dir = self.build_source_dir()

        if self.build_opts.is_windows():
            self.recreate_dir(self.src_dir, build_source_dir)
        else:
            self.recreate_linked_dir(self.src_dir, build_source_dir)

        dep_to_git = self._create_cargo_config()

        if self.ws_dir is not None:
            self._patchup_workspace(dep_to_git)

    def _build(self, install_dirs, reconfigure) -> None:
        # _prepare has been run already. Actually do the build
        build_source_dir = self.build_source_dir()
        args = ["--out-dir", os.path.join(self.inst_dir, "bin"), "-Zunstable-options"]
        if self.manifests_to_build is None:
            self.run_cargo(install_dirs, "build", args)
        else:
            for manifest in self.manifests_to_build:
                margs = args + ["--manifest-path", self.manifest_dir(manifest)]
                self.run_cargo(install_dirs, "build", margs)

        installed_source = os.path.join(self.inst_dir, "source")
        if self.build_opts.is_windows():
            self.recreate_dir(build_source_dir, installed_source)
        else:
            self.recreate_linked_dir(build_source_dir, installed_source)
 
    def run_tests(
        self, install_dirs, schedule_type, owner, test_filter, retry, no_testpilot
    ) -> None:
        args = []
        if test_filter:
            args = args + ["--", test_filter]

        if self.manifests_to_build is None:
            self.run_cargo(install_dirs, "test", args)
            if self.build_doc:
                doc_args = ["--no-deps"] + args
                self.run_cargo(install_dirs, "doc", doc_args)
        else:
            for manifest in self.manifests_to_build:
                margs = ["--manifest-path", self.manifest_dir(manifest)]
                self.run_cargo(install_dirs, "test", args + margs)
                if self.build_doc:
                    doc_args = ["--no-deps"] + args
                    self.run_cargo(install_dirs, "doc", doc_args)

    def _patchup_workspace(self, dep_to_git) -> None:
        """
        This method makes some assumptions about the state of the project and
        its cargo dependendies:
        1. Crates from cargo dependencies can be extracted from Cargo.toml files
           using _extract_crates function. It is using a heuristic so check its
           code to understand how it is done.
        2. The extracted cargo dependencies crates can be found in the
           dependency's install dir using _resolve_crate_to_path function
           which again is using a heuristic.

        Notice that many things might go wrong here. E.g. if someone depends
        on another getdeps crate by writing in their Cargo.toml file:

            my-rename-of-crate = { package = "crate", git = "..." }

        they can count themselves lucky because the code will raise an
        Exception. There migh be more cases where the code will silently pass
        producing bad results.
        """
        workspace_dir = self.workspace_dir()
        git_url_to_crates_and_paths = self._resolve_config(dep_to_git)
        if git_url_to_crates_and_paths:
            patch_cargo = os.path.join(workspace_dir, "Cargo.toml")
            if os.path.isfile(patch_cargo):           
                with open(patch_cargo, "r") as f:
                    manifest_content = f.read()
            else:
                manifest_content = ""
            
            new_content = manifest_content
            if "[package]" not in manifest_content:
                # A fake manifest has to be crated to change the virtual
                # manifest into a non-virtual. The virtual manifests are limited
                # in many ways and the inability to define patches on them is
                # one. Check https://github.com/rust-lang/cargo/issues/4934 to
                # see if it is resolved.
                null_file = "/dev/null"
                if self.build_opts.is_windows():
                    null_file = "nul"
                new_content += f"""
[package]
name = "fake_manifest_of_{self.manifest.name}"
version = "0.0.0"

[lib]
path = "{null_file}"

"""
            config = []
            for git_url, crates_to_patch_path in git_url_to_crates_and_paths.items():
                crates_patches = [
                    '{} = {{ path = "{}" }}'.format(
                        crate,
                        crates_to_patch_path[crate].replace("\\", "\\\\"),
                    )
                    for crate in sorted(crates_to_patch_path.keys())
                ]
                patch_key = f'[patch."{git_url}"]'
                if patch_key not in manifest_content:
                    config.append(f'\n{patch_key}\n' + "\n".join(crates_patches))
            new_content += "\n".join(config)
            if new_content != manifest_content:
                with open(patch_cargo, "w") as f:
                    print(f"writing patch to {patch_cargo}")
                    f.write(new_content)

    def _resolve_config(self, dep_to_git) -> str:
        """
        Returns a configuration to be put inside root Cargo.toml file which
        patches the dependencies git code with local getdeps versions.
        See https://doc.rust-lang.org/cargo/reference/manifest.html#the-patch-section
        """
        dep_to_crates = self._resolve_dep_to_crates(self.build_source_dir(), dep_to_git)

        git_url_to_crates_and_paths = {}
        for dep_name in sorted(dep_to_git.keys()):
            git_conf = dep_to_git[dep_name]
            req_crates = sorted(dep_to_crates.get(dep_name, []))
            if not req_crates:
                continue  # nothing to patch, move along

            git_url = git_conf.get("repo_url", None)
            crate_source_map = git_conf["crate_source_map"]
            if git_url and crate_source_map:
                crates_to_patch_path = git_url_to_crates_and_paths.get(git_url, {})
                for c in req_crates:
                    if c in crate_source_map and c not in crates_to_patch_path:
                        crates_to_patch_path[c] = crate_source_map[c]
                        print(
                            f"{self.manifest.name}: Patching crate {c} via virtual manifest in {self.workspace_dir()}"
                        )
                if crates_to_patch_path:
                    git_url_to_crates_and_paths[git_url] = crates_to_patch_path

        return git_url_to_crates_and_paths

    def _resolve_dep_to_git(self):
        """
        For each direct dependency of the currently build manifest check if it
        is also cargo-builded and if yes then extract it's git configs and
        install dir
        """
        dependencies = self.manifest.get_dependencies(self.ctx)
        if not dependencies:
            return []

        dep_to_git = {}
        for dep in dependencies:
            dep_manifest = self.loader.load_manifest(dep)
            dep_builder = dep_manifest.get("build", "builder", ctx=self.ctx)

            dep_cargo_conf = dep_manifest.get_section_as_dict("cargo", self.ctx)
            dep_crate_map = dep_manifest.get_section_as_dict("crate.pathmap", self.ctx)

            if (
                not (dep_crate_map or dep_cargo_conf)
                and dep_builder not in ["cargo"]
                or dep == "rust"
            ):
                # This dependency has no cargo rust content so ignore it.
                # The "rust" dependency is an exception since it contains the
                # toolchain.
                continue

            git_conf = dep_manifest.get_section_as_dict("git", self.ctx)
            if dep != "rust" and "repo_url" not in git_conf:
                raise Exception(
                    f"{dep}: A cargo dependency requires git.repo_url to be defined."
                )

            if dep_builder == "cargo":
                dep_source_dir = self.loader.get_project_install_dir(dep_manifest)
                dep_source_dir = os.path.join(dep_source_dir, "source")
            else:
                fetcher = self.loader.create_fetcher(dep_manifest)
                dep_source_dir = fetcher.get_src_dir()

            crate_source_map = {}
            if dep_crate_map:
                for (crate, subpath) in dep_crate_map.items():
                    if crate not in crate_source_map:
                        if self.build_opts.is_windows():
                            subpath = subpath.replace("/", "\\")
                        crate_path = os.path.join(dep_source_dir, subpath)
                        print(
                            f"{self.manifest.name}: Mapped crate {crate} to dep {dep} dir {crate_path}"
                        )
                        crate_source_map[crate] = crate_path
            elif dep_cargo_conf:
                # We don't know what crates are defined buy the dep, look for them
                search_pattern = re.compile('\\[package\\]\nname = "(.*)"')
                for crate_root, _, files in os.walk(dep_source_dir):
                    if "Cargo.toml" in files:
                        with open(os.path.join(crate_root, "Cargo.toml"), "r") as f:
                            content = f.read()
                            match = search_pattern.search(content)
                            if match:
                                crate = match.group(1)
                                if crate:
                                    print(
                                        f"{self.manifest.name}: Discovered crate {crate} in dep {dep} dir {crate_root}"
                                    )
                                    crate_source_map[crate] = crate_root

            git_conf["crate_source_map"] = crate_source_map

            if not dep_crate_map and dep_cargo_conf:
                dep_cargo_dir = self.loader.get_project_build_dir(dep_manifest)
                dep_cargo_dir = os.path.join(dep_cargo_dir, "source")
                dep_ws_dir = dep_cargo_conf.get("workspace_dir", None)
                if dep_ws_dir:
                    dep_cargo_dir = os.path.join(dep_cargo_dir, dep_ws_dir)
                git_conf["cargo_vendored_sources"] = dep_cargo_dir

            dep_to_git[dep] = git_conf
        return dep_to_git

    def _resolve_dep_to_crates(self, build_source_dir, dep_to_git):
        """
        This function traverse the build_source_dir in search of Cargo.toml
        files, extracts the crate names from them using _extract_crates
        function and returns a merged result containing crate names per
        dependency name from all Cargo.toml files in the project.
        """
        if not dep_to_git:
            return {}  # no deps, so don't waste time traversing files

        dep_to_crates = {}

        # First populate explicit crate paths from depedencies
        for name, git_conf in dep_to_git.items():
            crates = git_conf["crate_source_map"].keys()
            if crates:
                dep_to_crates.setdefault(name, set()).update(crates)

        # Now find from Cargo.tomls
        for root, _, files in os.walk(build_source_dir):
            for f in files:
                if f == "Cargo.toml":
                    more_dep_to_crates = CargoBuilder._extract_crates_used(
                        os.path.join(root, f), dep_to_git
                    )
                    for dep_name, crates in more_dep_to_crates.items():
                        existing_crates = dep_to_crates.get(dep_name, set())
                        for c in crates:
                            if c not in existing_crates:
                                print(
                                    f"Patch {self.manifest.name} uses {dep_name} crate {crates}"
                                )
                                existing_crates.add(c)
                        dep_to_crates.setdefault(name, set()).update(existing_crates)
        return dep_to_crates

    @staticmethod
    def _extract_crates_used(cargo_toml_file, dep_to_git):
        """
        This functions reads content of provided cargo toml file and extracts
        crate names per each dependency. The extraction is done by a heuristic
        so it might be incorrect.
        """
        deps_to_crates = {}
        with open(cargo_toml_file, "r") as f:
            for line in f.readlines():
                if line.startswith("#") or "git = " not in line:
                    continue  # filter out commented lines and ones without git deps
                for dep_name, conf in dep_to_git.items():
                    # Only redirect deps that point to git URLS
                    if 'git = "{}"'.format(conf["repo_url"]) in line:
                        pkg_template = ' package = "'
                        if pkg_template in line:
                            crate_name, _, _ = line.partition(pkg_template)[
                                2
                            ].partition('"')
                        else:
                            crate_name, _, _ = line.partition("=")
                        deps_to_crates.setdefault(dep_name, set()).add(
                            crate_name.strip()
                        )
        return deps_to_crates

    def _resolve_crate_to_path(self, crate, crate_source_map):
        """
        Tries to find <crate> in source_dir by searching a [package]
        keyword followed by name = "<crate>".
        """
        search_pattern = '[package]\nname = "{}"'.format(crate)

        for (_crate, crate_source_dir) in crate_source_map.items():
            for crate_root, _, files in os.walk(crate_source_dir):
                if "Cargo.toml" in files:
                    with open(os.path.join(crate_root, "Cargo.toml"), "r") as f:
                        content = f.read()
                        if search_pattern in content:
                            return crate_root

        raise Exception(
            f"{self.manifest.name}: Failed to find dep crate {crate} in paths {crate_source_map}"
        )
