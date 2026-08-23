# Permission access conditions: OEM and system software

Generated from the local Android 16 permission definition table and AOSP
permission mapping.

Machine-readable output:

```text
api/local-android16-permission-directory-access.json
```

## Classification

| Access scope | Count | Meaning |
|---|---:|---|
| `oem-vendor-restricted` | 17 | `oem` or `vendorPrivileged`; OEM/vendor policy is required |
| `framework-internal` | 118 | `internal`; framework-only or further role/privileged policy |
| `privileged-system-preinstalled` | 912 | privileged/system/preinstalled policy, often with platform signature/allowlist |
| `special-system-role` | 69 | installer, verifier, configurator, setup, recents, or incident approver |
| `role-restricted` | 42 | requires a specific Android role or role holder |
| `signature-restricted` | 1,732 | defining signing certificate required; not automatically system-only |
| `runtime-dangerous` | 163 | runtime/user grant, still subject to AppOps/targetSdk/restrictions |
| `normal` | 297 | normal protection, subject to extra qualifiers such as appop/instant/module |
| `unknown-no-device-definition` | 1,209 | no local protectionLevel; no access conclusion is made |

The categories sum to 4,559 directory entries.

## What is definitely OEM/vendor restricted

The strongest direct signal is a protection flag, not a package-name prefix:

```text
android.permission.ACCESS_TUNED_INFO
android.permission.ACCESS_TV_DESCRAMBLER
android.permission.ACCESS_TV_SHARED_FILTER
android.permission.ACCESS_TV_TUNER
android.permission.ALWAYS_BOUND_TV_INPUT
android.permission.BIND_IMS_SERVICE
android.permission.BIND_SATELLITE_SERVICE
android.permission.HDMI_CEC
android.permission.MANAGE_GLOBAL_PICTURE_QUALITY_SERVICE
android.permission.MANAGE_GLOBAL_SOUND_QUALITY_SERVICE
android.permission.MEDIA_RESOURCE_OVERRIDE_PID
android.permission.SINGLE_USER_TIS_ACCESS
android.permission.START_ACTIVITIES_FROM_BACKGROUND
android.permission.START_FOREGROUND_SERVICES_FROM_BACKGROUND
android.permission.TIS_EXTENSION_INTERFACE
android.permission.TUNER_RESOURCE_ACCESS
android.permission.TV_INPUT_HARDWARE
```

These have `oem` and/or `vendorPrivileged` in the local protection definition.
That is stronger evidence than names such as `com.xiaomi.*`; an OEM-looking
name without the protection evidence is not automatically OEM-only.

## What is system-software restricted

`framework-internal`, `privileged-system-preinstalled`, and
`special-system-role` are the practical system-software classes. Examples:

```text
MANAGE_DEVICE_POLICY_*
  framework device-policy controls, mostly internal/role restricted

DUMP
  privileged/development diagnostic access

BIND_INCALL_SERVICE
BIND_TELECOM_CONNECTION_SERVICE
BIND_CARRIER_SERVICES
BIND_WALLPAPER
  privileged system service/provider binding

GRANT_RUNTIME_PERMISSIONS
REVOKE_RUNTIME_PERMISSIONS
MANAGE_APP_OPS_MODES
MANAGE_ROLE_HOLDERS
  installer/verifier/role/system management
```

These should not be described as “any system APK can use them”: platform
signature, privileged allowlisting, role assignment, installer identity, and
AppOps may all be additional requirements.

## What is not system-only

- `signature` means same signing certificate as the defining package. A custom
  app-defined permission can be signature restricted without being an Android
  framework permission.
- `dangerous` means runtime-grantable in principle, not automatically granted.
- `normal` means the protection base is normal, but `appop`, `instant`, `module`
  and targetSdk behavior may still matter.
- An absent local definition means unknown, not ordinary and not unusable.

## Data-model rule

The access scope is a classification of observed protection conditions. It is
not a claim that the calling package currently holds the permission. Actual
access still requires checking package signing, privileged allowlist, role,
AppOps, user grant, targetSdk and the enforcing service.
