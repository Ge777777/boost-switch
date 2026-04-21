# scripts/dev

本目录存放开发辅助脚本。

当前包含：

- `scan_public_sync_guard.py`：对候选公开工作树执行只读扫描，检查旧命名、个人邮箱、本机路径和不允许公开的私有路径前缀

该扫描脚本服务于双仓并行阶段的“私有优先、同步公开”流程；它不会自动修改文件，也不应默认触碰真实 `/sys/devices/system/cpu/cpufreq/boost`。
