# AOSP module permission ownership

The core-res mapper leaves 308 `android.permission.*` entries unresolved. A
current-source sweep of these checked-out module repositories located 121:

| Module | Located entries |
|---|---:|
| HealthFitness | 100 |
| AdServices | 20 |
| PermissionController | 5 |
| Car | 0 |
| frameworks/base outside core/res | 0 |

Machine-readable result:

```text
api/local-android16-permission-directory-aosp-modules.json
```

## Confirmed module ownership

HealthFitness owns the `android.permission.health.*` family and the Health
Connect management permissions. Relevant source anchors include:

```text
packages/modules/HealthFitness/apk/HealthPermissionsManifest.xml
packages/modules/HealthFitness/framework/java/android/health/connect/HealthPermissions.java
packages/modules/HealthFitness/framework/java/android/health/connect/HealthConnectManager.java
packages/modules/HealthFitness/framework/api/current.txt
```

AdServices owns the AdServices permission family. Relevant anchors include:

```text
packages/modules/AdServices/adservices/apk/AdExtServicesManifest.xml
packages/modules/AdServices/adservices/framework/java/android/adservices/common/AdServicesPermissions.java
packages/modules/AdServices/adservices/framework/api/current.txt
```

PermissionController references selected Health Connect permission UI/role
policy and `MAINLINE_NETWORK_STACK`, but it is not the defining source for the
whole HealthFitness family.

## API-version boundary

The module sweep records current source ownership and API surface paths. It
leaves `module_first_seen_api` null because a current module branch does not
prove when the permission was introduced. Module history/API baselines must be
mapped separately, using module-specific release tags or `api_history` files.

The remaining 187 entries were not found in these checked-out module trees.
They need additional repositories (Connectivity, UWB, AppSearch, Car subtrees,
OEM framework source) or are malformed/stale permissions from installed APKs.
