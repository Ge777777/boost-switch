# boost-switch 两组方案技术路线与可行性分析

> 说明：本文保留“两组候选方案”的比较价值，但截至 `2026-04-20`，仓库主线已经改为 `GNOME Shell 扩展 + system bus + polkit`。当前公开实现边界以 `README.md` 与 `docs/architecture/overview.md` 为准。

## 1. 文档目的

本文档基于当前仓库已经确定的项目边界，对 `boost-switch` 的两组候选方案做工程化分析：

1. 桌面入口方案：
   - `Python 托盘应用`
   - `GNOME Shell 扩展`
2. 权限后端方案：
   - `sudoers` 受限命令
   - `polkit`

文档目标不是现在就拍板所有实现细节，而是回答下面几个更实际的问题：

- 这四个方向分别要怎么落地，才能适配本仓库当前结构？
- 哪些方案适合作为首发实现，哪些更适合作为后续增强？
- 从 Ubuntu 24 + GNOME 46 + 本机 CPU Boost 开关这个具体场景看，哪条路线的工程风险最低？

## 2. 当前边界与前提

### 2.1 仓库当前已知约束

从仓库现有文档和当前设计决策可以确认以下前提：

- 项目目标是为 Ubuntu 24 桌面环境提供 CPU Boost 快速切换工作流。
- 仓库已经预留 `tray-app/`、`gnome-extension/`、`shared/`、`tools/`、`system/` 等目录。
- 当前架构说明已经将仓库定位为 `GNOME Shell 扩展为主入口、Python 承担后端与 CLI` 的混合仓库。
- 当前主线权限后端已调整为 `polkit + systemd + system bus`，`sudoers` 保留为回退方案。
- 自动化测试默认不得写真实 `/sys/devices/system/cpu/cpufreq/boost`。

### 2.2 本机环境核对

本次分析同时参考了当前机器上的实际工具版本，以避免把路线讨论写成脱离环境的空方案：

- `gnome-shell --version`：`GNOME Shell 46.0`
- `python3 --version`：`Python 3.12.3`
- `sudo -V | head -n 1`：`Sudo version 1.9.15p5`
- `pkexec --version`：`pkexec version 124`

因此，本文默认目标环境不是“任意 Linux 桌面”，而是：

- Ubuntu 24 主机
- GNOME 46 会话
- 本机个人桌面使用场景
- 控制对象仅限 CPU Boost 状态，不扩展到完整性能调优面板

## 3. 评估维度

本次比较使用以下维度：

| 维度 | 关注点 |
| --- | --- |
| 与目标桌面的贴合度 | 是否符合 Ubuntu 24 / GNOME 46 的主要交互方式 |
| 实现复杂度 | 需要新增多少模块、运行时依赖和安装资产 |
| 权限边界清晰度 | 能否把“非特权 UI”和“特权写入”切干净 |
| 可测试性 | 是否容易做模拟测试、回归测试和主机集成验证 |
| 维护成本 | GNOME 版本漂移、依赖升级、调试难度是否可控 |
| 用户体验 | 开关入口是否足够快，错误提示和授权流程是否顺手 |
| 扩展空间 | 后续是否容易增加状态同步、诊断、日志与更多策略 |

## 4. 方案组一：桌面入口方案

### 4.1 方案 A：Python 托盘应用

#### 技术路线

`Python 托盘应用` 更适合做成一个“轻 UI + 外部命令编排器”的结构，核心不是直接在 UI 里写提权逻辑，而是让 UI 成为后端命令的消费者。

建议技术路线如下：

1. 在 `shared/` 中定义前后端共享状态模型。
   - 例如：`boost_supported`、`boost_enabled`、`backend`、`last_error`、`can_toggle`、`source`
   - 同时约定 JSON 输出和错误码语义，供托盘、扩展、CLI 复用
2. 在 `tools/boostctl/` 中实现统一控制入口。
   - 提供 `status --json`
   - 提供 `set on|off`
   - 提供 `diagnose --json`
   - UI 不直接写 `/sys`，只调用 `boostctl`
3. 在 `tray-app/` 中实现 Python 前端。
   - 推荐使用 `PyGObject + GTK4/Libadwaita` 作为窗口与设置页基础
   - 常驻逻辑负责状态轮询、菜单动作、错误提示和用户通知
   - 如需要托盘图标/顶栏常驻，可通过主机可用的状态图标路径接入，但这部分应被视为目标环境相关实现
4. 将授权与系统写入完全下沉到后端。
   - 托盘只负责显示状态和触发命令
   - 实际提权路径通过 `sudoers` 或 `polkit` 后端实现
5. 安装侧补充用户级集成。
   - 自启动 `.desktop`
   - 图标、桌面文件、日志路径、诊断入口

#### 推荐模块边界

| 模块 | 职责 |
| --- | --- |
| `shared/contracts` | 状态字段、命令返回结构、错误码约定 |
| `tools/boostctl` | 对外统一 CLI，屏蔽具体提权实现 |
| `tools/diagnostics` | 环境检查、权限检查、回退建议 |
| `tray-app` | 菜单、通知、轮询、状态展示、调用 CLI |
| `system/*` | 实际提权资产与系统集成文件 |

#### 验证路径

- 单元测试：用模拟 sysfs 路径和模拟 CLI 输出验证状态解析
- 组件测试：验证托盘前端能正确处理 `status`、`set`、`diagnose` 三类返回
- 集成测试：显式区分“模拟验证”和“真实主机 boost 切换验证”
- 回归重点：权限失败、状态刷新延迟、开机自启、异常提示

#### 主要优点

- 与仓库当前 `Python 为主的混合仓库` 定位一致，技术栈收敛。
- 前端逻辑与 CLI/诊断工具共享 Python 生态，开发和调试效率更高。
- UI 层不直接嵌入 GNOME Shell 内部逻辑，失败时通常不会影响整个桌面外壳。
- 未来如果要兼容非 GNOME 桌面，迁移成本低于 Shell 扩展。

#### 主要缺点

- “托盘”在 GNOME 语境里不是最原生的入口形态，体验依赖目标桌面会话对该类入口的支持情况。
- 如果最终交互依赖状态图标，跨桌面兼容性和视觉一致性会弱于 Quick Settings。
- 授权弹窗、状态刷新、常驻进程生命周期都需要自行编排，UI 细节工作量并不低。

#### 风险与控制

| 风险 | 说明 | 控制方式 |
| --- | --- | --- |
| 入口样式依赖目标桌面 | 托盘/状态图标并非所有桌面都一致支持 | 将目标环境明确收窄为 Ubuntu 24 主机，不承诺跨桌面一致性 |
| 常驻进程状态漂移 | 前端缓存状态可能落后于真实 sysfs | 强制以 `boostctl status --json` 为真值源，必要时缩短轮询 |
| 后端错误被 UI 吞掉 | 用户只看到按钮没变化 | 统一错误码与用户可读错误消息，前端直接展示 |

#### 可行性结论

从当前仓库的既定方向看，`Python 托盘应用` 的工程可行性为 `高`。

它最大的优势不是“UI 最原生”，而是：

- 与仓库已选技术栈一致
- 最容易先把 CLI、诊断、提权封装做扎实
- 对后续增加 GNOME 扩展不会形成阻碍

如果目标是“先做出稳定可用的第一版”，它更适合作为首发前端。

### 4.2 方案 B：GNOME Shell 扩展

#### 技术路线

`GNOME Shell 扩展` 更适合做成一个“原生 Quick Settings 开关 + 极薄状态桥接层”的结构。它的价值在于入口原生，不在于承担复杂业务。

建议技术路线如下：

1. 以 Quick Settings 为主入口实现扩展。
   - 提供开关状态
   - 提供简短副标题或错误摘要
   - 提供“打开设置”或“运行诊断”入口
2. 扩展只维护 UI 和轻量状态同步，不直接承载复杂提权逻辑。
   - 读取状态：调用 `boostctl status --json` 或访问受控 D-Bus 接口
   - 切换状态：调用统一后端入口
3. 在 `gnome-extension/` 中拆分以下部分：
   - `extension.js`：入口与生命周期
   - `prefs.js`：偏好设置
   - `schemas/`：扩展配置
   - `lib/`：命令调用、状态解析、错误映射
4. 将“复杂诊断”和“高级配置”留给外部窗口或 CLI。
   - Quick Settings 只做切换与简要反馈
   - 避免把过多业务堆进 Shell 进程
5. 保留版本适配层。
   - 当前主目标是 GNOME 46
   - 后续 Shell 升级时通过单独适配文件或版本说明处理

#### 验证路径

- 静态验证：扩展元数据、schema、资源文件完整性
- 主机验证：`gnome-extensions` 安装/启用/禁用流程
- 功能验证：开关、错误提示、禁用恢复、Shell 重载后的状态恢复
- 升级验证：GNOME Shell 小版本升级后的最小回归检查

#### 主要优点

- 与 GNOME 46 的 `Quick Settings` 交互模式高度贴合，入口最顺手。
- 用户无需单独寻找托盘图标或额外窗口，操作链路最短。
- 对“单个开关 + 少量状态展示”这种功能形态非常合适。

#### 主要缺点

- 扩展运行在 GNOME Shell 进程相关语境中，出错时影响面比普通应用更大。
- GNOME 扩展天然比普通 GTK 应用更容易受到 Shell 升级影响。
- 调试、打包、版本适配和现场排障难度通常高于 Python 独立应用。

#### 风险与控制

| 风险 | 说明 | 控制方式 |
| --- | --- | --- |
| GNOME 版本漂移 | 扩展代码容易受 Shell 内部变化影响 | 严格限定首发支持版本为 GNOME 46，并建立版本回归检查 |
| 扩展异常影响桌面体验 | UI 卡死、开关失效、错误消息不直观 | 业务逻辑外移到 `boostctl`/后端，扩展只做薄 UI |
| 调试门槛高 | Shell 扩展问题通常比普通应用更难定位 | 提前准备日志入口、诊断命令和最小化实现 |

#### 可行性结论

在“只服务 Ubuntu 24 + GNOME 46”这个收窄目标下，`GNOME Shell 扩展` 的产品贴合度为 `高`，工程可行性为 `中高`。

它的问题不在于做不出来，而在于：

- 首版实现时，调试成本和版本维护成本都高于 Python 托盘应用
- 如果后端接口还不稳定，直接上扩展会把 UI 和底层联调成本叠在一起

因此它更适合作为：

- 第二阶段前端
- 或者在后端接口稳定后，再切换为主入口

### 4.3 桌面入口方案对比

| 项目 | Python 托盘应用 | GNOME Shell 扩展 |
| --- | --- | --- |
| 与仓库现方向一致性 | 高 | 中 |
| 与 GNOME 46 原生交互贴合度 | 中 | 高 |
| 首发实现难度 | 中 | 中高 |
| 调试与回归成本 | 低到中 | 中到高 |
| 跨桌面延展性 | 高 | 低 |
| 作为第二前端复用后端 | 高 | 高 |

#### 入口层推荐结论

如果只问“哪个更原生”，答案仍然是 `GNOME Shell 扩展`。

如果问“当前仓库已经拍板的主线是什么”，答案也已经变成 `GNOME Shell 扩展`。

新的实施顺序是：

1. 先定义统一 D-Bus / 状态契约
2. 先落 `polkit + systemd + system bus` 后端与 `boostctl`
3. 再落 GNOME Shell 扩展作为主入口
4. 如有需要，再补 Python 托盘作为备选入口

## 5. 方案组二：权限后端方案

### 5.1 方案 A：`sudoers` 受限命令

#### 技术路线

`sudoers` 方案最适合采用“极小特权 helper + 非特权 CLI 包装”的结构，而不是让前端直接以 `sudo` 任意运行脚本。

建议技术路线如下：

1. 提供一个职责极窄的 helper。
   - 建议安装到固定绝对路径，例如 `/usr/libexec/boost-switch-helper`
   - 仅支持极少数子命令，例如 `get`、`set on`、`set off`
   - 参数严格校验，不接受自由拼接的任意命令
2. 在 `system/sudoers/` 中提供精确的 `sudoers.d` 模板。
   - 只放行 helper 的固定路径和固定参数模式
   - 不使用 `ALL`
   - 不依赖“允许大范围命令后再用 `!` 排除”的写法
3. 在 `tools/boostctl/` 中封装外部调用。
   - UI 层只调用 `boostctl`
   - `boostctl` 决定何时走 `sudo`
4. 把真实 sysfs 写入限制在 helper 内部。
   - 读取、写入、异常处理、日志全部在 helper 里完成
   - 普通前端不持有直接写系统路径的逻辑
5. 测试时使用模拟路径。
   - helper 支持测试模式或环境变量注入模拟 sysfs 根路径
   - 默认测试不得触碰真实 `/sys`

#### 优点

- 边界清晰，容易把特权能力压缩到最小。
- 对本项目这种“只有少数固定动作”的场景非常合适。
- 安装、排错、诊断路径相对直观。
- 作为 MVP 后端，开发速度最快。

#### 缺点

- 桌面用户体验不如更深度的桌面授权机制自然。
- 如果规则写得过宽，安全收益会迅速下降。
- 需要仔细处理密码提示、日志、执行路径与错误返回。

#### 关键安全注意点

这个方案的安全性不来自 `sudo` 这三个字，而来自“helper 是否足够窄”。

需要明确避免以下做法：

- 允许任意脚本、shell、编辑器或通用解释器提权执行
- 依赖 `ALL, !cmd` 这类表面收紧、实际容易绕过的策略
- 让前端把未经约束的用户输入直接透传给特权命令

正确姿势是：

- 固定 helper 绝对路径
- 固定子命令集合
- 固定参数枚举
- helper 内部再次做白名单校验

#### 风险与控制

| 风险 | 说明 | 控制方式 |
| --- | --- | --- |
| `sudoers` 规则过宽 | 看似方便，实际等同扩大 root 能力面 | 只允许固定 helper，不允许通用解释器 |
| UI 直接拼接命令行 | 会把输入校验责任错误地下放到前端 | 所有写入都走 `boostctl -> helper` 固定协议 |
| 测试误写真实 sysfs | 容易伤及主机 | 测试必须使用模拟路径，真实写入只作为显式集成验证 |

#### 可行性结论

在本项目当前阶段，`sudoers` 受限命令的工程可行性仍然是 `高`，但它已经不再是仓库主线，而是：

- 本地主线失败时的回退方案
- 或用于更小实现面的备用实现

### 5.2 方案 B：`polkit`

#### 技术路线

`polkit` 方案必须区分两件事：

1. `polkit` 作为桌面授权框架是可行的
2. “应用自己安装一堆通用 JavaScript 规则”不是本项目的推荐落地方式

对于本仓库，更实际的 `polkit` 路线应该是以下两层之一：

#### 路线 B1：`pkexec` + 专用 helper

1. 安装 root 权限 helper
2. 提供配套 `.policy` 动作定义
3. 前端通过 `pkexec` 调起 helper
4. 由桌面认证代理弹出授权对话框

这个路线比 `sudoers` 更贴近桌面交互，但仍然属于“命令式调用”。

#### 路线 B2：特权 D-Bus 机制 + `polkit`

1. 安装一个 system bus 服务或 root 机制程序
2. 前端通过 D-Bus 发请求
3. 特权服务通过 `polkit` 检查授权
4. 授权通过后执行真实写入，再把结果返回前端

这个路线是更完整、更长期的桌面化做法，但复杂度也显著更高。

#### 为什么不推荐“应用自带通用 rules.d 逻辑”作为主路线

`polkit` 官方文档明确把 JavaScript 规则定位给系统管理员和特种环境使用，而不是普通应用普遍安装的第一选择。因此，本项目如果采用 `polkit`，更推荐：

- 定义清晰的动作
- 通过 `.policy` 与 helper / D-Bus 机制协作
- 避免把业务策略直接写成通用 `rules.d` 安装资产

#### 优点

- 与桌面授权代理整合更自然，用户体验通常优于直接 `sudo`
- 更适合以后演进为真正的桌面后台服务
- 如果后续要做更细粒度动作授权，扩展空间优于简单命令放行

#### 缺点

- 实现层级更深，安装资产更多，调试难度更高
- 如果只为一个很小的 Boost 开关动作而上 D-Bus 机制，首版可能投入过重
- `pkexec` 路径虽然较轻，但官方文档也明确提醒：当动作默认授权被修改或允许保留授权时，目标程序绝不能隐式信任输入参数

#### 风险与控制

| 风险 | 说明 | 控制方式 |
| --- | --- | --- |
| 误把 `rules.d` 当应用逻辑层 | 维护与分发风险高 | 以 `.policy` + helper / 机制程序为主，不把规则脚本当主实现 |
| `pkexec` 输入面过宽 | 授权缓存或默认授权变化时可能放大风险 | helper 参数必须是白名单，不接受任意命令行 |
| D-Bus 机制过重 | 首版开发周期过长 | 先评估是否真的需要长驻机制，再决定是否升级 |

#### 可行性结论

`polkit` 的长期架构可行性为 `高`，并且在当前仓库里已经上升为主线方案。

这次选择成立的前提是：

- 目标环境已经收窄到本机 `Ubuntu 24 + GNOME 46`
- 用户更重视 Quick Settings 原生入口和低打扰授权体验
- 实现形态选择的是 `system bus + root 机制程序`，而不是把 `polkit` 理解成单纯的 `pkexec` 包装

因此，当前仓库对 `polkit` 的定位已变为：

- 主线权限后端
- `sudoers` 为回退后端

### 5.3 权限后端方案对比

| 项目 | `sudoers` 受限命令 | `polkit` |
| --- | --- | --- |
| 首发实现复杂度 | 低 | 中到高 |
| 边界是否容易收紧 | 高 | 中 |
| 桌面授权体验 | 中 | 高 |
| 调试和排障难度 | 低到中 | 中到高 |
| 适合当前单功能 MVP | 高 | 中 |
| 适合后续服务化演进 | 中 | 高 |

#### 后端推荐结论

如果当前目标是“本机 GNOME 主线、尽量减少日常重复授权打断”，优先级已经调整为：

1. `polkit + systemd + system bus`
2. `sudoers` 受限命令

如果未来需要更小实现面或主线遇到不可接受的维护成本，再退回 `sudoers` 路径。

## 6. 推荐组合与分阶段落地路线

### 6.1 当前最推荐的首发组合

当前最推荐的首发组合已经调整为：

- 前端：`GNOME Shell 扩展`
- 后端：`polkit + systemd + system bus`

推荐理由：

- 与 `Ubuntu 24 + GNOME 46` 的目标环境最贴合
- Quick Settings 入口比托盘形态更原生
- `system bus + 机制程序` 更适合承接低打扰授权体验
- 仍然能满足“测试默认不写真实 sysfs”的仓库要求

### 6.2 推荐实施顺序

#### 阶段 1：统一后端协议

- 定义 `shared/contracts` 中的 D-Bus 接口、状态结构与错误码
- 明确 `boostctl status/set/diagnose` 的输入输出
- 定义前后端统一日志与错误语义

#### 阶段 2：落地主线后端

- 实现 `system bus + root 机制程序`
- 补齐 `.policy`、systemd 与 D-Bus 激活资产
- 完成模拟测试与显式主机集成验证

#### 阶段 3：落地 GNOME Shell 扩展

- 完成 Quick Settings 状态展示、点击切换、错误提示
- 打通与 D-Bus 后端的状态同步
- 完成主机上的启用、禁用和恢复验证

#### 阶段 4：补齐本机少弹窗配置与诊断

- 通过管理员显式安装流程生成站点本地规则
- 提供组成员、active session、服务状态诊断
- 验证“本机少弹窗”和“可分发保守模式”两种路径

#### 阶段 5：评估第二前端或回退后端

- 如有需要，再补 Python 托盘作为备选入口
- 如主线维护成本不可接受，再评估回退到 `sudoers`

## 7. 最终结论

对于 `boost-switch` 当前这个项目边界，最稳妥的判断不是“哪一个最先进”，而是“哪一个最符合本机 GNOME 主线目标，同时仍保留后续回退空间”。

结论如下：

- 桌面入口层：
  - 当前主线选择为 `GNOME Shell 扩展`
  - `Python 托盘应用` 保留为备选入口
- 权限后端层：
  - 当前主线选择为 `polkit + systemd + system bus`
  - `sudoers` 受限命令保留为回退实现

因此，当前最推荐的路线是：

`GNOME Shell 扩展 + polkit + systemd + system bus` 作为主线先落地，`Python 托盘应用 + sudoers` 作为备选与回退方向保留。

这样既满足了本机 GNOME 46 的原生入口与低打扰授权目标，也给未来简化实现面或回退策略留下了空间。

## 8. 参考资料

### 仓库内文档

- `README.zh-CN.md`
- `docs/architecture/overview.md`
- `AGENTS.md`

### 官方资料

- GNOME JavaScript: Quick Settings
  - https://gjs.guide/extensions/topics/quick-settings.html
- GNOME JavaScript: Extensions Overview
  - https://gjs.guide/extensions/
- GNOME JavaScript: Updates and Breakage
  - https://gjs.guide/extensions/overview/updates-and-breakage.html
- GNOME JavaScript: Port Extensions to GNOME Shell 46
  - https://gjs.guide/extensions/upgrading/gnome-shell-46.html
- PyGObject Overview
  - https://gnome.pages.gitlab.gnome.org/pygobject/index.html
- PyGObject: Adwaita Application
  - https://gnome.pages.gitlab.gnome.org/pygobject/tutorials/libadwaita/application.html
- polkit manual
  - https://polkit.pages.freedesktop.org/polkit/polkit.8.html
- pkexec manual
  - https://polkit.pages.freedesktop.org/polkit/pkexec.1.html
- sudoers manual
  - https://www.sudo.ws/docs/man/sudoers.man/
