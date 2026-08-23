# AOSP permission/API mapping: Android 8-16

Generated from the local permission directory and a sparse checkout of
`platform/frameworks/base`, using these release tags:

```text
android-8.0.0_r1 .. android-16.0.0_r1
```

Source file checked:

```text
frameworks/base/core/res/AndroidManifest.xml
```

Machine-readable result:

```text
api/local-android16-permission-directory-aosp.json
```

## Coverage

| Result | Count |
|---|---:|
| Permission directory entries | 4,559 |
| `android.permission.*` entries | 1,317 |
| Found in `frameworks/base/core/res/AndroidManifest.xml` | 1,006 |
| Not found in that file | 311 |
| Non-framework/vendor/app-specific entries | 3,242 |

For the 1,006 matches, each entry records:

- `first_api`: first matched major Android release;
- `source_tag`: the exact AOSP release tag used;
- `source_line`: line in that tag's manifest;
- `aosp_protection_level`: definition from that tag;
- `source`: the canonical AOSP path.

First-match distribution:

```text
API 8:  376
API 9:   67
API 10:  76
API 11:  59
API 12: 101
API 13:  76
API 14: 147
API 15:  65
API 16:  39
```

## Confirmed examples

| Permission | First API | AOSP protection level | Function |
|---|---:|---|---|
| `android.permission.INTERNET` | 8 | `normal\|ephemeral` in API 8 tag | create network sockets |
| `android.permission.CAMERA` | 8 | `dangerous\|ephemeral` in API 8 tag | camera access |
| `android.permission.QUERY_ALL_PACKAGES` | 11 | `normal` | package visibility |
| `android.permission.MANAGE_EXTERNAL_STORAGE` | 11 | `signature\|appop\|preinstalled` | broad external-storage management |
| `android.permission.POST_NOTIFICATIONS` | 13 | `dangerous\|instant` | post notifications |
| `android.permission.READ_MEDIA_IMAGES` | 13 | `dangerous` | read images from shared media |

## Meaning of “first API”

`first_api` means the permission exists in the selected release tag's
`core/res/AndroidManifest.xml`. It is a major-release lower bound, not an exact
commit introduction date. A permission may have been added during an API
release's development before the selected `r1` tag, or may have been moved to a
module in a later release.

## The 311 unresolved framework names

`not-found-in-frameworks-base-core-res` means only that the permission was not
found in this one AOSP file. It does not mean “not an AOSP permission”. Likely
next source domains include:

- PermissionController / Mainline permission modules;
- Health Connect / HealthFitness;
- AdServices;
- Car / automotive framework;
- UWB, Bluetooth and other modular packages;
- OEM framework additions;
- malformed or stale manifest strings.

Those entries require a second source sweep before assigning an API version.
The mapper deliberately leaves their `first_api` null instead of guessing.

## Reproducibility

```sh
python3 scripts/map_aosp_permissions.py \
  --aosp ~/aosp-frameworks-base \
  --directory api/local-android16-permission-catalog.json \
  --output api/local-android16-permission-directory-aosp.json
```
