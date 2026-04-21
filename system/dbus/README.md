# system/dbus

本目录保存 `boost-switch` 的 system bus policy 资产。

当前包含：

- `io.github.ge777777.BoostSwitch1.conf`

职责边界：

- D-Bus policy 只负责“谁可以拥有名字、谁可以把消息送到这个服务”
- 真正的可切换授权仍由 `boost-switchd` 内部的会话检查与 `polkit` 决定

安装脚本会把该文件安装到 `/usr/share/dbus-1/system.d/`，并在安装/卸载后请求 system bus 重新加载配置。
