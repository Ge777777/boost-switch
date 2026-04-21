# tools/boostctl

本目录对应控制台入口 `boostctl`。

当前主命令包括：

- `boostctl status --json`
- `boostctl set on`
- `boostctl set off`
- `boostctl watch`

运行时通过 system bus 访问 `io.github.ge777777.BoostSwitch1`，不直接写 `/sys`。
