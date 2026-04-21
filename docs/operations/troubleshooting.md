# 故障排查

## 切换时仍然弹授权框

- 检查是否安装了 `/etc/polkit-1/rules.d/50-boost-switch-local.rules`
- 检查当前用户是否属于 `boost-switch` 组
- 变更组成员后重新登录 GNOME 会话

## 扩展显示与 CLI 不一致

- 先运行 `boostctl status --json`
- 再运行 `boost-switch-diag`
- 再运行 `bash scripts/verify/verify_host_integration.sh`
- 检查 `boost-switchd.service` 和 `io.github.ge777777.BoostSwitch1` 是否存在

## 服务不可达

- `systemctl status boost-switchd.service --no-pager`
- `busctl --system tree io.github.ge777777.BoostSwitch1`
- 确认 `/usr/share/dbus-1/system.d/io.github.ge777777.BoostSwitch1.conf` 已安装
- 如最近刚更新了 unit，先执行 `sudo systemctl daemon-reload`
- 如最近刚更新了 D-Bus policy，先重新执行安装脚本或显式重载 system bus 配置

## `boostctl` 命令不存在

- 确认 `/usr/local/bin/boostctl` 已存在
- 重新运行本机安装脚本，确认 wrapper 已被安装

## 扩展没有被 `gnome-extensions` 识别

- 确认 `~/.local/share/gnome-shell/extensions/boost-switch@ge777777.github.io` 存在
- 确认目录顶层存在 `extension.js`、`prefs.js` 与 `metadata.json`
- 确认该目录归属为当前用户，而不是 `root:root`
- 确认目录下已经有最新的 `schemas/gschemas.compiled`
- 如果这是首次安装或刚更新过该扩展目录，重新登录 GNOME 会话后再运行 `gnome-extensions info boost-switch@ge777777.github.io`
- 再运行 `gnome-extensions info boost-switch@ge777777.github.io`

## `boostctl` 提示 `PID <...> does not belong to any known session`

- 旧实现会把 `login1.GetSessionByPID` 当成所有调用的硬前提，VS Code 集成终端这类 `user.slice` 进程会被误判
- 当前实现会先回退到 `GetUserByPID -> User.Display / Sessions`，再解析该用户的活跃本地图形会话
- 写操作不会再因为这类 session 解析失败被服务端提前拒绝，最终授权交给 `pkcheck --system-bus-name`
- 如果重新安装后仍看到这个错误，优先确认实际运行中的 `boost-switchd` 是否已经更新到最新安装版本

## 本地 rule 已安装但前台切换仍然弹窗

- 确认 `/etc/polkit-1/rules.d/50-boost-switch-local.rules` 存在
- 确认安装时曾使用 `--enable-local-rule`
- 确认当前登录用户已属于 `boost-switch` 组
- 如组成员关系是本次安装刚变更的，重新登录 GNOME 会话后再试
- 运行 `bash scripts/verify/verify_host_integration.sh --enable-extension --verify-local-rule --allow-real-toggle`
- 上面的脚本只确认后端授权链路和前台复验前置条件；随后仍需在当前 GNOME 会话里手动点击 Quick Settings 开关，确认是否继续弹框

## 本地 rule 无法被非交互确认

- `verify_host_integration.sh --verify-local-rule` 由普通用户运行时，可能因为 `/etc/polkit-1/rules.d` 不可遍历且 `sudo -n` 也无法确认文件存在
- 这类场景下脚本会直接失败收口，而不是继续假装通过
- 这类场景先运行 `sudo ls -l /etc/polkit-1/rules.d/50-boost-switch-local.rules`
- 如果文件存在，再检查当前登录会话是否已经刷新 `boost-switch` 组成员关系
- 之后重新运行 host 验证脚本，并在真实前台 GNOME 会话里手动点击 Quick Settings 开关完成最终复验

## sysfs 不存在

- 确认宿主机存在 `/sys/devices/system/cpu/cpufreq/boost`
- 如果路径不存在，这更像是机器或内核差异，而不是纯权限问题
