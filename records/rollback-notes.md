# 竖屏异常的回退步骤（仅用于本机调试）

若替换组件后系统不能正常显示，可通过 hdc 或 COM11 串口恢复。先确认 /data/local/tmp 中的备份文件存在；原件也已保存到本目录。

```sh
mount -o remount,rw /
cp /data/local/tmp/libdms.before-portrait.z.so /system/lib64/libdms.rollback.new
chmod 644 /system/lib64/libdms.rollback.new
mv /system/lib64/libdms.rollback.new /system/lib64/libdms.z.so
# 渲染服务原件将在替换前保存为 librender_service.before-portrait.z.so
cp /data/local/tmp/librender_service.before-portrait.z.so /system/lib64/librender_service.rollback.new
chmod 644 /system/lib64/librender_service.rollback.new
mv /system/lib64/librender_service.rollback.new /system/lib64/librender_service.z.so
sync
```

通过 hdc 将 display_manager_config.original.xml 写回 /vendor/etc/window/resources/display_manager_config.xml（先将 /vendor 重挂为可写，完成后 chmod 644 和 sync）。设置 persist.rosen.hardwarecomposer.enabled=true。重启后应恢复 1920×1080。不要在运行中直接截断覆盖正在使用的 .so 文件，使用临时文件和同目录 mv。
