# 浏览器白屏修复记录 · 2026-11-07

状态：已完成上板修复与验收。

## 已定位的故障

浏览器包 com.example.simplebrowser 已加载 ArkWeb 引擎，但渲染进程无法启动。日志显示 nwebspawn 用 sandboxNsFlags=0x60000000 创建 PID 与网络命名空间时失败，errno=22；AMS 随后报告 render pid=0。板端 /proc/config.gz 显示 CONFIG_NET_NS=y，但 CONFIG_PID_NS 未启用。

独立 namespace-probe 使用同样的命名空间标志复现 errno=22，确认问题在系统能力而非网址或浏览器页面布局。

## 修复方案

启用 CONFIG_PID_NS，重新构建内核 Image 与模块。保留 ArkWeb 命名空间隔离，不采用关闭浏览器隔离的办法。

备份来自板端当前 boot_linux 分区（/dev/block/mmcblk1p5），长度 100663296 字节。新启动包在该备份副本上仅替换 /extlinux/Image，保留 extlinux.conf 和 toybrick.dtb，避免丢失 HDMI、SD 启动与已有硬件配置。新内核对应的四个 rtw89 WiFi 模块一同更新。

已备份：boot.original.img、modules.original.tar；板端对应备份在 /data/local/tmp/boot-browser-backup.img 与 browser-modules-original.tar。

构建脚本：build_kernel.py；打包并读回校验脚本：pack_boot.py；隔离能力探针：namespace-probe.c。

构建机源码配置：device/board/opc/opi5plus/kernel/configs/orangepi5plus_oh_defconfig 与当前内核构建目录内对应 defconfig，均保留 *.before_browser 备份。

## 原定验收项目

1. 重启后 CONFIG_PID_NS=y；namespace-probe 子进程中的 PID=1，成功退出。
2. ArkWeb 渲染进程启动成功，不再出现 fork errno22。
3. 本地测试网页显示；页面 JavaScript 按钮可更新文字。
4. HTTP/HTTPS 网页可加载，错误网址有错误提示。
5. 竖屏、鼠标与巡检应用回归正常。

当前文档不构成修复完成声明；以本文件后续实测更新为准。

## 实测更新
新内核已上板，CONFIG_PID_NS=y；使用原始 getpid 系统调用的命名空间探针返回子 PID=1、退出状态 0。ArkWeb 渲染子进程成功运行，本地 HTML、JavaScript 按钮更新 DOM、HTTP 页面均通过。截图 local.jpeg、http.jpeg，DOM 证据 js.json。已安装浏览器完整导航版本，保存在 browser-core-tested.hap。

地址栏随页面更新的后续修正版已编译签名为 D:\oh_app\dist\browser-repaired.hap，因电脑重新切回校园网，暂未安装该修正版，HTTPS 测试尚未完成。内核与 WiFi 更新已完成，竖屏截图仍正常。原 D:\oh_image\update.img 未重新打包。

## 最终验收结果

地址栏修正版已成功安装，HTTPS 百度页面显示成功，地址栏跟随页面跳转；后退回本地页、前进返回 HTTPS 均通过。原有竖屏截图完整，MMI 输入范围仍为 1080×1920，巡检应用总览启动回归通过。设备最终停留浏览器。

核心修复是启用内核 PID 命名空间并更新匹配的四个 WiFi 模块。未关闭浏览器进程隔离，未清空应用数据。新旧启动包、模块和最终 HAP 的校验清单见 manifest.json。此前网络断开导致的暂未安装记录为中间状态，本次已完成。原 update.img 仍未重新打包。
