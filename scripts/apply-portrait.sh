#!/bin/sh
# OpenHarmony 6.0 portrait patch for RK3588 / Orange Pi 5 Plus.
# Run on the device as root:
#   sh apply-portrait.sh [/data/local/tmp/oh6-patch]
set -eu

D=${1:-/data/local/tmp/oh6-patch}
[ "$(id -u)" = "0" ] || { echo "error: root shell required"; exit 1; }

for f in libdms librender_service libwms; do
    [ -f "$D/$f.z.so" ] || { echo "error: missing $D/$f.z.so"; exit 1; }
done
[ -f "$D/display_manager_config.xml" ] || { echo "error: missing $D/display_manager_config.xml"; exit 1; }

mount -o remount,rw / 2>/dev/null || true
for f in libdms librender_service libwms; do
    dst=/system/lib64/$f.z.so
    [ -f "$dst" ] || { echo "error: $dst not found"; exit 1; }
    cp -f "$dst" "$D/$f.before-apply.z.so" 2>/dev/null || true
    cp -f "$D/$f.z.so" "$dst.new"
    chmod 644 "$dst.new"
    sync
    mv -f "$dst.new" "$dst"
    echo "replaced $dst"
done

V=/vendor/etc/window/resources/display_manager_config.xml
[ -f "$V" ] || { echo "error: $V not found"; exit 1; }
mount -o remount,rw /vendor 2>/dev/null || true
cp -f "$V" "$D/display_manager_config.before.xml" 2>/dev/null || true
cp -f "$D/display_manager_config.xml" "$V.new"
chmod 644 "$V.new"
sync
mv -f "$V.new" "$V"
echo "replaced $V"

param set persist.window.logical_pointer true 2>/dev/null || true
sync
echo "portrait patch installed; reboot to apply"
