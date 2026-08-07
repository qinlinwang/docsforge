# docsforge 需求与路线图（Roadmap）

> 本文档从**用户视角**回答一个问题：**"我作为使用者，希望 docsforge 能帮我做什么？"**
> 并按功能优先级列出怎么做、现状如何，作为需求锚点——后续新增功能回到这里对照取舍。
>
> 一句话定位：**你在源码里写 `docs:` 注释，docsforge 帮你把整个项目的标准文档
> 生成出来，并在源码改动、文档过期时告诉你。**

---

## 一、用户视角的功能全景

按"文档工具的完整生命周期"拆成四类：**认识源码 → 产出文档 → 保证质量 → 融入工作流**。

### 1. 认识源码（提取）

| 功能 | 说明 | 现状 |
|---|---|---|
| **读懂多种语言/框架** | Python(FastAPI)、TypeScript、Go、Java、配置文件、SQL、基础设施（Docker/K8s）……每种语言一个适配器 | ⚠️ 仅 Python(FastAPI) |
| **就近声明 + 自动回退** | 注释优先；代码本身含的信息不写注释也有产出（如 FastAPI 装饰器 → method/path/summary、默认参数 → 默认值、类型注解 → 数据模型） | ✅ 已有（API 装饰器 + 配置默认值回退）|
| **一次扫整个项目** | 从单文件升级为目录/glob 多文件扫描，一本书的文档不再一个个文件拼 | ✅ 已有（`scan.py` 的 `resolve_inputs` + `scan_files`） |
| **定位源码出处** | 每条文档能回溯到声明所在文件 + 行号，方便回查 | ✅ 已有（IR 带 line） |

### 2. 产出文档（渲染）

目标不是"吐一堆 Markdown"，而是**按项目类型产出规范形态**：

| 功能 | 说明 | 现状 |
|---|---|---|
| **API 路由分组表** | 按分组归类的 方法/路径/说明 表 | ✅ 已有 |
| **配置参考表**（`docs:config`） | 配置项 / 环境变量 / 默认值 / 说明，所有后端与基础设施项目都要 | ✅ 已有（MVP：`--token config-reference`）|
| **CLI 命令参考**（`docs:cli`） | 命令行工具自文档化（参数/用法/示例） | ❌ |
| **模块 / 类 / 函数索引** | 库与 SDK 类项目的公共 API 地图（`docs:index` 注解 + `module-index` 渲染器） | ✅ 已完成 |
| **数据模型 / 图表** | schema 表、时序图（`docs:seq` 标记）、架构图 | ❌（仅识别标记） |
| **标准目录骨架**（`docsforge init`） | 每种项目类型有一套推荐的文档目录结构：`reference/`（生成区）+ `guides/topics`（手写区），机器生成与人写物理隔开 | ❌ 是 L1 的核心目标 |

### 3. 保证文档质量（校验）

这是 docsforge 的**核心差异化**——"高质量"意味着文档与源码**永远一致**：

| 功能 | 说明 | 现状 |
|---|---|---|
| **漂移检查** | 比对"现有生成区"与"重新扫描结果"，改了代码忘了重新生成即报错，可进 CI/pre-commit | ✅ 已有 |
| **生成区幂等替换** | 只动 `<!-- BEGIN/END GENERATED -->` 包裹的内容，手写部分绝不被覆盖 | ✅ 已有 |
| **缺失覆盖告警** | "这个 API 端点没写 `docs:` 注解""写了注解却没进文档"，反过来催你补齐文档 | ❌ |
| **规范 lint** | 把团队规范变成机器检查：每个路由必须有 summary / 必须有 method | ❌ |

### 4. 融入工作流（集成）

| 功能 | 说明 | 现状 |
|---|---|---|
| **`scan` 生成 / `check` 校验 / `handlers` 查看** | 三个直觉命令 | ✅ 已有 |
| **精确插入章节**（`--anchor`） | 生成区插到文档指定标题之下，与手写内容共存 | ✅ 已有 |
| **配置驱动（YAML manifest）** | `docsforge.yaml` 声明项目类型、扫哪些文件、**产出哪些章节到哪个目录**；`docsforge init` 按项目类型一键生成标准目录骨架 | ❌ |
| **站点化输出** | 裸 Markdown 之外，可接入 MkDocs / VitePress 成为正式文档站 | ❌ |
| **插件生态** | 装个第三方包即可支持新语言，无需改本仓库（`entry_points` 自动发现） | ❌ |

---

## 二、典型使用场景（为什么需要这些功能）

- **后端服务**：一次扫描全项目，产出 API 路由表 + 配置参考表，提交前 `check` 兜底 → API/配置文档与代码同步演进。
- **SDK / 库**：产出模块/类/函数索引作为 API 手册，README 引用它 → 使用者一行代码入门。
- **基础设施**：Docker / K8s / Terraform 里写 `docs:config` → 自动生成部署配置参考。
- **命令行工具**：`docs:cli` 注解作用到函数/参数 → 生成 CLI 命令参考，替代手写 `--help` 文本。
- **多语言 monorepo**：YAML 声明各子项目的语言与章节，一次 `docsforge scan` 全仓生成。

---

## 三、现状对照：给了多少，缺多少

- **已经能用（S1–S4）**：渲染器按 token 分派（S1）、配置参考表（S2）、Python handler 覆盖类/模块/配置项（S3）、多文件/目录/glob 扫描（S4）；API 路由分组表 + 模块/类/函数索引、漂移检查、生成区幂等替换、`--anchor` 插入、CLI 三命令。
- **最重要的缺口（L1）**：**YAML manifest 配置驱动 + `docsforge init`**——声明项目类型 → 每类项目有推荐文档骨架（`reference/` 生成区 + `guides/topics` 手写区），`scan`/`check` 从 manifest 读取配置一次跑全量。它是"按项目类型差异化"与所有跨语言扩展的 base（见 WS-4）。
- **其次**：CLI 命令参考（`docs:cli` 渲染器，覆盖命令行工具类型项目，WS-5）；跨语言 handler（TS → Go → Java，L2）。
- **已知问题**：Python handler 会把 docstring 中的文档示例（如 `docs:config` / `docs:api` 伪注解）误解析为真实注解，导致对 `docsforge/**/*.py` 的 config-reference 扫描出现误报（WS-6 待修）。
- **长期差异化**：缺失覆盖告警 + 规范 lint（把"质量要求"变成机器强制）、拖进 CI 的漂移门槛、插件生态。

---

## 四、实施顺序（面向用户价值的优先级）

不是按技术依赖，而是按"用户今天最想要什么依次给"：

1. ~~多文件扫描~~ **（S4 已完成）**——让"整个项目"成为可能的共同土壤已就位
2. ~~渲染器按 token 分派~~ **（S1 已完成）**——新增产出物 = 新渲染器 + 新 token，机制已打通
3. ~~配置参考表（S2）/ 模块·类·函数索引（S3）~~ **（已完成）**——后端、基础设施、库/SDK 最普遍要的标准文档已就位
4. **YAML 配置驱动 + `docsforge init`（L1，WS-4）**——① 声明项目类型与目录结构，一键生成骨架，monorepo 一次跑全量；**当前最高优先**
5. **CLI 命令参考（`docs:cli`，WS-5）**——② 覆盖命令行工具类型项目
6. **跨语言 handler（TS → Go → Java）**——③ 覆盖"更多类型项目"
7. **缺失覆盖告警 + 规范 lint**——④ 质量从"生成"提升到"强制补齐"
8. **站点渲染 / 时序图 / 插件生态**——⑤ 体验与生态收尾

> 括号内数字是**给开发者的内部编号**（S1–S4 / L1–L8），工程分层与依赖细节见
> 研发视角补充（本章下方），一般使用者可忽略。

---

## 五、研发视角补充（内部：分层与依赖）

架构主线：`tags`（解析注解）→ `registry/handlers`（按语言提取）→ `render`（渲染）→
`drift`（生成区/漂移）→ `cli`（入口）。只有 handlers/ 是语言相关的，其余全部复用。

| 内部编号 | 功能 | 所在层 | 依赖 |
|---|---|---|---|
| S1 | 渲染器按 topic 分派（新产出物=新渲染器+新 token） | render + cli | ✅ 已完成（`render()` 注册表 + `--token` 多值）|
| S2 | `docs:config` 配置参考表 | render + handlers/python | ✅ 已完成（MVP：config-reference 渲染器）|
| S3 | Python handler 覆盖类/模块/配置项 | handlers/python | ✅ 已完成（配置常量 + 模块 docstring + class 定义）|
| S4 | `scan()` 多文件/目录扫描 ⭐ | registry + handlers + cli | ✅ 已完成（无依赖）|
| L1 | YAML manifest 配置驱动（**含标准文档目录结构 + `docsforge init`**）：声明项目类型 → 每类项目有推荐骨架（`reference/` 生成区 + `guides/topics` 手写区），产出章节写入对应目录 | manifest 解析 + skeleton + cli | S4 |
| L2 | TypeScript / Go / Java handler | handlers | S4 |
| L3 | 从代码推断（默认值/类型→schema） | handlers + render | S1,S3 |
| L4 | 缺失覆盖告警 + 规范 lint | 校验模块 + cli | S1 |
| L5 | 链接完整性校验 | cli + drift | — |
| L6 | `entry_points` 插件自动发现 | registry + pyproject | — |
| L7 | 站点渲染（MkDocs/VitePress） | render + 导出 | — |
| L8 | 时序图/架构图生成器集成 | handlers + render | — |

---

### ⭐ 统一验收目标：本项目吃自己的狗粮

docsforge 仓库自带标准文档骨架（`docs/` + `docsforge.yaml`），因此它本身就是
**S4 / L1 的活验收用例**：

- **S4 验收红线**：必须能一次扫描 `docsforge/**/*.py`，把本项目 `docs/reference/`
  的生成区真正由 `docsforge scan` 填充（替换现有手填占位）。
- **L1 验收红线**：必须能 `docsforge init` 从本项目 `docsforge.yaml` 的
  `structure:` 重建整套骨架；且 `docsforge check` 校验本项目文档与源码一致。

实现 S4 / L1 时，若 docsforge 自己的文档仍无法被工具自驱动，则该功能不算完成。

---

## 六、记录的维护

- 本文档是**需求锚点**：每完成一项，把上表对应格子改为 ✅，并保持与 README 的
  roadmap 摘要同步。
- 完成 **S4 / L1**时，除功能验证外，必须核对上一节的"吃狗粮"验收红线
  （本项目 `docs/` 能被自己的工具自驱动）。
- 若某需求被否决，保留一条记录（标注"已否决"及原因），避免重复评估。
- 新增功能前，先问：这是用户能感知的哪个功能？属于"认识/产出/质量/集成"哪类？
  依赖哪个现有项？答不上来就回到本文档讨论。
- **每次需求讨论的结论必须落盘**：无论是新需求、字段/界面细节，还是"已定/已否决"，
  都写进本章"需求讨论台账"，不留口头结论。避免跨会话遗忘、需求被重复讨论。

---

## 七、需求讨论台账（决策落盘区）

> 这里是**需求讨论的单一事实来源**。每次和 docsforge 聊需求，结论（新增需求、
> 细节定稿、归属阶段、验收标准）都追加到下表；已定稿的就从这里摘到正文对应章节。
> 状态：✅ 已实施 ｜ 🚧 实施中 ｜ 📋 待实施 ｜ ⚖️ 讨论中 ｜ ❌ 已否决（保留原因）

| 日期 | 需求 / 结论 | 归属编号 | 状态 |
|---|---|---|---|
| 08-01 | S4 多文件扫描确认已实现（`scan.py` 的 `resolve_inputs` + `scan_files`；CLI `source` 支持多输入）| S4 | ✅ 已实施 |
| 08-01 | 确立"需求讨论落盘"协作机制：结论写回本表，`check` 前逐条核对 | — | ✅ 已实施 |
| 08-01 | S1 渲染器按 token 分派完成：`render.py` 新增 `@register_renderer(token)` 注册表 + `render(token, decls)`；`--token` 支持多值（`action="append"`），未知 token 报错退出码 2；新增产出物=写渲染器+装饰器一行 | S1 | ✅ 已实施 |
| 08-01 | S2/S3 MVP 完成：`docs:config` 配置参考表 + Python handler 识别模块/类级配置常量（`_config_assignment`）| S2/S3 | ✅ 已实施 |
| 08-01 | **下一步建议**：CLI 命令参考（docs:cli，index）与类/函数索引（module-index），覆盖 SDK/库/命令行工具 | S3/S1 | ⚖️ 讨论中 |
| 08-01 | **module-index 渲染器已实现**：新增 `render_module_index` 令牌渲染器（按模块分组 + 类/函数/位置列）；handler 增强识别模块 docstring 和 class 定义；docsforge 全部 9 个模块已写 `docs:index` 注解；`docs/reference/index.md` 生成区已由工具自驱动填入并验证无漂移，api-routes 生成区同步与 verify 通过 | S3 | ✅ 已实施 |
| 08-06 | **WS-3 需求核查**：S1–S4 全部完成（代码 + 自驱动文档双重确认）。吃狗粮基线：`docsforge check "docsforge/**/*.py" docs/reference/index.md --token module-index`（模块索引）与 `docsforge check examples/main.py docs/reference/api-routes.md --token api-routes`（路由示例）均无漂移；`docs/reference/config.md` 由 `examples/main.py` 的 `docs:config` 注解驱动 | S1–S4 | ✅ 已实施 |
| 08-06 | **拆分下一批需求**：L1 YAML manifest 配置驱动 + `docsforge init`（最高优先，解锁标准目录骨架与按项目类型差异化）→ **WS-4**；CLI 命令参考渲染器（`docs:cli`）→ **WS-5**；修复 config 扫描误报（docstring 伪注解被解析：对 `docsforge/**/*.py` 的 config-reference 扫描误报 `PORT`/`render_config_reference` 两条）→ **WS-6** | L1 / — / — | 📋 待实施 |
