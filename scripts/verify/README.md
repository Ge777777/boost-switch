# scripts/verify

本目录保存验证脚本。当前包括：

- `verify_simulated.sh`
  运行默认不触碰真实 `/sys` 的自动化验证
- `verify_host_integration.sh`
  运行显式主机集成验证；只有传 `--allow-real-toggle` 才会写真实 boost
