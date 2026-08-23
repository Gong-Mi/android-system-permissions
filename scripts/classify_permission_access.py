#!/usr/bin/env python3
"""Classify permission access conditions from protectionLevel flags."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def classify(protection: str | None) -> tuple[str, str]:
    if not protection:
        return "unknown-no-device-definition", "No protectionLevel from the local device definition."
    flags = set(protection.split("|"))
    if "oem" in flags or "vendorPrivileged" in flags:
        return "oem-vendor-restricted", "Requires OEM/vendor privileged policy; not an ordinary application permission."
    if "internal" in flags:
        return "framework-internal", "Framework-internal permission; role/privileged qualifiers may further narrow holders."
    if {"privileged", "system", "preinstalled"} & flags:
        return "privileged-system-preinstalled", "Requires platform/privileged/preinstalled policy; signature and allowlist conditions may also apply."
    if {"installer", "verifier", "configurator", "setup", "recents", "incidentReportApprover"} & flags:
        return "special-system-role", "Restricted to a system role such as installer, verifier, configurator, setup, recents, or incident approver."
    if "role" in flags:
        return "role-restricted", "Requires the corresponding Android role or role-holder policy."
    if "signature" in flags or protection == "signatureOrSystem":
        return "signature-restricted", "Requires the defining signing certificate; this is not automatically system-only."
    if "dangerous" in flags or "runtime" in flags:
        return "runtime-dangerous", "Runtime/dangerous permission; AppOps, targetSdk, restriction flags, and user grant still apply."
    if "normal" in flags:
        return "normal", "Normal permission, subject to any appop/instant/module qualifiers."
    return "restricted-other", "Restricted protection flags require source and package-policy verification."


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    counts = Counter()
    for entry in data["permissions"].values():
        aosp = entry.setdefault("aosp", {})
        protection = entry.get("protection_level") or aosp.get("aosp_protection_level")
        scope, conditions = classify(protection)
        aosp["access_scope"] = scope
        aosp["access_conditions"] = conditions
        counts[scope] += 1
    data["schema"] = "android-system-permissions/permission-directory-with-access-conditions-v1"
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
