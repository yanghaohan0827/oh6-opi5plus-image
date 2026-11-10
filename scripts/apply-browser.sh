#!/bin/sh
# Enable CONFIG_PID_NS kernel + matching rtw89 modules (ArkWeb renderer fix).
# Run on the device as root:
#   sh apply-browser.sh [/data/local/tmp/oh6-patch]
set -eu

D=${1:-/data/local/tmp/oh6-patch}
[ "$(id -u)" = "0" ] || { echo "error: root shell required"; exit 1; }
[ -f "$D/boot.fixed.img" ] || { echo "error: missing $D/boot.fixed.img"; exit 1; }
for m in rtw89_core rtw89_pci rtw89_8852b rtw89_8852be; do
    [ -f "$D/modules/$m.ko" ] || { echo "error: missing $D/modules/$m.ko"; exit 1; }
done

P=$(readlink -f /dev/block/by-name/boot_linux 2>/dev/null || true)
[ -n "$P" ] || P=/dev/block/mmcblk1p5
[ -b "$P" ] || { echo "error: boot partition $P not found"; exit 1; }

isize=$(wc -c < "$D/boot.fixed.img")
psize=$(blockdev --getsize64 "$P")
[ "$isize" -le "$psize" ] || { echo "error: image $isize bytes > partition $psize bytes"; exit 1; }
[ "$isize" -eq 100663296 ] || echo "warning: unexpected boot image size $isize"

echo "backing up $P to $D/boot.before-apply.img ..."
dd if="$P" of="$D/boot.before-apply.img" bs=1M
echo "writing $D/boot.fixed.img to $P ..."
dd if="$D/boot.fixed.img" of="$P" bs=1M conv=fsync
sync

KO=$(find /vendor /system -name rtw89_8852be.ko 2>/dev/null | head -n 1)
[ -n "$KO" ] || { echo "error: rtw89_8852be.ko not found"; exit 1; }
MDIR=${KO%/*}
case "$MDIR" in
    /vendor/*) mount -o remount,rw /vendor 2>/dev/null || true ;;
    /system/*) mount -o remount,rw / 2>/dev/null || true ;;
esac

for m in rtw89_core rtw89_pci rtw89_8852b rtw89_8852be; do
    dst=$MDIR/$m.ko
    cp -f "$dst" "$D/$m.before-apply.ko" 2>/dev/null || true
    cp -f "$D/modules/$m.ko" "$dst.new"
    chmod 644 "$dst.new"
    sync
    mv -f "$dst.new" "$dst"
    echo "replaced $dst"
done

sync
echo "browser patch installed; reboot to apply"
