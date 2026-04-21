# gnome-extension

本目录保存当前主线的 GNOME Shell 扩展实现，对外提供 Quick Settings 开关入口。

当前目录中的关键文件包括：

- `metadata.json`：扩展元数据与支持的 Shell 版本
- `src/extension.js`：Quick Settings 入口与扩展生命周期
- `src/prefs.js`：扩展偏好设置入口
- `schemas/org.gnome.shell.extensions.boost-switch.gschema.xml`：扩展设置 schema
- `tests/`：GJS 侧的状态、错误和 presenter 逻辑测试

相关验证：

- `glib-compile-schemas gnome-extension/schemas`
- `gjs -m gnome-extension/tests/test-state.js`
- `gjs -m gnome-extension/tests/test-errors.js`
- `gjs -m gnome-extension/tests/test-presenter.js`
