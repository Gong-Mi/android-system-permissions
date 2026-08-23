#!/usr/bin/env python3
"""Map permission-directory entries to AOSP frameworks/base API-era sources.

This first pass covers frameworks/base/core/res/AndroidManifest.xml across
Android 8-16 release tags. A null first_api means the permission was not found
in that file; it does not prove the permission is absent from AOSP modules or
OEM source.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

TAGS = [
    (4, "android-1.6_r1"),
    (5, "android-2.0_r1"),
    (7, "android-2.1_r1"),
    (8, "android-2.2_r1"),
    (10, "android-2.3.3_r1"),
    (14, "android-4.0.1_r1"),
    (16, "android-4.1.1_r1"),
    (17, "android-4.2.2_r1"),
    (18, "android-4.3_r1"),
    (19, "android-4.4_r1"),
    (21, "android-5.0.0_r1"),
    (23, "android-6.0.0_r1"),
    (24, "android-7.0.0_r1"),
    (26, "android-8.0.0_r1"),
    (28, "android-9.0.0_r1"),
    (29, "android-10.0.0_r1"),
    (30, "android-11.0.0_r1"),
    (31, "android-12.0.0_r1"),
    (33, "android-13.0.0_r1"),
    (34, "android-14.0.0_r1"),
    (35, "android-15.0.0_r1"),
    (36, "android-16.0.0_r1"),
]
SOURCE = "platform/frameworks/base/core/res/AndroidManifest.xml"
GIT_SOURCE = "core/res/AndroidManifest.xml"


def source_text(aosp: Path, tag: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(aosp), "show", f"{tag}:{GIT_SOURCE}"],
        text=True,
        errors="replace",
    )


def permission_blocks(text: str) -> dict[str, tuple[int, str]]:
    out = {}
    for match in re.finditer(r"^\s*<permission\b.*?(?:/>|</permission>)", text, re.M | re.S):
        block = match.group(0)
        name_match = re.search(r'android:name="([^"]+)"', block)
        if not name_match:
            continue
        name = name_match.group(1)
        line = text.count("\n", 0, match.start()) + 1
        out[name] = (line, block)
    return out


def attrs(block: str) -> dict[str, str]:
    return {
        key: value
        for key, value in re.findall(r'android:([A-Za-z]+)="([^"]+)"', block)
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aosp", required=True, type=Path)
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    directory = json.loads(args.directory.read_text(encoding="utf-8"))
    names = directory["permissions"]
    records = {}
    parsed = {tag: permission_blocks(source_text(args.aosp, tag)) for _, tag in TAGS}

    for name, old in names.items():
        record = {
            "status": "not-android-framework-namespace",
            "first_seen_api": None,
            "source": None,
            "source_line": None,
            "source_tag": None,
            "aosp_protection_level": None,
        }
        if name.startswith("android.permission."):
            record["status"] = "not-found-in-frameworks-base-core-res"
            for api, tag in TAGS:
                if name in parsed[tag]:
                    line, block = parsed[tag][name]
                    a = attrs(block)
                    record.update(
                        {
                            "status": "frameworks-base-core-res",
                            "first_seen_api": api,
                            "source": SOURCE,
                            "source_line": line,
                            "source_tag": tag,
                            "aosp_protection_level": a.get("protectionLevel"),
                        }
                    )
                    break
        records[name] = dict(old, aosp=record)

    output = dict(directory)
    output["schema"] = "android-system-permissions/permission-directory-with-aosp-v1"
    output["permissions"] = dict(sorted(records.items()))
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    found = sum(v["aosp"]["status"] == "frameworks-base-core-res" for v in records.values())
    framework = sum(n.startswith("android.permission.") for n in records)
    print(json.dumps({"permissions": len(records), "framework_namespace": framework, "core_res_found": found}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
