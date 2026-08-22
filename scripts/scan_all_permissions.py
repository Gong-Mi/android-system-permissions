#!/usr/bin/env python3
"""Build a complete permission catalog from one Android device snapshot.

The local collector intentionally uses three root calls:
1. `dumpsys package` once for the device permission-definition table;
2. one batched `pm path` collection for base and installed split APKs;
3. eight parallel `aapt2 dump permissions` workers over those APKs.

It does not start one root process per package.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def run_root(command: str) -> str:
    return subprocess.run(["su", "-c", command], check=True, capture_output=True, text=True).stdout


def collect_local(out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    definitions = out_dir / ".dumpsys-package.txt"
    requested = out_dir / ".aapt-permissions.tsv"
    definition_text = run_root("dumpsys package")
    definitions.write_text(definition_text, encoding="utf-8")

    paths = out_dir / ".package-paths.tsv"
    path_collector = Path(__file__).with_name("device_apk_paths.sh")
    path_rows = []
    for line in run_root(f"sh {path_collector}").splitlines():
        fields = line.split("\t", 2)
        if len(fields) == 3 and fields[0] == "PKG":
            path_rows.append(f"{fields[1]}\t{fields[2]}")
    paths.write_text("\n".join(path_rows) + "\n", encoding="utf-8")

    collector = Path(__file__).with_name("device_aapt_scan.sh")
    requested.write_text(run_root(f"sh {collector} {paths}"), encoding="utf-8")
    return definitions, requested


def parse_definitions(text: str) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    # The Permission section is the authoritative on-device definition list.
    for match in re.finditer(
        r"^  Permission \[([^]]+)\].*?^    sourcePackage=([^\n]+).*?^    uid=.*? prot=([^\n]+)",
        text,
        re.M | re.S,
    ):
        name, source, protection = match.groups()
        records[name] = {"defining_package": source.strip(), "protection_level": protection.strip()}
    return records


def parse_requested(text: str) -> dict[str, set[str]]:
    apps: dict[str, set[str]] = defaultdict(set)
    for line in text.splitlines():
        fields = line.split("\t", 2)
        if len(fields) == 3 and fields[0] == "PKG":
            package, raw_permissions = fields[1], fields[2]
            for permission in raw_permissions.split(","):
                permission = permission.strip()
                if permission:
                    apps[package].add(permission)
        elif len(fields) == 2 and fields[0] == "PKG":
            apps.setdefault(fields[1], set())
        elif line.startswith("PERM\t"):
            # Backward-compatible parser for the first pm-dump collector.
            package = next(reversed(apps), None)
            if package:
                apps[package].add(line.split("\t", 1)[1].strip())
    return dict(apps)


def build_catalog(
    definitions: dict[str, dict[str, str]],
    apps: dict[str, set[str]],
    source: str,
    packages_discovered: int | None = None,
) -> dict:
    declared_by: dict[str, set[str]] = defaultdict(set)
    for package, permissions in apps.items():
        for permission in permissions:
            declared_by[permission].add(package)

    all_names = set(definitions) | set(declared_by)
    permissions = {}
    for name in sorted(all_names):
        definition = definitions.get(name, {})
        if name.startswith("android.permission."):
            kind = "framework"
        elif name in definitions:
            kind = "defined-on-device"
        else:
            kind = "declared-without-definition"
        permissions[name] = {
            "kind": kind,
            "defining_package": definition.get("defining_package"),
            "protection_level": definition.get("protection_level"),
            "declared_by_count": len(declared_by.get(name, set())),
            "declared_by": sorted(declared_by.get(name, set())),
        }

    return {
        "schema": "android-system-permissions/device-catalog-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "packages_scanned": len(apps),
        "packages_with_declarations": len(apps),
        "packages_discovered": packages_discovered if packages_discovered is not None else len(apps),
        "declared_permission_rows": sum(len(x) for x in apps.values()),
        "unique_permission_names": len(all_names),
        "permissions": permissions,
        "apps": {package: sorted(names) for package, names in sorted(apps.items())},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="collect from this Android host through su")
    parser.add_argument("--definitions", help="saved dumpsys package file")
    parser.add_argument("--requested", help="saved package/requested TSV file")
    parser.add_argument("--package-paths", help="optional package/path TSV to count all discovered packages")
    parser.add_argument("--output", required=True)
    parser.add_argument("--work-dir", default=".scan-work")
    args = parser.parse_args()
    if args.local == bool(args.definitions or args.requested):
        parser.error("use --local, or provide both --definitions and --requested")

    if args.local:
        definitions_path, requested_path = collect_local(Path(args.work_dir))
        source = "local device via su: dumpsys package + batched pm dump"
    else:
        if not (args.definitions and args.requested):
            parser.error("both --definitions and --requested are required offline")
        definitions_path, requested_path = Path(args.definitions), Path(args.requested)
        source = "offline sanitized device snapshot"

    catalog = build_catalog(
        parse_definitions(definitions_path.read_text(encoding="utf-8", errors="replace")),
        parse_requested(requested_path.read_text(encoding="utf-8", errors="replace")),
        source,
        packages_discovered=(
            sum(1 for line in definitions_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.startswith("  Package ["))
            if args.local
            else (
                sum(1 for line in Path(args.package_paths).read_text(encoding="utf-8", errors="replace").splitlines() if line.strip())
                if args.package_paths
                else None
            )
        ),
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: catalog[k] for k in ("packages_scanned", "declared_permission_rows", "unique_permission_names")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
