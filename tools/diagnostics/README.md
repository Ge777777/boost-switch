# tools/diagnostics

本目录对应诊断入口 `boost-switch-diag`。

默认输出至少包含以下字段：

- 当前用户与 UID
- 是否属于 `boost-switch` 组
- 当前会话是否为 local active
- 服务与 D-Bus 名称是否可见
- `boost` sysfs 路径是否可读
