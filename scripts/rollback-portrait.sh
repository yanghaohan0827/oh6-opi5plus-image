#!/bin/sh
# Restore the pre-patch display libraries and orientation config.
#   sh rollback-portrait.sh [/data/local/tmp/oh6-patch]
set -eu

D=${1:-/data/local/tmp/oh6-patch}
[ "$(id -u)" = "0" ] || { echo "error: root shell required"; exit 1; }

mount -o remount,rw / 2>/dev/null || true
for f in libdms librender_service libwms; do
    src=$D/$f.before-apply.z.so
    [ -f "$src" ] || src=$D/original/$f.original.z.so
    [ -f "$src" ] || { echo "error: no backup for $f"; exit 1; }
    dst=/system/lib64/$f.z.so
    cp -f "$src" "$dst.new"
    chmod 644 "$dst.new"
    sync
    mv -f "$dst.new" "$dst"
    echo "restored $dst"
done

V=/vendor/etc/window/resources/display_manager_config.xml
src=$D/display_manager_config.before.xml
[ -f "$src" ] || src=$D/original/display_manager_config.original.xml
[ -f "$src" ] || { echo "error: no backup for display_manager_config.xml"; exit 1; }
mount -o remount,rw /vendor 2>/dev/null || true
cp -f "$src" "$V.new"
chmod 644 "$V.new"
sync
mv -f "$V.new" "$V"
echo "restored $V"

param set persist.window.logical_pointer false 2>/dev/null || true
sync
echo "portrait patch rolled back; reboot to apply"
