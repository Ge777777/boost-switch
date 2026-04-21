# boost-switch

[English](README.md) | 简体中文

`boost-switch` 是一个面向 Ubuntu 24 本机部署场景的 CPU Boost 切换项目，桌面主入口是 GNOME Shell Quick Settings，真正写入 `/sys` 的只有 system-bus 特权服务。

## 当前状态

当前仓库已经具备本机安装、CLI 检查和主机集成验证链路，但仍属于演进中的主线实现，还不是稳定发布版。

- GNOME Shell Quick Settings 扩展作为主要桌面入口
- `system bus + polkit + systemd` 作为默认提权后端
- `boostctl` 与诊断 CLI 作为验证和排障入口
- 安装时会自举仓库级 `.tools/uv/`，实际运行时仍使用 `/usr/lib/boost-switch/venv`

> 提示：本项目会直接影响主机上的 CPU Boost 行为，请先阅读相关文档，并自行承担风险。

## 适用范围

- Ubuntu 24 且使用 GNOME Shell 的主机
- 存在 `/sys/devices/system/cpu/cpufreq/boost` 的机器

当前不覆盖：

- 非 GNOME 桌面环境
- 不存在 `/sys/devices/system/cpu/cpufreq/boost` 的机器
- 跳过安装脚本、直接复制现有运行目录的迁移方式

## 快速开始

先确认主机具备 `/usr/bin/python3`、`python3-venv`、`gjs`、`glib-compile-schemas`、`systemctl` 和 `polkit`。安装流程会自动自举仓库内 `.tools/uv/`，因此不要求预先安装用户级 `uv`。

使用主线默认安装命令：

```bash
sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch
```

常用安装选项：

```bash
sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch --enable-local-rule
sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch --enable-local-rule --add-current-user
```

`--enable-local-rule` 是显式启用的本机便利模式，不是默认安全基线。它会安装一条本地 polkit rule，对本地活跃且属于 `boost-switch` 组的用户直接放行 boost 切换，因此只适合受信任的单机使用场景。

如果这是首次安装、刚更新过扩展目录，或安装过程中刚变更了组成员关系，请先重新登录 GNOME 会话，再做前台复验。

完整安装流程以及 `.tools/uv/` 自举细节见 [docs/operations/ubuntu-24-install.md](docs/operations/ubuntu-24-install.md)。

## 验证安装

先验证后端与 CLI 链路：

```bash
boostctl status --json
bash scripts/verify/verify_simulated.sh
bash scripts/verify/verify_host_integration.sh
```

持续集成只覆盖上面的模拟验证链路，不能替代真实主机上的 GNOME 会话复验。

## 前台 GNOME 手工复验

后端验证通过，并不等于 Quick Settings 点击路径已经完成验证。要确认前台路径，请先确认扩展已被 GNOME Shell 识别，再在当前 GNOME 会话里手动点击 Quick Settings 开关。

```bash
gnome-extensions info boost-switch@ge777777.github.io
```

## 延伸文档

英文 README 负责对外概览与关键入口说明；当前更细的运维文档以及部分 GNOME UI 字符串仍以中文为主。

- [Ubuntu 24 安装说明](docs/operations/ubuntu-24-install.md)
- [卸载说明](docs/operations/uninstall.md)
- [故障排查](docs/operations/troubleshooting.md)
- [同配置主机迁移部署方案](docs/operations/same-config-migration.md)

## 协作入口

- [贡献说明](CONTRIBUTING.md)
- [社区行为准则](CODE_OF_CONDUCT.md)
- [安全策略](SECURITY.md)

## 架构摘要

当前主线架构是：GNOME Shell Quick Settings 作为用户入口，system-bus 特权服务负责实际写入，`polkit + systemd` 提供安装与运行时权限层。`sudoers` 只保留为回退方向，不再作为主线路径。

## 仓库布局

- `docs/`：公开架构与运维文档
- `scripts/`：安装、验证和开发辅助脚本
- `system/`：D-Bus、polkit、systemd 等权限集成资产
- `shared/`：共享契约、schema 与示例载荷
- `src/`：Python 服务端与 CLI 实现
- `gnome-extension/`：GNOME Shell 扩展源码与 schema
- `tools/`：CLI 与诊断入口的说明文档

## 许可证

本项目使用 [MIT License](LICENSE)。
