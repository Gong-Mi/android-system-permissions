Import, normalization, and validation scripts live here.

## Inspect an installed app

```sh
python3 scripts/inspect_app_permissions.py \
  --package com.example.app --serial <adb-serial> --root
```

For an unprivileged device shell, omit `--root`. Root is recommended on Android
11+ because package visibility can hide packages from the caller.

The output separates:

- framework permissions (`android.permission.*`);
- third-party permissions proven by `granted=true`;
- fallback-covered permissions;
- package-prefix candidates that still require verification;
- permissions with no defining evidence.

Offline mode is available for sanitized `pm dump` evidence:

```sh
python3 scripts/inspect_app_permissions.py \
  --dump devices/<package>-pm-dump.txt \
  --packages devices/pm-packages.txt \
  --fallback ../LibChecker/app/src/main/assets/permissions/known_permissions.json \
  --json
```
