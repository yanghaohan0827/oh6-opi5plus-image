# v1.0.0-base · 2026-11-11

OpenHarmony 6.0-Release（RK3588 / Orange Pi 5 Plus）基础镜像 + 2026-11-07 实机验证的竖屏与 ArkWeb 补丁。

## 资产

| 文件 | 字节 |
| --- | ---: |
| `oh6-opi5plus-20261106.img.part1` | 1,992,294,400 |
| `oh6-opi5plus-20261106.img.part2` | 1,560,005,194 |
| `boot.fixed.img` | 100,663,296 |
| `boot.original.img` | 100,663,296 |
| `modules.fixed.tar` | 1,105,920 |
| `modules.original.tar` | 1,094,144 |

合并后的 `update.img`：3,552,299,594 字节，SHA-256 `8994286e12c2b8a05aafd9479026fffafc34112ff47ddc199fe0cf5725f38d34`。

## 说明

- 镜像本体打包于 2026-11-06，**不含** 2026-11-07 的竖屏与 ArkWeb 修复；修复以补丁形式提供。
- 已验证：1080×1920 竖屏、鼠标方向与范围、`CONFIG_PID_NS=y`、命名空间子进程 PID=1、ArkWeb 本地/HTTP/HTTPS 页面、重启后补丁仍生效。
- 未验证：整镜像重打包、换内核后的 Wi-Fi 单独联网复测、触摸、其他载板。
- 完整步骤见 README 与 `docs/`。

## English

OpenHarmony 6.0-Release base image for RK3588 / Orange Pi 5 Plus, plus the portrait-orientation and ArkWeb (CONFIG_PID_NS) patches verified on hardware on 2026-11-07.

- The image itself was built on 2026-11-06 and does **not** contain the two patches; apply them after flashing.
- Join the two image parts and verify SHA-256 `8994286e12c2b8a05aafd9479026fffafc34112ff47ddc199fe0cf5725f38d34` (3,552,299,594 bytes).
- Verified: 1080×1920 portrait, mouse range, `CONFIG_PID_NS=y`, namespace child PID=1, ArkWeb local/HTTP/HTTPS pages, patches survive reboot.
- Not verified: full-image repack, separate Wi-Fi retest after the kernel swap, touch input, other boards.
- See [README.en.md](README.en.md) and `docs/` for details.
