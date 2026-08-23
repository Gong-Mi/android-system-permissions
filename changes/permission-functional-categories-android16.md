# Android 16 permission functional categories

Snapshot: `api/local-android16-permission-catalog.json`.

The directory contains 4,559 unique names after extracting only the quoted
permission name from `aapt2 dump permissions` output. The classifier below is a
mutually exclusive, name-based first pass over the 1,317 entries in the
`android.permission.*` namespace. Non-framework names are not assigned a
framework function merely because a token happens to look similar.

## Result: 17 top-level classes

| Class | Count | Confidence from name alone |
|---|---:|---|
| Framework other; source lookup needed | 607 | framework-owned, exact operation not safe to infer from name alone |
| Sensors / health / biometric | 126 | high for `BODY_SENSORS`, `ACTIVITY_RECOGNITION`, Health Connect and biometric names; hidden service binders need source |
| Network / connectivity | 94 | high for Internet, network state, Wi-Fi, Bluetooth, NFC and VPN names |
| Security / device policy | 91 | medium: security/admin/policy names identify the subsystem, not always the exact operation |
| Storage / media | 66 | high for external storage, media, download and media-provider names |
| UI / window / input / accessibility | 60 | medium to high; exact exported service or internal UI behavior needs source |
| Telephony / SMS / MMS | 59 | high for phone, SMS, MMS, call, IMS and voicemail names |
| Package / app management | 59 | high for package visibility, installation, deletion and package-manager names |
| Notifications / haptics | 31 | high for notification listener/assistant/policy and vibration names |
| Camera / microphone / capture | 27 | high for camera, audio recording, capture and media-projection names |
| Accounts / credentials | 25 | high for account manager, credential provider and authenticator names |
| Location | 24 | high for coarse/fine/background location and GPS/geofence names |
| Power / boot / alarm | 23 | high for wake lock, battery, boot, alarm and scheduling names |
| Foreground service | 12 | high for service-type declarations; this describes service eligibility, not a user grant by itself |
| Contacts / calendar | 7 | high for contacts and calendar names |
| Ads / privacy / attribution | 6 | high for AdServices, attribution, protected-signals and topics names |
| Vendor / app-specific / non-standard | 3,242 | not safely inferable from name alone |

The counts sum to 4,559. The large final class includes third-party permissions,
OEM permissions, malformed declarations and permissions whose name does not use
the Android framework namespace. It is intentionally not split into guessed
functional categories.

## What can be determined concretely

These names are strong functional evidence, subject to the permission's
protection level and caller restrictions:

- `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`,
  `ACCESS_BACKGROUND_LOCATION`: location access.
- `INTERNET`, `ACCESS_NETWORK_STATE`, `ACCESS_WIFI_STATE`,
  `CHANGE_WIFI_STATE`, Bluetooth/NFC/VPN permissions: network or nearby-device
  connectivity.
- `READ_MEDIA_*`, `MANAGE_EXTERNAL_STORAGE`, external-storage and download
  permissions: media/storage or download-provider access.
- `READ_PHONE_STATE`, `READ_SMS`, `SEND_SMS`, call, IMS and voicemail
  permissions: telephony and messaging data/operations.
- `READ_CONTACTS`, `WRITE_CONTACTS`, `READ_CALENDAR`, `WRITE_CALENDAR`:
  contacts/calendar data.
- `CAMERA`, `RECORD_AUDIO`, capture and media-projection permissions: camera,
  microphone or screen/media capture.
- `BODY_SENSORS`, `ACTIVITY_RECOGNITION`, `android.permission.health.*`,
  biometric/fingerprint permissions: sensors, health or biometric services.
- `POST_NOTIFICATIONS`, notification listener/assistant/policy and vibration
  permissions: notification delivery, observation, policy or haptics.
- `WAKE_LOCK`, boot, battery, alarm and exact-scheduling permissions: power,
  boot or scheduled execution.
- `QUERY_ALL_PACKAGES`, install/uninstall, package-verifier and package-manager
  permissions: package visibility or package lifecycle management.
- `SYSTEM_ALERT_WINDOW`, status-bar, accessibility, input and window
  permissions: UI/window/input/accessibility control.
- Account-manager, authenticator and credential-provider permissions: account
  or credential integration.
- `FOREGROUND_SERVICE_*`: foreground-service type eligibility. The permission
  does not by itself prove that the app is currently running that service.

## What cannot be determined from the directory alone

A permission name is not enough to establish:

- whether an app can actually obtain or exercise it;
- whether the permission is runtime-grantable, signature-only, privileged,
  role-bound, installer-bound or OEM-only;
- the exact API call or Binder transaction controlled by a hidden permission;
- the behavior of `com.xiaomi.*`, `com.miui.*`, `com.oplus.*`, `com.vivo.*`,
  `com.android.*` private permissions or other third-party permissions;
- whether a permission is merely a broadcast/provider/service protection token;
- whether a malformed or stale manifest string has any effect.

For those cases the next evidence layer is the on-device permission definition
(`defining_package`, `protection_level`) plus that defining package's manifest,
framework source or OEM source. A permission absent from this device's definition
table is not automatically meaningless on another Android/OEM build.

## Classification boundary

This is a directory-level functional taxonomy, not a replacement for API-level
source mapping. Exact API changes should be recorded separately with AOSP tag,
source path, symbol and API level in a permission API record.
