# 02 · 应用系统补丁

两项补丁都在**已经刷好的基础镜像**上应用，按下面顺序执行。两个脚本都会先备份被替换的文件，可用 [04 · 回退](04-rollback.md) 撤销。

> 前提：`hdc shell` 能进入 **root** shell；`/data` 至少留 1 GB 空间（启动分区备份 96 MB、系统库备份约 17 MB）。

## 准备目录

```sh
hdc shell "mkdir -p /data/local/tmp/oh6-patch/original"
```

## 一、整机竖屏补丁

### 1. 推送文件

```sh
hdc file send patches/portrait/libdms.z.so /data/local/tmp/oh6-patch/libdms.z.so
hdc file send patches/portrait/librender_service.z.so /data/local/tmp/oh6-patch/librender_service.z.so
hdc file send patches/portrait/libwms.z.so /data/local/tmp/oh6-patch/libwms.z.so
hdc file send patches/portrait/display_manager_config.xml /data/local/tmp/oh6-patch/display_manager_config.xml
hdc file send scripts/apply-portrait.sh /data/local/tmp/oh6-patch/apply-portrait.sh

# 可选：同时推送原件，便于完全回退
hdc file send patches/portrait/original/libdms.original.z.so /data/local/tmp/oh6-patch/original/libdms.original.z.so
hdc file send patches/portrait/original/librender_service.original.z.so /data/local/tmp/oh6-patch/original/librender_service.original.z.so
hdc file send patches/portrait/original/libwms.original.z.so /data/local/tmp/oh6-patch/original/libwms.original.z.so
hdc file send patches/portrait/original/display_manager_config.original.xml /data/local/tmp/oh6-patch/original/display_manager_config.original.xml
```

### 2. 执行并重启

```sh
hdc shell "sh /data/local/tmp/oh6-patch/apply-portrait.sh"
hdc shell reboot
```

脚本做的事：

1. 备份 `/system/lib64/libdms.z.so`、`librender_service.z.so`、`libwms.z.so` 到 `/data/local/tmp/oh6-patch/`；
2. 先写 `.new` 临时文件，`sync` 后同目录 `mv` 原子替换（不要在运行中截断正在使用的 `.so`）；
3. 备份并替换 `/vendor/etc/window/resources/display_manager_config.xml`（`buildInDefaultOrientation` 由 0 改为 1）；
4. 设置 `persist.window.logical_pointer=true`。

### 3. 检查

见 [03 · 验收](03-verify.md)。正常表现：开机即为 1080×1920 竖屏，HDMI 仍输出 1920×1080 时序，画面由显示层旋转铺满；USB 鼠标方向与四边范围正确。

## 二、ArkWeb 渲染进程补丁（内核 PID_NS）

### 1. 推送文件

```sh
hdc file send dist-assets/boot.fixed.img /data/local/tmp/oh6-patch/boot.fixed.img
hdc file send dist-assets/modules.fixed.tar /data/local/tmp/oh6-patch/modules.fixed.tar
hdc file send scripts/apply-browser.sh /data/local/tmp/oh6-patch/apply-browser.sh

# 可选：回退用的原始启动分区与模块
hdc file send dist-assets/boot.original.img /data/local/tmp/oh6-patch/boot.original.img
hdc file send dist-assets/modules.original.tar /data/local/tmp/oh6-patch/modules.original.tar
```

### 2. 解压模块并执行

```sh
hdc shell "cd /data/local/tmp/oh6-patch && tar xf modules.fixed.tar"
hdc shell "sh /data/local/tmp/oh6-patch/apply-browser.sh"
hdc shell reboot
```

脚本做的事：

1. 自动定位启动分区：优先 `/dev/block/by-name/boot_linux`，否则 `/dev/block/mmcblk1p5`；
2. 校验镜像不大于分区，先把原分区完整备份为 `boot.before-apply.img`；
3. 用 `dd conv=fsync` 写入 `boot.fixed.img`（只替换了 `/extlinux/Image`，保留 `extlinux.conf` 与 `toybrick.dtb`）；
4. 在 `/vendor` 或 `/system` 下找到现有 `rtw89_8852be.ko` 所在目录，原子替换 4 个 rtw89 模块。

### 3. 检查

```sh
hdc shell "zcat /proc/config.gz | grep CONFIG_PID_NS"
# 期望：CONFIG_PID_NS=y

hdc file send patches/browser/namespace-probe /data/local/tmp/namespace-probe
hdc shell "chmod +x /data/local/tmp/namespace-probe && /data/local/tmp/namespace-probe"
# 期望：render-style namespace child pid=1
#       namespace clone succeeded, child status=0
```

## 注意事项

- **写入启动分区时不要断电**，`dd` 完成后会自动 `sync`，再执行重启。
- 补丁直接替换系统库与内核，属于开发/评测用途，不是签名 OTA；量产设备应改为正式 OTA 流程。
- 若 `dd` 或替换中途失败，用 [04 · 回退](04-rollback.md) 恢复；完全无法启动时重新刷基础镜像。
- 不同载板、不同屏幕参数的设备不要直接套用，需要重新适配显示配置。
