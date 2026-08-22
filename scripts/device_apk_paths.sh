#!/system/bin/sh
# Emit package<TAB>apk path for base and every installed split.
pm list packages -u | cut -d: -f2 | xargs -n1 -P8 sh -c '
p="$1"
pm path "$p" 2>/dev/null | while IFS= read -r line; do
path="$(printf "%s" "$line" | cut -d: -f2-)"
printf "PKG\\t%s\\t%s\\n" "$p" "$path"
done
' sh
