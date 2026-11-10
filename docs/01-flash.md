# 01 · 刷入基础镜像

## 前置条件

- 硬件：Orange Pi 5 Plus（RK3588），SD 卡容量 ≥ 8 GB
- 镜像：`update.img`，3,552,299,594 字节（3.55 GB）
- Windows 刷写工具：Rockchip `SDDiskTool`（SD 卡启动）或 `RKDevTool`（USB 升级）
- 刷写会清空 SD 卡，请先备份卡内数据

## 第一步：合并分卷

GitHub Release 单个文件上限 2 GB，镜像被拆成两个分卷：

- `oh6-opi5plus-20261106.img.part1`（1,992,294,400 字节）
- `oh6-opi5plus-20261106.img.part2`（1,560,005,194 字节）

Windows（PowerShell，在仓库根目录）：

```powershell
.\scripts\join-parts.ps1
```

Linux / macOS：

```sh
./scripts/join-parts.sh
```

合并后必须匹配：

```
大小   : 3552299594 字节
SHA-256: 8994286e12c2b8a05aafd9479026fffafc34112ff47ddc199fe0cf5725f38d34
```

不匹配就不要刷，重新下载。

## 第二步：写入 SD 卡（推荐的 SD 启动方式）

1. 以管理员身份打开 `SDDiskTool`。
2. 固件选择合并后的 `update.img`。
3. 磁盘选择 SD 卡对应盘符。**再次确认盘符**，不要选成移动硬盘或 U 盘。
4. 点击“开始创建”，等待写入与校验完成。
5. 安全弹出 SD 卡，插入板卡，接 HDMI、USB 鼠标与电源。

`SDDiskTool` 是 Rockchip 官方工具，本仓库不分发，请从其官方渠道获取。

## 可选：USB 升级

`update.img` 是 RKFW 格式固件包，文件头为 `RKFW`，也可以用 Rockchip 的 USB 升级方式写入：

- Windows：`RKDevTool` → 升级固件 → 选择 `update.img` → 升级
- Linux：`upgrade_tool uf update.img`

进入 Loader / MaskROM 模式的按键与时序随载板不同，请以 Orange Pi 官方文档为准。

## 第一次启动

- 基础镜像默认是 **横屏 1920×1080**，尚未包含竖屏补丁。
- 串口控制台可用；`hdc` 通过 USB 连接：

```sh
hdc list targets
hdc shell
```

- 如果需要 TCP 连接（开发机与板卡同网段）：

```sh
hdc shell "param set persist.hdc.mode tcp"
hdc shell "param set persist.hdc.port 8710"
# 重启后生效，然后：
hdc tconn <板卡IP>:8710
```

- 首次开机需要初始化，耐心等待桌面出现。
- 确认系统能正常启动、`hdc` 能进入 shell 之后，再应用补丁。

下一步：[02 · 应用系统补丁](02-apply-patches.md)
