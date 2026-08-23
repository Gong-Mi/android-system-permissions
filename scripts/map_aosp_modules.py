#!/usr/bin/env python3
"""Locate unresolved permission names in AOSP module repositories.

This records current-source ownership only. It deliberately does not infer an
API introduction version from a current branch; module history must be present
before a version can be assigned.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

MODULES = {
    "healthfitness": "packages/modules/HealthFitness",
    "adservices": "packages/modules/AdServices",
    "permissioncontroller": "packages/modules/Permission",
    "car": "packages/services/Car",
    "frameworks-base": "platform/frameworks/base",
}
REPO_DIRS = {
    "permissioncontroller": "aosp-permission",
    "frameworks-base": "aosp-frameworks-base",
}


def build_index(repo: Path) -> dict[str, set[str]]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "grep", "-n", "-E", r"android\.permission\.[A-Za-z0-9_.]+", "HEAD", "--"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {}
    index: dict[str, set[str]] = {}
    import re
    for line in out.splitlines():
        match = re.match(r"[^:]+:([^:]+):", line)
        if not match:
            continue
        path = match.group(1)
        for name in re.findall(r"android\.permission\.[A-Za-z0-9_.]+", line):
            index.setdefault(name, set()).add(path)
    return index


def classify(paths: list[str]) -> str:
    if any("framework/api/" in p or "/api/" in p for p in paths):
        return "module-api-surface"
    if any("Manifest" in p or "manifest" in p or "permission" in p.lower() for p in paths):
        return "module-permission-source"
    if any("service" in p.lower() or "manager" in p.lower() for p in paths):
        return "module-enforcement-or-manager"
    return "module-reference-only"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--directory", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--root", required=True, type=Path)
    args = ap.parse_args()

    directory = json.loads(args.directory.read_text(encoding="utf-8"))
    repos = {}
    indexes = {}
    for key, relative in MODULES.items():
        repo = args.root / REPO_DIRS.get(key, "aosp-" + key)
        if repo.is_dir() and (repo / ".git").exists():
            repos[key] = (repo, relative)
            indexes[key] = build_index(repo)

    output = dict(directory)
    output["schema"] = "android-system-permissions/permission-directory-with-aosp-modules-v1"
    records = {}
    for name, entry in directory["permissions"].items():
        aosp = dict(entry.get("aosp", {}))
        if aosp.get("status") != "not-found-in-frameworks-base-core-res":
            records[name] = dict(entry, aosp=aosp)
            continue
        hits = []
        for key, (repo, relative) in repos.items():
            paths = sorted(indexes[key].get(name, set()))
            if paths:
                hits.append(
                    {
                        "module": key,
                        "repository": relative,
                        "paths": paths[:30],
                        "path_count": len(paths),
                        "source_class": classify(paths),
                    }
                )
        aosp["module_sources"] = hits
        aosp["module_api_status"] = "current-source-located" if hits else "not-located-in-checked-modules"
        aosp["module_first_seen_api"] = None
        records[name] = dict(entry, aosp=aosp)
    output["permissions"] = dict(sorted(records.items()))
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    unresolved = [v for v in records.values() if v["aosp"].get("status") == "not-found-in-frameworks-base-core-res"]
    located = sum(bool(v["aosp"].get("module_sources")) for v in unresolved)
    print(json.dumps({"unresolved_core_res": len(unresolved), "located_in_checked_modules": located}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
