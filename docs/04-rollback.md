# 04 · 回退

两个安装脚本都在 `/data/local/tmp/oh6-patch/` 留下了自动备份：

| 补丁 | 自动备份 |
| --- | --- |
| 竖屏 | `libdms.before-apply.z.so`、`librender_service.before-apply.z.so`、`libwms.before-apply.z.so`、`display_manager_config.before.xml` |
| ArkWeb | `boot.before-apply.img`、`rtw89_*.before-apply.ko` |

如果推送过 `patches/portrait/original/` 与 `dist-assets/*.original.*`，脚本也会自动使用它们。

## 回退竖屏

```sh
hdc file send scripts/rollback-portrait.sh /data/local/tmp/oh6-patch/rollback-portrait.sh
hdc shell "sh /data/local/tmp/oh6-patch/rollback-portrait.sh"
hdc shell reboot
```

恢复 3 个系统库与 `display_manager_config.xml`，并把 `persist.window.logical_pointer` 设回 `false`。重启后应回到 1920×1080 横屏。

## 回退 ArkWeb 内核补丁

```sh
hdc file send scripts/rollback-browser.sh /data/local/tmp/oh6-patch/rollback-browser.sh
hdc shell "sh /data/local/tmp/oh6-patch/rollback-browser.sh"
hdc shell reboot
```

把启动分区写回 `boot.original.img`（或安装时自动生成的 `boot.before-apply.img`），并恢复 4 个 rtw89 模块。回退后 ArkWeb 会重新出现渲染进程启动失败，这是基础镜像的已知行为。

## 完全恢复

仍无法启动时，按 [01 · 刷入基础镜像](01-flash.md) 重新制作 SD 卡。刷机只会清空 SD 卡上的系统与 `/data`，不会损坏板卡。

## 板端原始备份位置

修复时在板卡上另存了一份：`/data/local/tmp/boot-browser-backup.img`、`/data/local/tmp/browser-modules-original.tar`，以及 `/data/local/tmp/*before-portrait.z.so`。这些文件可能已被清理，以仓库内原件为准。
