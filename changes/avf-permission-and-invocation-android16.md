# AVF invocation and permission gates: Android 16

This record connects the Android Virtualization Framework (AVF) API surface to
its permission enforcement path. It does not claim that a VM successfully boots
on a particular device; runtime capability and guest boot are separate evidence.

## Permission records

The local Android 16 permission directory contains:

| Permission | Device definition | Protection level |
|---|---|---|
| `android.permission.MANAGE_VIRTUAL_MACHINE` | `com.android.virtualmachine.res` | `signature|development|preinstalled` |
| `android.permission.USE_CUSTOM_VIRTUAL_MACHINE` | `com.android.virtualmachine.res` | `signature|development` |

Both permissions are absent from `frameworks/base/core/res/AndroidManifest.xml`
in the checked framework manifest sweep. They are AVF/module-owned permissions,
not evidence that the framework permission is absent.

## Java API entry point

The framework client obtains the manager through the system service registry:

```java
VirtualMachineManager vmm =
        context.getSystemService(VirtualMachineManager.class);
```

AOSP source anchor:

```text
avf-android16-reference/libs/framework-virtualization/README.md:35
avf-android16-reference/libs/framework-virtualization/src/android/system/virtualmachine/VirtualizationFrameworkInitializer.java:47-53
```

The manager API operates on `VirtualMachine` objects and VM descriptors/configs.
The Java call is only the client entry point; it does not by itself prove that
`virtmgr`, `virtualizationservice`, crosvm, or a hypervisor backend is available.

## Binder/service enforcement

The AVF service checks the Binder caller UID/PID through the Android permission
service. Root UID 0 is allowed by this implementation; other callers must pass
`IPermissionController.checkPermission()`:

```text
android/virtualizationservice/src/aidl.rs:951-967
```

The service-specific gates are:

```text
android/virtualizationservice/src/aidl.rs:974-982
android/virtmgr/src/aidl.rs:1624-1640
```

They check:

```text
MANAGE_VIRTUAL_MACHINE
USE_CUSTOM_VIRTUAL_MACHINE
```

The relevant distinction is:

- `MANAGE_VIRTUAL_MACHINE`: management operations such as VM lifecycle/control;
- `USE_CUSTOM_VIRTUAL_MACHINE`: custom VM configuration/descriptors and other
  non-default VM inputs, where the individual AIDL field also documents this
  requirement.

The exact operation-to-gate mapping must be read from the individual Binder
method; possessing both permissions does not guarantee every feature.

## AIDL custom-configuration evidence

The AVF AIDL explicitly annotates custom VM configuration fields:

```text
android/virtualizationservice/aidl/android/system/virtualizationservice/VirtualMachineAppConfig.aidl:56
android/virtualizationservice/aidl/android/system/virtualizationservice/VirtualMachineAppConfig.aidl:74
android/virtualizationservice/aidl/android/system/virtualizationservice/VirtualMachineAppConfig.aidl:104
android/virtualizationservice/aidl/android/system/virtualizationservice/VirtualMachineAppConfig.aidl:142
```

Those annotations establish the permission contract for the API payload. They do
not establish that the target device grants the permission or supports the
requested hypervisor backend.

## Evidence separation

```text
manifest declaration
  -> app requests the permission

package-manager grant / Binder check
  -> caller is authorized for the protected AVF operation

VirtualMachineManager / Binder transaction
  -> AVF request reaches virtmgr or virtualizationservice

virtmgr -> crosvm -> /dev/gzvm or /dev/kvm
  -> selected virtualization backend is opened

guest console/userspace/module evidence
  -> VM actually booted and the guest workload was verified
```

For the Redmi K90 Max evidence in the adjacent GZVM investigation, the first
three layers were observed for the debug client, and crosvm opened `/dev/gzvm`.
That is not equivalent to `/dev/kvm` availability or successful OTA4003 guest
userspace boot.
