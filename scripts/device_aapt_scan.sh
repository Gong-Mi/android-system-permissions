#!/system/bin/sh
# Read package<TAB>base.apk paths generated from one dumpsys package snapshot.
# aapt2 is an absolute Termux path because su's PATH is system-only.
pathfile="${1:-/data/data/com.termux/files/home/android-system-permissions/devices/.package-paths.tsv}"
cat "$pathfile" \
  | xargs -n2 -P8 sh -c '
p="$1"
apk="$2"
perms="$(/data/data/com.termux/files/usr/bin/aapt2 dump permissions "$apk" 2>/dev/null | grep "^uses-permission: name=" | cut -d= -f2 | cut -c2- | rev | cut -c2- | rev | tr "\n" ",")"
printf "PKG\\t%s\\t%s\\n" "$p" "$perms"
' sh
