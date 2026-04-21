# 卸载说明

## 本机卸载

运行：

`sudo bash scripts/install/uninstall_local.sh --prefix /usr/lib/boost-switch`

卸载脚本会同时移除：

- `/etc/systemd/system/boost-switchd.service`
- `/usr/share/dbus-1/system-services/io.github.ge777777.BoostSwitch1.service`
- `/usr/share/dbus-1/system.d/io.github.ge777777.BoostSwitch1.conf`
- `/usr/share/polkit-1/actions/io.github.ge777777.boostswitch.policy`
- `/etc/polkit-1/rules.d/50-boost-switch-local.rules`
- `/usr/local/bin/boostctl`
- `/usr/local/bin/boost-switch-diag`
- 用户扩展目录下的 `boost-switch@ge777777.github.io`

如果你曾把当前用户加入 `boost-switch` 组，脚本不会自动移除该组成员关系，需要按本机策略自行清理。
