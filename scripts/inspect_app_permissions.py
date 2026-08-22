#!/usr/bin/env python3
"""Inspect one installed Android app's declared permissions.

Examples:
  inspect_app_permissions.py --package com.example.app
  inspect_app_permissions.py --package com.example.app --root --fallback known_permissions.json
  inspect_app_permissions.py --dump pm-dump.txt --packages pm-packages.txt

The adb mode collects `pm dump <package>` and `pm list packages`. The dump mode
makes the same classifier usable with sanitized evidence files and CI fixtures.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Permission:
    name: str
    kind: str
    status: str
    evidence: str


def run(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise SystemExit(f"command not found: {cmd[0]}; use --dump/--packages offline") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout).strip()
        raise SystemExit(f"command failed ({exc.returncode}): {' '.join(cmd)}\n{detail}") from exc
    return result.stdout


def adb_shell(serial: str | None, command: str, root: bool) -> str:
    prefix = ["adb"] + (["-s", serial] if serial else []) + ["shell"]
    if root:
        return run(prefix + ["su", "-c", command])
    return run(prefix + ["sh", "-c", command])


def local_shell(command: str) -> str:
    """Run a package-manager command on the Android host itself."""
    return run(["su", "-c", command])


def declared_permissions(dump: str) -> set[str]:
    names: set[str] = set()
    in_requested = False
    for raw in dump.splitlines():
        line = raw.rstrip()
        if re.search(r"\brequested permissions:\s*$", line):
            in_requested = True
            continue
        if in_requested:
            if re.match(r"\s{4}install permissions:\s*$", line):
                in_requested = False
                continue
            match = re.match(r"\s{6,}([A-Za-z][\w.]+)(?::|$)", line)
            if match:
                names.add(match.group(1))
                continue
            if line and not line.startswith(" "):
                in_requested = False
    # Some Android versions print the block as `requested permissions:` followed
    # by lines with a different indentation. Accept the common `name: granted=`
    # form without scanning unrelated package fields.
    if not names:
        block = re.search(
            r"requested permissions:\s*\n(.*?)(?=\n\s*install permissions:|\n\s*runtime permissions:|\Z)",
            dump,
            re.S,
        )
        if block:
            names.update(re.findall(r"^\s+([A-Za-z][\w.]+):", block.group(1), re.M))
    return names


def granted_permissions(dump: str) -> set[str]:
    # pm dump lines vary, but granted entries conventionally contain granted=true.
    return set(re.findall(r"^\s*([A-Za-z][\w.]+): granted=true\b", dump, re.M))


def installed_packages(text: str) -> set[str]:
    return {
        line.strip()[len("package:") :]
        for line in text.splitlines()
        if line.strip().startswith("package:")
    }


def fallback_names(path: str | None) -> set[str]:
    if not path:
        return set()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data.get("permissions"), dict):
        return set(data["permissions"])
    if isinstance(data.get("permissions"), list):
        return {str(item["name"] if isinstance(item, dict) else item) for item in data["permissions"]}
    raise SystemExit(f"unsupported fallback format: {path}")


def classify(dump: str, packages: set[str], fallback: set[str]) -> list[Permission]:
    granted = granted_permissions(dump)
    result: list[Permission] = []
    for name in sorted(declared_permissions(dump)):
        if name.startswith("android.permission."):
            result.append(Permission(name, "framework", "resolvable", "android package"))
        elif name in granted:
            result.append(Permission(name, "third-party", "resolvable", "granted=true"))
        elif name in fallback:
            result.append(Permission(name, "third-party", "fallback", "bundled fallback"))
        else:
            # Do not claim the permission-name prefix is its defining package.
            # Package presence is only a hint and is explicitly marked as such.
            prefix = next((p for p in packages if name.startswith(p + ".")), None)
            if prefix:
                result.append(Permission(name, "third-party", "candidate", f"package-prefix={prefix}"))
            else:
                result.append(Permission(name, "third-party", "unresolvable", "no defining evidence"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", help="installed package name; collect through adb")
    parser.add_argument("--serial", help="adb serial")
    parser.add_argument("--root", action="store_true", help="run adb shell commands through su")
    parser.add_argument("--local", action="store_true", help="collect from this Android host through su")
    parser.add_argument("--dump", help="offline pm dump file")
    parser.add_argument("--packages", help="offline pm list packages file")
    parser.add_argument("--fallback", help="LibChecker known_permissions.json")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    if bool(args.package) == bool(args.dump):
        parser.error("choose exactly one of --package or --dump")

    if args.package:
        if args.local:
            dump = local_shell(f"pm dump {args.package}")
            package_text = local_shell("pm list packages -u")
        else:
            dump = adb_shell(args.serial, f"pm dump {args.package}", args.root)
            package_text = adb_shell(args.serial, "pm list packages -u", args.root)
    else:
        dump = Path(args.dump).read_text(encoding="utf-8", errors="replace")
        package_text = (
            Path(args.packages).read_text(encoding="utf-8", errors="replace")
            if args.packages
            else ""
        )

    rows = classify(dump, installed_packages(package_text), fallback_names(args.fallback))
    counts = {
        "declared": len(rows),
        "framework_resolvable": sum(r.kind == "framework" for r in rows),
        "third_party_resolvable": sum(r.status == "resolvable" and r.kind != "framework" for r in rows),
        "fallback": sum(r.status == "fallback" for r in rows),
        "candidate_needs_verification": sum(r.status == "candidate" for r in rows),
        "unresolvable": sum(r.status == "unresolvable" for r in rows),
    }
    if args.json:
        print(json.dumps({"counts": counts, "permissions": [asdict(r) for r in rows]}, ensure_ascii=False, indent=2))
        return 0
    print("declared:                      ", counts["declared"])
    print("framework resolvable:          ", counts["framework_resolvable"])
    print("third-party resolvable:        ", counts["third_party_resolvable"])
    print("fallback-covered:              ", counts["fallback"])
    print("candidate, verify definer:     ", counts["candidate_needs_verification"])
    print("unresolvable:                  ", counts["unresolvable"])
    for row in rows:
        print(f"{row.status:12} {row.name} [{row.evidence}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
