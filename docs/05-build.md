# 05 · 构建与打包（供复现）

补丁二进制来自 OpenHarmony 6.0-Release `opi5plus` 的完整源码树。脚本里的路径是构建机上的 `/home/user/oh`，换机器时需要改 `root` / `ROOT_DIR` 等变量。

## 竖屏组件

修改了 5 处（源码副本在 [`patches/portrait/src/`](../patches/portrait/src/)）：

| 文件 | 修改 |
| --- | --- |
| `foundation/window/window_manager/dmserver/src/abstract_screen_controller.cpp` | 启动与方向变化时，在 `SetRotation` 之后显式调用 `RSDisplayNode::SetScreenRotation` |
| `foundation/graphic/graphic_2d/rosen/modules/render_service/core/pipeline/main_thread/rs_render_service_visitor.cpp` | `PrepareLogicalDisplayRenderNode` 合入逻辑屏幕矩阵后再遍历子节点，避免竖屏子窗口被横屏画布裁切 |
| `foundation/graphic/graphic_2d/rosen/modules/render_service/core/feature/capture/rs_surface_capture_task.cpp` | 逻辑屏幕截图时合入显示矩阵的逆矩阵，消除二次旋转与裁切 |
| `foundation/window/window_manager/wmserver/src/input_window_monitor.cpp` | 新增 `persist.window.logical_pointer` 开关；开启时向 MMI 报告逻辑 1080×1920、方向 0 |
| `vendor/opc/opi5plus/custom_conf/window/display_manager_config.xml` | `buildInDefaultOrientation` 由 `0` 改为 `1` |

构建方式（逐一执行）：

```sh
python3 patch_portrait.py     # libdms
python3 patch_render.py       # librender_service（visitor）
python3 patch_capture.py      # librender_service（capture）
python3 patch_input.py        # libwms
python3 build_component.py    # 只重编受影响对象，复用现有 ninja 参数
```

`patch_*.py` 会在源码旁留 `.before_portrait` 备份，并用 `assert` 确认待替换文本唯一；上游代码变化时会直接失败，不会静默改错。`build_component.py` 从现有 `libdms.ninja` 中抽取目标对象与 `solink` 规则，避免整树重编；同一思路也写在 `patch_render.py` / `patch_capture.py` / `patch_input.py` 里。

产物随后以“写 `.new` → `chmod 644` → `sync` → 同目录 `mv`”的方式替换到板上。

## 内核（CONFIG_PID_NS）

```sh
python3 build_kernel.py
```

脚本做三件事：

1. 打开 `CONFIG_PID_NS`，同时写入构建目录 `.config`、内核 `arch/arm64/configs/orangepi5plus_oh_defconfig` 与产品 `device/board/opc/opi5plus/kernel/configs/orangepi5plus_oh_defconfig`，三处都保留 `.before_browser` 备份；
2. 复用 OH 预编译的 clang/LLVM、GCC 与 pahole；
3. `make ARCH=arm64 ... Image modules -j6`。

打包启动分区：

```sh
python3 pack_boot.py
```

- 以板端启动分区备份（100,663,296 字节）为基底，用 `debugfs -w` 删除并重写 `/extlinux/Image`；
- **保留** `extlinux.conf` 与 `toybrick.dtb`，因此 HDMI、SD 启动与既有硬件配置不变；
- 写完后再 `dump` 回来比对 SHA-256，确认镜像与构建产物一致；
- 把 `rtw89_core / rtw89_pci / rtw89_8852b / rtw89_8852be` 打成 `modules.fixed.tar`。

内核为 Linux 6.6（OpenHarmony 6.0-Release），许可证 GPL-2.0。本仓库不附带完整内核源码；改动仅为上述配置开关，脚本与 defconfig 路径已给出。

## 关于整镜像重打包

2026-11-06 的 `update.img` 之后**没有重新打包**。要得到“刷完即带补丁”的镜像，需要在 Linux 上解包 RKFW、替换 `boot_linux` / `system` / `vendor` 分区后重打包，并重新做上板验收。该流程本项目没有实际走通，因此不提供未经验证的命令。当前经过验证的路径是：刷基础镜像 → 应用补丁 → 重启验收。
