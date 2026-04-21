# system/polkit

本目录保存 `boost-switch` 的主线 `polkit` 资产。

当前包含：

- 分发默认 `.policy` 文件
- 本机少弹窗模式的本地规则模板

约束：

- `.policy` 可进入分发默认安装路径
- `.rules.template` 只能在本机显式安装时渲染到 `/etc/polkit-1/rules.d/`
- `.rules.template` 的效果是：对本地活跃且属于 `boost-switch` 组的用户直接放行 `io.github.ge777777.boostswitch.set`，因此它属于本机便利选项，不是默认分发安全基线
- system bus 可达性不由 `polkit` 负责，D-Bus 名字拥有和发送权限由 `system/dbus/` 资产负责
