# Permission definition versus usage

Status: source-backed investigation target; detailed API-level records pending.

## Terms

- `<permission>` declares a permission and identifies its defining package.
- `<uses-permission>` declares that an application requests/uses a permission.
- An app that defines a permission is not automatically a consumer of that
  permission for reference statistics.

## Existing evidence

- Upstream LibChecker issue #1593 reports incomplete permission-reference
  statistics for `com.xiaomi.security.permission.ACCESS_XSOF`.
- The maintainer response distinguishes the defining package from applications
  that declare `<uses-permission>`.
- Upstream LibChecker issue #1885 discusses `PackageParser.Package.permissions`
  versus requested permissions and the difficulty of enumerating Android system
  permissions through the wrong API path.

These links are context, not substitutes for AOSP source anchors:

- https://github.com/LibChecker/LibChecker/issues/1593
- https://github.com/LibChecker/LibChecker/issues/1885

## Required follow-up records

- AOSP parser/model fields for defined and requested permissions by API level.
- PermissionManager query behavior and caller restrictions by API level.
- OEM behavior where a defining package is absent, protected, or split across
  system/system_ext/product/vendor partitions.
- A device reproduction showing which API returns label, description,
  defining package, and protection level for an unresolvable permission.
