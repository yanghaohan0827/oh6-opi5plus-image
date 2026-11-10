# 03 · 验收

以下项目在 2026-11-07 的 Orange Pi 5 Plus 实机上逐项通过，记录见 [`records/`](../records/)。

## 一键只读检查

```sh
hdc file send scripts/verify-on-device.sh /data/local/tmp/oh6-verify.sh
hdc shell "sh /data/local/tmp/oh6-verify.sh"
```

## 竖屏

| 检查 | 命令 | 期望 |
| --- | --- | --- |
| 逻辑指针开关 | `hdc shell "param get persist.window.logical_pointer"` | `true` |
| 截图尺寸 | `hdc shell "snapshot_display -f /data/local/tmp/s.jpeg"`，再 `hdc file recv /data/local/tmp/s.jpeg` | 1080×1920，正向、无半屏黑边 |
| 显示层旋转 | `hdc shell "hidumper -s RenderService -a screen"` | 图层 `transformType=3`（270°），目标矩形 1920×1080，源裁切 1080×1920 |
| 鼠标 | 实机操作 | 方向正确，可到四角附近（约 0,0 与 1074,1914） |

参考截图：[docs/images/portrait-app.jpeg](images/portrait-app.jpeg)

## ArkWeb 渲染

| 检查 | 命令 | 期望 |
| --- | --- | --- |
| 内核配置 | `hdc shell "zcat /proc/config.gz \| grep CONFIG_PID_NS"` | `CONFIG_PID_NS=y` |
| 命名空间探针 | 运行 `namespace-probe` | 子进程 PID=1，子进程退出码 0 |
| 本地网页 | 打开任意 ArkWeb 应用加载本地 HTML | 页面显示，JS 按钮能更新 DOM |
| HTTP / HTTPS | 加载网页 | 正常显示；错误网址有错误提示 |

修复前日志特征：`nwebspawn` 以 `sandboxNsFlags=0x60000000` 创建命名空间返回 `errno=22`，随后 `render pid=0`，页面白屏。

## 回归

- 重启后竖屏仍然生效，鼠标范围不变。
- 应用热安装后可正常启动。
- 4 个 rtw89 模块替换后系统正常启动；Wi-Fi 未做单独的联网复测。

## 证据文件

- [`records/portrait-repair.md`](../records/portrait-repair.md)：竖屏定位、5 处修改、验证读数。
- [`records/browser-repair.md`](../records/browser-repair.md)：白屏根因、内核构建、最终验收。
- [`records/rollback-notes.md`](../records/rollback-notes.md)：板端原件位置与回退参考。
