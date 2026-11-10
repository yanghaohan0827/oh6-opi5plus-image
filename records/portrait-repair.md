# 整机竖屏修复与验收 · 2026-11-07

## 最终结果

整机使用 1080×1920 逻辑竖屏，HDMI 仍保持面板可用的 1920×1080@60 输出时序，由系统渲染层旋转铺满。用户已确认实体画面铺满；鼠标修复后，用户再次确认方向与四边活动范围均正常。截图也已恢复为完整、正向的 1080×1920，无半屏黑边。

最终应用截图：final-app.jpeg。设备最终停留巡检应用总览，网关场景 normal。

## 修复内容

1. vendor 默认方向：buildInDefaultOrientation=1；保持原 HDMI 时序和 DPI。
2. libdms：启动与后续方向变化时显式下发 RSDisplayNode::SetScreenRotation。
3. librender_service：非统一渲染路径原来直接遍历逻辑屏幕子节点，遗漏逻辑屏幕矩阵。现在 PrepareLogicalDisplayRenderNode 保存画布、合入逻辑屏幕矩阵、遍历后恢复，子窗口获得正确的合成矩阵和完整目标区域。
4. 截图：显示截图使用逻辑坐标，因此在捕获逻辑屏幕时合入显示矩阵的逆矩阵，消除已旋转表面在截图中的二次旋转和裁切。
5. libwms：为本机启用 persist.window.logical_pointer=true，向 MMI 提供 1080×1920 逻辑坐标与方向 0。显示层统一旋转输出。该开关默认 false，对其他未启用设备保留原行为。
6. 应用改为顶部导航，设备选择栏支持横向滚动，保留竖向内容宽度。

最初仅改方向配置导致半屏显示。试验禁用硬件合成无效，已恢复 persist.rosen.hardwarecomposer.enabled=true；screen correction 已恢复 0。最终不依赖这些试验选项。

## 验证

- 重启后 DisplayManager 报告逻辑尺寸 1080×1920。
- RenderService 图层 transformType=3（270°），目标矩形 1920×1080，源裁切 1080×1920。
- MMI 报告 width=1080、height=1920、direction=0、displayDirection=0。
- 鼠标命令测试能到约 (1074,1914) 和 (0,0)；最大值受平台指针边缘留白影响。
- 用户实际鼠标确认：方向和范围都正常。
- 系统重启与应用热安装后仍可使用；最终截图完整显示总览及底部导航栏。

## 源码与构建

构建机 OH-Build：

- foundation/window/window_manager/dmserver/src/abstract_screen_controller.cpp
- foundation/window/window_manager/wmserver/src/input_window_monitor.cpp
- foundation/graphic/graphic_2d/rosen/modules/render_service/core/pipeline/main_thread/rs_render_service_visitor.cpp
- foundation/graphic/graphic_2d/rosen/modules/render_service/core/feature/capture/rs_surface_capture_task.cpp
- vendor/opc/opi5plus/custom_conf/window/display_manager_config.xml
- vendor/opc/opi5plus/etc/para/hardware_opi5plus.para

产品源码的默认方向和逻辑鼠标开关也已同步。增量构建复用现有 ninja 的原编译、链接参数，只重编修改对象及相应共享库；脚本在本目录。链接包装脚本明确使用 python3。完整构建图中原有重复生成目标的问题没有在本次处理。

## 已部署与回退

当前 SD 系统已替换 libdms.z.so、librender_service.z.so、libwms.z.so；均先写临时文件，再同目录原子替换。原件分别保存在本目录的 *.original.z.so，以及板端 /data/local/tmp/*before-portrait.z.so。

方向原件：display_manager_config.original.xml。回退参考回退说明.md；完整回退还需恢复 libwms 原件并把 persist.window.logical_pointer 设为 false。

D:\oh_image\update.img 尚未重新打包，重新刷旧镜像会丢失这些系统补丁。当前修复已在运行中的 SD 系统及构建源码保存，未重烧整份镜像。
