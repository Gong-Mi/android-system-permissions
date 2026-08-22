# Android System Permissions

Versioned evidence base for Android system permission APIs.

This repository records, by Android API level:

- public, hidden, and `@SystemApi` permission-related APIs;
- permission-definition and permission-usage semantics;
- AOSP/framework implementation changes;
- OEM or device-specific differences;
- source-level code anchors and reproducible device observations.

It is intentionally separate from LibChecker. LibChecker consumes a curated,
versioned subset at runtime; this repository stores the history and evidence
needed to update that subset without mixing research data with app code.

## Full local-device scan

The scanner uses the Android host itself and does not require adb:

```sh
python3 scripts/scan_all_permissions.py \
  --local \
  --output api/local-android16-permission-catalog.json
```

The optimized path performs one `dumpsys package` call to obtain the device
permission-definition table, extracts each package's base APK path, then runs
`aapt2 dump permissions` in eight parallel workers. It does not invoke a root
shell once per application and does not confuse `dumpsys package` bookkeeping
fields with manifest permissions.

The checked-in snapshot contains:

- 902 discovered packages;
- 548 packages with at least one declared permission;
- 20,032 declared permission rows;
- 4,528 unique permission names;
- 2,183 permissions with an on-device defining package;
- 1,331 framework permissions;
- 1,014 declared permissions with no matching definition in this device's
  permission table.

The catalog is an evidence snapshot, not a universal Android permission list.
Its device build, API level, and OEM behavior must be recorded separately when
comparing another device.


Every entry must distinguish:

1. AOSP source or official SDK documentation;
2. observed behavior on a named device/build;
3. inference or compatibility risk.

Do not describe an API as public merely because it exists in framework source.
Record `public`, `@SystemApi`, `hidden`, shell-only, reflection-only, and OEM-only
boundaries explicitly.

## Layout

```text
api/                 API-level indexes and permission API records
aosp/                Source anchors: repository, tag, path, symbol, lines
changes/             Human-readable API-level change notes
devices/             Device dumps and reproducible observation records
schemas/             Machine-readable entry schemas
scripts/             Import, normalization, and validation tools
```

## First tracked question

The initial research target is the difference between:

- a permission defined by an installed package (`<permission>`);
- a permission requested by an app (`<uses-permission>`);
- a permission exposed by the system permission manager but not resolvable
  through the calling app's installed-package metadata.

This distinction underlies LibChecker issues #1593 and #1885 and the fallback
metadata work in `Gong-Mi/LibChecker`.

## Relationship to LibChecker

- Research and source evidence live here.
- LibChecker's generated/runtime fallback data remains in LibChecker.
- A LibChecker change should cite a commit or versioned record from this repo.
- Device dumps must be sanitized before publication; do not commit package
  paths, account identifiers, or private application data.

## Status

The repository currently contains the schema and recording workflow only. API
records are added from official AOSP/SDK sources or captured device evidence;
absence of a record is not evidence that an API did not exist.
