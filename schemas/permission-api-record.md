# Permission API record schema

Each record should answer one narrow compatibility question.

```yaml
id: android.permission-manager.query-permissions
api_levels:
  introduced: 23
  changed: [30, 33, 35]
kind: public | system-api | hidden | shell | oem
subject: PermissionManager
symbol: queryPermissionsByGroup
semantics:
  definition_or_usage: definition | usage | both | not-applicable
  caller_boundary: app | privileged | system | shell | reflection
source:
  - repository: platform/frameworks/base
    ref: android-<tag>
    path: <path>
    symbol: <class-or-method>
    lines: <optional line range>
    url: <permalink>
observations:
  - device: <model>
    build: <fingerprint or sanitized build id>
    android_api: <integer>
    command_or_code: <reproducer>
    result: <observed result>
    artifact: devices/<file>
assessment:
  aosp_behavior: <what source establishes>
  compatibility_difference: <OEM/API-level difference or none known>
  confidence: confirmed | observed | inferred | unknown
  libchecker_impact: <runtime/data impact>
```

Rules:

- Keep one API behavior per record; split unrelated changes.
- Preserve exact symbols and identifiers.
- Use immutable source permalinks where possible.
- Never turn an inference into an AOSP fact.
- API-level lists describe framework/API behavior, not device support alone.
