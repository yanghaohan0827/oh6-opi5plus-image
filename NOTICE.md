# 第三方组件与许可说明

本仓库包含三类内容，许可是分开的：

1. **自有脚本、文档、适配改动**（`scripts/`、`docs/`、`records/`、`patches/` 下的补丁脚本与修改）：
   Apache License 2.0，见 [LICENSE](LICENSE)。

2. **镜像与二进制中的 OpenHarmony 6.0-Release 组件**：
   Apache License 2.0，版权归 OpenHarmony 项目及其贡献者。

3. **Linux 内核（linux-6.6）**：
   GPL-2.0。本仓库分发的是编译产物与构建脚本，不包含完整内核源码；唯一的功能性改动是启用 `CONFIG_PID_NS`，相关脚本与 defconfig 路径见 [docs/05-build.md](docs/05-build.md)。内核源码可从 OpenHarmony 6.0-Release 官方仓库获取。

镜像中还包含 Rockchip / Orange Pi 提供的固件、GPU 驱动、Wi-Fi 固件与其他厂商二进制。这些组件归各自权利人所有，按原始许可随镜像分发；本仓库不对其授予任何额外权利。

本仓库不是 OpenHarmony、Rockchip 或 Orange Pi 的官方发布。
