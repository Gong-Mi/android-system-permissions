# AOSP permission/API mapping: Android 1.6-16

Generated from the local permission directory and a sparse checkout of
`platform/frameworks/base`, using these release tags:

```text
android-1.6_r1 .. android-16.0.0_r1
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
| Found in `frameworks/base/core/res/AndroidManifest.xml` | 1,009 |
| Not found in that file | 308 |
| Non-framework/vendor/app-specific entries | 3,242 |

For the 1,009 matches, each entry records:

- `first_seen_api` / `available_since_api`: first matched API level in the available AOSP tag window;
- `api_history`: every selected release tag where the definition exists, including protection-level changes;
- `source_tag`: the exact AOSP release tag used;
- `source_line`: line in that tag's manifest;
- `aosp_protection_level`: definition from the first matched tag;
- `aosp_permission_group` and `permission_flags`, when present;
- `related_permissions`, including source-backed background permissions and explicit API migration families;
- `source`: the canonical AOSP path.

First-match distribution:

```text
API 4:  111
API 5:    7
API 7:    7
API 8:   12
API 10:   3
API 14:  25
API 16:  17
API 17:  16
API 18:   9
API 19:  18
API 21:  40
API 23:  45
API 24:  36
API 26:  40
API 28:  67
API 29:  76
API 30:  59
API 31: 101
API 33:  76
API 34: 147
API 35:  65
API 36:  39
```

## Related and replacement permissions

The mapper records only relationships with explicit evidence or a narrow,
well-defined API family:

- `ACCESS_FINE_LOCATION` / `ACCESS_COARSE_LOCATION` are a precision pair; both
  point to `ACCESS_BACKGROUND_LOCATION` through AOSP's `backgroundPermission`
  attribute.
- `CAMERA` points to `BACKGROUND_CAMERA` through AOSP's
  `backgroundPermission` attribute.
- `RECORD_AUDIO` points to `RECORD_BACKGROUND_AUDIO` through the same attribute.
- `BODY_SENSORS` points to `BODY_SENSORS_BACKGROUND` through the same
  attribute.
- `READ_EXTERNAL_STORAGE` is related to the API 33 media split family:
  `READ_MEDIA_IMAGES`, `READ_MEDIA_VIDEO`, `READ_MEDIA_AUDIO`, and
  `READ_MEDIA_VISUAL_USER_SELECTED`.

A related permission is not automatically interchangeable. For example,
background permission normally requires the foreground/base permission and may
have separate targetSdk, AppOps, role, or runtime-grant rules.

## Confirmed examples

| Permission | First API | AOSP protection level | Function |
|---|---:|---|---|
| `android.permission.INTERNET` | 4 (earliest available tag) | `normal\|ephemeral` in API 4 tag | create network sockets |
| `android.permission.CAMERA` | 4 (earliest available tag) | `dangerous\|ephemeral` in API 4 tag | camera access |
| `android.permission.QUERY_ALL_PACKAGES` | 11 | `normal` | package visibility |
| `android.permission.MANAGE_EXTERNAL_STORAGE` | 11 | `signature\|appop\|preinstalled` | broad external-storage management |
| `android.permission.POST_NOTIFICATIONS` | 13 | `dangerous\|instant` | post notifications |
| `android.permission.READ_MEDIA_IMAGES` | 13 | `dangerous` | read images from shared media |

## Meaning of `first_seen_api`

`first_seen_api` means the earliest matching release tag available in this
checkout. The current tag window starts at Android 1.6 / API 4 because this
AOSP repository does not expose the Android 1.0-1.5 framework tags under the
names searched here. Therefore API 4 entries are lower bounds, not proof that
the permission was introduced in API 4. For API 5 and later entries, the tag
window covers the corresponding major release but still does not provide an
exact development commit.

## The 308 unresolved framework names

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
