#!/bin/sh
# Restore the original boot partition and rtw89 modules.
#   sh rollback-browser.sh [/data/local/tmp/oh6-patch]
set -eu

D=${1:-/data/local/tmp/oh6-patch}
[ "$(id -u)" = "0" ] || { echo "error: root shell required"; exit 1; }

ORIG=$D/boot.original.img
[ -f "$ORIG" ] || ORIG=$D/boot.before-apply.img
[ -f "$ORIG" ] || { echo "error: no boot partition backup"; exit 1; }

P=$(readlink -f /dev/block/by-name/boot_linux 2>/dev/null || true)
[ -n "$P" ] || P=/dev/block/mmcblk1p5
[ -b "$P" ] || { echo "error: boot partition $P not found"; exit 1; }

isize=$(wc -c < "$ORIG")
psize=$(blockdev --getsize64 "$P")
[ "$isize" -le "$psize" ] || { echo "error: backup larger than partition"; exit 1; }
echo "restoring $ORIG to $P ..."
dd if="$ORIG" of="$P" bs=1M conv=fsync
sync

if [ -f "$D/modules.original.tar" ]; then
    mkdir -p "$D/modules-original"
    tar xf "$D/modules.original.tar" -C "$D/modules-original"
fi

KO=$(find /vendor /system -name rtw89_8852be.ko 2>/dev/null | head -n 1)
[ -n "$KO" ] || { echo "error: rtw89_8852be.ko not found"; exit 1; }
MDIR=${KO%/*}
case "$MDIR" in
    /vendor/*) mount -o remount,rw /vendor 2>/dev/null || true ;;
    /system/*) mount -o remount,rw / 2>/dev/null || true ;;
esac

for m in rtw89_core rtw89_pci rtw89_8852b rtw89_8852be; do
    src=$D/modules-original/modules/$m.ko
    [ -f "$src" ] || src=$D/$m.before-apply.ko
    [ -f "$src" ] || { echo "error: no backup for $m.ko"; exit 1; }
    cp -f "$src" "$MDIR/$m.ko.new"
    chmod 644 "$MDIR/$m.ko.new"
    sync
    mv -f "$MDIR/$m.ko.new" "$MDIR/$m.ko"
    echo "restored $MDIR/$m.ko"
done

sync
echo "browser patch rolled back; reboot to apply"
