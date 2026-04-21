# Ubuntu 24 安装说明

## 本机安装

1. 确认主机具备 `/usr/bin/python3`、`python3-venv`、`gjs`、`glib-compile-schemas`、`systemctl` 和 `polkit` 运行环境；安装脚本现在会自举项目级工具环境，不再依赖用户级 `uv`。
2. 执行：
   `sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch`
3. 如果明确接受更宽松的本机授权边界，并希望日常切换尽量少弹窗，可追加：
   `--enable-local-rule`
   该选项会安装本地 polkit rule，对本地活跃且属于 `boost-switch` 组的用户直接放行切换请求，更适合受信任的单机使用场景，不应视为默认推荐配置。
4. 如果希望把当前登录用户加入授权组，可追加：
   `--add-current-user`
5. 安装脚本会同时：
   - 在仓库内自举 `.tools/uv/`，并统一使用 `.tools/uv/bin/uv`
   - 用这份 repo-local `uv` 创建目标运行时 `/usr/lib/boost-switch/venv`
   - 安装 `io.github.ge777777.BoostSwitch1.conf` 到 `/usr/share/dbus-1/system.d/`
   - 安装 `boostctl` 与 `boost-switch-diag` 到 `/usr/local/bin/`
   - 在用户扩展目录编译 `glib-compile-schemas`
   - 把 `.tools/uv/` 和扩展目录归属修正为当前用户
   - 重启 `boost-switchd.service`，确保重装后立即切到最新代码
6. 如果这是首次安装、刚刚更新扩展目录，或者本次安装刚刚变更了组成员，请重新登录 GNOME 会话。

`.tools/uv/` 只是仓库内的安装工具环境，可删除、可重建，不作为服务运行环境。真正供服务和 CLI 使用的仍然是 `/usr/lib/boost-switch/venv`。

## 安装完成后可直接使用的命令

- `boostctl status --json`
- `boostctl set on`
- `boostctl set off`
- `boost-switch-diag`

## 自动化验证

- `bash scripts/verify/verify_simulated.sh`

## 主机集成验证

- `bash scripts/verify/verify_host_integration.sh`
- `bash scripts/verify/verify_host_integration.sh --enable-extension`
- 若要显式执行真实 boost 切换，再运行：
  `bash scripts/verify/verify_host_integration.sh --allow-real-toggle`
- 若已安装本地 rule 且希望为前台 GNOME 会话复验准备前置检查，再运行：
  `bash scripts/verify/verify_host_integration.sh --enable-extension --verify-local-rule --allow-real-toggle`
  这一步只会验证 service / D-Bus / CLI 授权链路，以及扩展可见性与 local rule 前置条件；它不会代替前台 Quick Settings 点击本身。

## 前台 GNOME 会话手工复验

1. 先运行 `gnome-extensions info boost-switch@ge777777.github.io`，确认扩展已被 GNOME Shell 识别。
   如果这是首次安装或刚更新过扩展目录，而这里仍提示扩展不存在，优先重新登录 GNOME 会话再试；GNOME 46 不保证对新写入的用户扩展做当前会话热发现。
2. 需要时运行 `gnome-extensions enable boost-switch@ge777777.github.io`，把扩展启用到当前会话。
3. 如果安装时使用了 `--enable-local-rule`，并且当前用户已经具备 `boost-switch` 授权组成员关系，则运行：
   `bash scripts/verify/verify_host_integration.sh --enable-extension --verify-local-rule --allow-real-toggle`
4. 上一步只是在进入前台交互前，确认扩展已可见、local rule 已可确认、并且 `boostctl` 的后端授权链路可用。
5. 然后在当前 GNOME 会话里手动点击 Quick Settings 开关，确认是否仍弹出额外的 polkit 授权框。只有这一步才真正覆盖前台交互路径。

## 相关脚本

- `scripts/install/install_local.sh`
- `scripts/verify/verify_simulated.sh`
- `scripts/verify/verify_host_integration.sh`

## 同配置主机迁移

如果目标机与当前主线环境一致，需要把现有功能迁移到另一台同类 Ubuntu 24 主机，请直接参考 [同配置主机迁移部署方案](same-config-migration.md)。
