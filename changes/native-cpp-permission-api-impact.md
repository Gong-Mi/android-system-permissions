# Native C/C++ permission and API-level impact

Sources inspected:

- `platform/frameworks/native/libs/binder/PermissionCache.cpp`
- `platform/frameworks/native/libs/permission/android/permission/PermissionChecker.cpp`
- `platform/frameworks/native/libs/gui/BufferQueueConsumer.cpp`
- `platform/frameworks/native/services/surfaceflinger/SurfaceFlinger.cpp`
- `platform/frameworks/native/services/sensorservice/SensorService.cpp`
- `platform/frameworks/native/libs/binder/ndk/include_cpp/android/binder_interface_utils.h`

## Native permission strings found

The current frameworks/native C/C++ tree contains 16 literal Android permission
names. All 16 are present in the local AOSP-enriched directory and are mapped to
an AOSP core-res API-era tag:

| Permission | Native use | First seen API |
|---|---|---:|
| `ACCESS_GPU_SERVICE` | GPU service access gate | 34 |
| `ACCESS_SURFACE_FLINGER` | SurfaceFlinger privileged operations | 4 |
| `ACTIVITY_RECOGNITION` | activity-recognition service path | 29 |
| `CAPTURE_BLACKOUT_CONTENT` | capture of protected/blackout content | 31 |
| `CONTROL_DISPLAY_BRIGHTNESS` | display brightness control | 28 |
| `DUMP` | diagnostic/state dump access | 4 |
| `HARDWARE_TEST` | hardware-test operations | 4 |
| `HIGH_SAMPLING_RATE_SENSORS` | high-rate sensor sampling | 31 |
| `INTERNAL_SYSTEM_WINDOW` | internal window access | 4 |
| `LOCATION_HARDWARE` | hardware location access | 18 |
| `MANAGE_SENSORS` | sensor management | 28 |
| `OBSERVE_PICTURE_PROFILES` | picture-profile observation | 36 |
| `READ_FRAME_BUFFER` | framebuffer read access | 4 |
| `REGISTER_STATS_PULL_ATOM` | stats pull-atom registration | 30 |
| `ROTATE_SURFACE_FLINGER` | SurfaceFlinger rotation control | 31 |
| `WAKEUP_SURFACE_FLINGER` | SurfaceFlinger wakeup control | 34 |

`First seen API` has the same tag-window meaning as the AOSP mapping report: it
is the first matching tag available in the Android 1.6/API 4 through Android
16/API 36 sweep, and API 4 entries can predate the available window.

## What changes in native C/C++

### 1. Permission semantics are runtime Binder policy, not C preprocessor API

`PermissionCache::checkPermission()` caches a result by permission name and UID,
then calls the system permission service when the cache misses. The native code
does not decide whether a permission is dangerous, signature, privileged, role
bound, or AppOp-controlled. That policy is supplied by the framework permission
service.

The cache explicitly treats root and the process itself as allowed, and it does
not cache the PID. A permission-name directory therefore cannot be used as a
native authorization result.

### 2. Data-delivery checks add attribution and AppOps semantics

`PermissionChecker.cpp` sends the permission name, `AttributionSourceState`,
data-delivery/preflight flags and an attributed AppOp code through the Binder
permission checker. For native callers this means that “permission present” is
not the complete decision: attribution chain, AppOps and data-delivery state can
change the result.

### 3. Vendor/no-Binder builds have a different behavior boundary

`BufferQueueConsumer.cpp` checks `DUMP` through `PermissionCache` only when
`!__ANDROID_VNDK__ && !NO_BINDER`. In vendor or no-Binder builds the code cannot
reach PermissionController and denies non-shell callers directly. This is a
build-variant behavior difference, not an Android permission API-level change.

### 4. Native services use concrete permission gates

`SurfaceFlinger.cpp` uses `PermissionCache` for SurfaceFlinger access,
framebuffer reads, secure/blackout capture and display brightness. The string
names identify the protected operation, while the actual authorization still
comes from the Binder permission service.

`SensorService.cpp` gates high sampling rate, dump, location hardware and sensor
management with explicit permission checks.

## Separate API-level impact in C++/NDK

The Android API level affects whether native Binder APIs can be compiled or
called, independently of the permission directory:

- Binder shell-command registration is guarded at API 30.
- NDK Binder parcelable/string helpers contain API 31 guards.
- Transaction-code-to-function-name mapping is guarded at API 36.
- `__builtin_available(android N, *)`, weak unavailable symbols and
  `__ANDROID_API__` decide compile/runtime dispatch for these APIs.

Therefore native compatibility has two independent axes:

```text
permission policy axis:
  permission name → framework Binder/PermissionController/AppOps decision

native API availability axis:
  __ANDROID_API__ / __builtin_available → whether the C/C++ API symbol/path exists
```

Changing `targetSdk` or `minSdk` does not rewrite a native permission string.
It changes framework compatibility behavior and may change whether a caller can
reach an operation; the native code still needs the correct API guards and
runtime fallback.

## Boundary for the next sweep

The 16 native permission strings above are now source-backed. The remaining
unresolved permission names should be searched in module repositories and OEM
framework source. For C/C++ impact, the next useful targets are native code in
HealthFitness, AdServices, SurfaceFlinger/sensorservice-related modules and
vendor-specific service implementations; ordinary permission declarations do
not imply that a native implementation exists.
