#!/bin/sh
# Read-only checks to run on the device after applying the patches.
set -u

echo '== kernel namespaces =='
zcat /proc/config.gz 2>/dev/null | grep -E '^CONFIG_(PID_NS|NET_NS)=' || echo 'cannot read /proc/config.gz'

echo '== logical pointer =='
param get persist.window.logical_pointer 2>/dev/null || echo 'param get failed'

echo '== screenshot =='
if snapshot_display -f /data/local/tmp/oh6-verify.jpeg; then
    echo 'saved /data/local/tmp/oh6-verify.jpeg (expect 1080x1920)'
else
    echo 'snapshot_display failed'
fi
