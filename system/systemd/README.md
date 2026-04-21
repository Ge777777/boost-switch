# system/systemd

本目录保存 `boost-switchd` 的 `systemd` 与 D-Bus 激活资产。

当前包含：

- `boost-switchd.service`
- `io.github.ge777777.BoostSwitch1.service`

安装脚本会把 unit 渲染到 `/etc/systemd/system/`，并把 system bus service 文件安装到 `/usr/share/dbus-1/system-services/`。

注意：

- `boost-switchd.service` 使用 `Type=simple`，只负责把 Python 机制程序拉起
- well-known bus name 仍由 Python 服务内部主动申请
- `io.github.ge777777.BoostSwitch1.service` 负责把 system bus 请求转给 `boost-switchd.service`
- 普通用户能否向 `io.github.ge777777.BoostSwitch1` 发送消息，还需要 `system/dbus/io.github.ge777777.BoostSwitch1.conf`
