# boost-switch 架构概览

`boost-switch` 当前主线是一个面向 Ubuntu 24 + GNOME Shell 的本机 CPU Boost 切换项目。

公开仓库中的实现已经覆盖：

- GNOME Shell Quick Settings 前端入口
- `boostctl` 与诊断 CLI
- `system bus + polkit + systemd` 后端写入链路
- 安装、卸载、模拟验证与主机集成验证脚本

## 分层思路

当前实现按四层拆分：

1. `gnome-extension/`
   负责 GNOME Shell Quick Settings 前端入口与轻量状态展示。它不直接写 `/sys`，而是通过共享契约访问后端能力。

2. `shared/`、`tools/` 与 `src/boost_switch/contracts.py`
   负责前后端共用的接口约定、schema、示例载荷、CLI 入口和诊断输出，让扩展、CLI 与后端围绕同一套状态模型协作。

3. `src/boost_switch/`
   负责 Python 机制程序、授权判断、sysfs 访问抽象和 CLI 实现。

4. `system/` 与 `scripts/`
   负责安装资产和运行时集成，包括 D-Bus policy、systemd unit、polkit policy、本机安装脚本与验证脚本。

## 当前边界

- 已选择当前主线：`GNOME Shell 扩展 + Python 后端/CLI + system bus + polkit + systemd`
- `sudoers` 只保留为回退方向，不再作为主线路径
- `tray-app/` 仍保留为未来备选前端入口，但不属于当前主线
- 自动化测试默认只覆盖模拟验证，不直接写真实 `/sys/devices/system/cpu/cpufreq/boost`
- Quick Settings 的真实点击体验仍需要在主机 GNOME 会话中手工复验
