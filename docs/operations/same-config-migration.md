# 同配置主机迁移部署方案

## 结论

当前项目可以在相同主机配置下完成功能迁移，但现阶段的迁移形态是“同版本源码 + 同安装参数 + 同主机前提下的重部署”，不是直接复制运行目录后立即无差异接管。

当前实现没有额外的持久化业务状态或独立配置数据库需要导出；迁移时真正需要冻结的是源码版本、安装参数、授权组策略，以及目标机是否满足相同的系统前提。

## 适用前提

- 源机与目标机都为 Ubuntu 24 主机
- 目标机具备与当前主线一致的 GNOME Shell、`systemd`、`polkit`、system bus 与 `login1` 运行环境
- 目标机存在 `/sys/devices/system/cpu/cpufreq/boost`
- 目标机可用 `/usr/bin/python3`、`python3-venv`、`gjs`、`glib-compile-schemas`、`systemctl`、`busctl`、`gnome-extensions`
- 目标机准备部署与源机相同的仓库提交版本

## 不在本方案覆盖范围

- 非 GNOME Shell 主机
- 不存在 `/sys/devices/system/cpu/cpufreq/boost` 的机器或内核
- 直接复制 `/usr/lib/boost-switch` 后跳过安装脚本的迁移方式
- 跨用户共享同一份扩展目录的部署方式

## 迁移前冻结项

在源机上先记录以下信息，避免目标机部署时出现“代码相同但参数不同”的偏差：

1. 冻结源码版本：
   `git rev-parse HEAD`
2. 记录实际安装命令：
   `sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch`
3. 记录是否启用了本地少弹窗规则：
   是否带了 `--enable-local-rule`
4. 记录是否把当前登录用户加入授权组：
   是否带了 `--add-current-user`
5. 记录当前会话用户是否已具备 `boost-switch` 组成员关系：
   `id`

## 源机健康确认

迁移前先确认源机本身闭环正常，避免把已有故障带到目标机：

- `boostctl status --json`
- `boost-switch-diag`
- `systemctl status boost-switchd.service --no-pager`
- `busctl --system tree io.github.ge777777.BoostSwitch1`
- `gnome-extensions info boost-switch@ge777777.github.io`

如果这里已经失败，优先修复源机，再做迁移。

## 目标机部署步骤

### 1. 准备相同源码版本

在目标机准备一份同仓库工作副本，并切换到与源机一致的提交号：

```bash
git fetch --all --tags
git checkout <source-commit>
```

这里的 `<source-commit>` 应替换为源机 `git rev-parse HEAD` 的结果。

### 2. 核对目标机前提

```bash
test -e /sys/devices/system/cpu/cpufreq/boost
command -v python3
python3 -m venv --help >/dev/null
command -v gjs
command -v glib-compile-schemas
command -v systemctl
command -v busctl
command -v gnome-extensions
```

任一关键项缺失，都不应继续执行正式迁移。

### 3. 使用与源机一致的安装参数部署

最小主线安装命令：

```bash
sudo bash scripts/install/install_local.sh --prefix /usr/lib/boost-switch
```

如果源机启用了少弹窗本地规则，则保持一致：

```bash
sudo bash scripts/install/install_local.sh \
  --prefix /usr/lib/boost-switch \
  --enable-local-rule
```

如果源机在安装时把当前登录用户加入授权组，则目标机也保持一致：

```bash
sudo bash scripts/install/install_local.sh \
  --prefix /usr/lib/boost-switch \
  --enable-local-rule \
  --add-current-user
```

安装脚本会自动完成以下动作：

- 在仓库内自举 `.tools/uv/`，并用它创建目标前缀下的运行时环境 `/usr/lib/boost-switch/venv`
- 安装 D-Bus policy、systemd unit、D-Bus service 与 polkit policy
- 安装 `boostctl` / `boost-switch-diag` wrapper
- 将 GNOME Shell 扩展复制到当前用户扩展目录并编译 schema
- 重启 `boost-switchd.service`

### 4. 刷新桌面会话

以下任一场景成立时，目标机都需要重新登录 GNOME 会话后再继续验证：

- 首次安装
- 更新了扩展目录
- 本次安装刚变更了 `boost-switch` 组成员关系

## 目标机验证步骤

### 1. 先跑不触碰真实 `/sys` 的验证

```bash
bash scripts/verify/verify_simulated.sh
```

### 2. 再跑主机集成验证

```bash
bash scripts/verify/verify_host_integration.sh
```

如需连带扩展可见性一起检查：

```bash
bash scripts/verify/verify_host_integration.sh --enable-extension
```

如需复验本地 rule 与真实 toggle：

```bash
bash scripts/verify/verify_host_integration.sh \
  --enable-extension \
  --verify-local-rule \
  --allow-real-toggle
```

### 3. 做前台 GNOME 手工复验

```bash
gnome-extensions info boost-switch@ge777777.github.io
gnome-extensions enable boost-switch@ge777777.github.io
```

然后在当前 GNOME 会话里手动点击 Quick Settings 开关，确认：

- 扩展入口可见
- 状态与 `boostctl status --json` 一致
- 若启用了本地 rule，是否仍出现额外 polkit 弹窗

## 失败回退步骤

如果目标机迁移失败，优先回退到干净状态，再重新部署：

```bash
sudo bash scripts/install/uninstall_local.sh --prefix /usr/lib/boost-switch
```

回退后重新执行正式安装，不要直接手工删除零散文件替代脚本卸载。

## 当前迁移边界说明

- 当前仓库支持的是“同构环境重部署”，还不是发布级安装包迁移
- `boost-switch@ge777777.github.io` 扩展安装在当前用户主目录下，目标机如果更换登录用户，需要按目标用户重新安装
- 即使源机和目标机配置相同，前台 Quick Settings 是否完全无额外弹窗，仍需在目标机活跃 GNOME 会话里手工复验
- 如果目标机缺少 `/sys/devices/system/cpu/cpufreq/boost`，这属于主机差异，不属于当前迁移方案可消除的问题
