# XTable 阶段开发评估记录

本文档是 XTable 项目规范的一部分，用于记录每个开发阶段在审核、验收或复盘中发现的问题，并作为后续开发、返工和验收的目标参考。

## 1. 评估记录规则

- 每次阶段审核、人工验收、代码评审或架构复盘后，必须在本文档追加记录。
- 问题必须归属到具体阶段；跨阶段问题需要在所有受影响阶段记录，或明确写入“跨阶段问题”。
- 问题必须归档到明确批次。每次集中审核形成一个批次，批次记录需要说明来源、范围、状态和关联问题 ID。
- 每条问题必须包含严重级别、问题描述、影响、修改建议和当前状态。
- 严重级别使用 `P1`、`P2`、`P3`：
  - `P1`：阻塞阶段验收、影响数据安全、破坏核心架构或导致后续阶段无法可靠推进。
  - `P2`：不阻塞最小运行，但会造成明显质量、可维护性、测试或体验风险。
  - `P3`：文档、命名、覆盖率、细节体验或后续增强项。
- 阶段进入“已完成”前，必须确认本文档中该阶段的 `P1` 问题已关闭；遗留 `P2/P3` 必须写明接受原因和后续处理阶段。
- 开发日志中的阶段进度和验收完整度必须与本文档中的未关闭问题保持一致。
- 当前会话角色为测试角色时，只能评估、找 bug、复验、验收和更新文档，不得直接修改实现代码、测试代码或资源文件；角色按会话区分，边界以 [项目角色协作规范](./project-role-guidelines.md) 为准。

## 2. 状态枚举

- `待处理`：已确认问题，尚未开始修改。
- `处理中`：正在修改或已有部分修复。
- `待验证`：已修改，等待测试、人工验收或复盘确认。
- `已关闭`：已验证通过。
- `接受遗留`：明确不在当前阶段修复，已记录原因和后续处理阶段。

## 3. Phase 0：工程骨架与技术基线

### 3.1 审核结论

Phase 0 已建立 Python/PySide6 工程骨架、应用入口、主窗口和测试命令，自动化测试可以运行。当前可作为工程基线继续推进，但基础主题和 UI 模块边界仍需在后续阶段补齐，避免 Phase 3 之后返工成本上升。

### 3.2 问题记录

| ID | 级别 | 问题 | 影响 | 修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- |
| P0-001 | P2 | Phase 0 交付内容要求包含“基础主题”，但当前仅有主窗口骨架，尚未形成统一主题变量或可切换主题实现。 | 后续 UI 组件容易出现颜色、间距和状态样式分散硬编码，影响 Dark/Light 主题验收。 | 在 UI 模块中新增主题 token/QSS 管理，并为主窗口、工具栏、侧栏、状态栏接入统一主题。 | 已关闭 |
| P0-002 | P2 | PySide6 主窗口、弹窗和布局目前位于 `app/main_window.py`，与规划中 `app` 负责启动装配、`ui` 负责视图控件的模块边界不完全一致。 | 后续表格工作台、问题抽屉、主题系统扩展时，`app` 层可能承载过多 UI 细节。 | 将主窗口、项目弹窗、主题与基础控件逐步迁移到 `xtable.ui`，`xtable.app` 保留应用入口和装配逻辑。 | 已关闭 |
| P0-003 | P3 | UI smoke 测试当前只验证主窗口和少量对象存在，未覆盖主题切换、核心面板打开和状态栏结构。 | Phase 0 验收证据偏弱，无法提前发现布局或主题退化。 | 补充基础 UI 测试：主窗口区域、侧栏按钮语义、主题切换入口和状态栏字段。 | 已关闭 |

## 4. Phase 1：项目与文件系统

### 4.1 审核结论

Phase 1 已实现项目创建、打开、保存、最近项目记录，以及外部修改/只读/写入失败的基础冲突检测。当前更适合标记为“待验收”，不建议直接视为完整完成；项目目录结构、文件安全语义、UI 验收项和测试覆盖仍有差距。

### 4.2 问题记录

| ID | 级别 | 问题 | 影响 | 修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- |
| P1-001 | P1 | 推荐项目目录结构未按规范落地。需求要求 `tables/ rules/ enums/ types/ settings/ logs/ cache/ recovery/`，当前实现只创建 `tables/ exports/ .xtable/recovery/ .xtable/logs/`。 | Phase 2/6 的规则、枚举、Meta 和设置文件缺少稳定承载位置，也可能污染后续版本工具约定。 | 调整项目创建目录结构，与需求文档保持一致；如保留内部 `.xtable` 目录，需要同步更新需求和开发计划。 | 已关闭 |
| P1-002 | P1 | 保存流程直接写目标配置文件，缺少临时文件写入、flush/fsync 和原子替换。 | 写入中断或系统异常可能损坏 `xtable.project.json`，文件安全验收证据不足。 | 将保存流程改为临时文件写入并原子替换；失败时保持原文件不变，并补充失败回滚测试。 | 已关闭 |
| P1-003 | P1 | 文件占用检测当前通过写入失败统一映射为冲突提示，无法区分占用、权限、磁盘或其他 I/O 失败。 | 用户无法获得明确处理建议，且与“检测被占用、只读或外部修改”的验收语义存在差距。 | 增加平台适配层或错误分类，至少在 UI 提示中区分外部修改、只读、写入失败和疑似占用。 | 已关闭 |
| P1-004 | P2 | UI 侧栏只有 `T/E/M` 按钮，缺少明确的 `Table/Enum/Meta` 语义、对象名和右侧功能窗口切换。 | 不满足 UI 验收中“点击 Table、Enum、Meta 切换对应界面”的要求。 | 为三个入口提供稳定对象名、工具提示和占位页面；点击后切换中央/右侧工作区。 | 已关闭 |
| P1-005 | P2 | 状态栏当前只是单条消息，未拆分当前项目、当前对象、保存状态、校验状态、后台任务和问题数量。 | 不满足状态栏验收，也会限制后续校验、后台任务和问题报告接入。 | 建立状态栏模型或多个 QLabel 字段，并提供统一更新方法。 | 已关闭 |
| P1-006 | P2 | 主题切换和问题报告抽屉尚未实现。 | 与主需求 UI 与主题验收项不一致，Phase 3/4 接入问题报告时会再次返工。 | 在 Phase 1 收尾或 Phase 2 前补齐最小主题切换和问题抽屉占位能力。 | 已关闭 |
| P1-007 | P2 | 项目文件测试覆盖偏基础，缺少损坏 JSON、缺字段、最近项目文件损坏、目录结构完整性、原子保存失败回滚等场景。 | 难以支撑“文件安全检测已完成”的验收结论。 | 扩展 `tests/test_project_files.py`，覆盖异常输入、错误分类、目录规范和回滚行为。 | 已关闭 |
| P1-008 | P3 | 开发日志中 Phase 1 进度和验收完整度偏乐观。 | 后续阶段可能基于过高完成度推进，导致阶段依赖风险被低估。 | 将 Phase 1 标记为待验收并注明未关闭 P1/P2 问题；验收完整度与本文档保持一致。 | 已关闭 |

## 5. 跨阶段问题

| ID | 级别 | 问题 | 影响 | 修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- |
| X-001 | P2 | 自动化测试通过，但测试内容主要是 smoke 和服务 happy path，缺少对验收标准的系统映射。 | 阶段“测试通过”容易被误解为“验收通过”。 | 后续每个阶段至少建立一组与开发计划验收标准一一对应的测试或人工验收清单。 | 已关闭 |
| X-002 | P2 | 当前不是 Git 仓库，无法通过 commit 历史追踪阶段变更。 | 与开发计划中“文档更新不得替代 Git commit message”的规范存在执行缺口。 | 初始化版本管理或在进入正式开发分支前明确外部版本管理方式。 | 已关闭 |

## 6. 批次归档

### 6.1 第一批次：Phase 0/Phase 1 基础验收问题

- 来源：Phase 0、Phase 1 计划完成度、代码质量、架构设计、功能完整度和 UI 布局审核。
- 范围：工程骨架、主题基线、UI 模块边界、项目目录结构、文件安全、侧栏切换、状态栏、问题抽屉、测试覆盖和开发日志一致性。
- 关联问题：`P0-001`、`P0-002`、`P0-003`、`P1-001`、`P1-002`、`P1-003`、`P1-004`、`P1-005`、`P1-006`、`P1-007`、`P1-008`、`X-001`、`X-002`。
- 当前状态：已验收并关闭。

#### 6.1.1 第一批次未达 100% 问题修改建议

| ID | 当前完成度判断 | 修改建议 | 建议优先级 |
| --- | --- | --- | --- |
| P0-001 | 约 90% | 扩展主题 token 和 QSS 覆盖范围，不只覆盖窗口、普通按钮和标签，还要覆盖 `QToolButton`、`QMenuBar`、`QMenu`、`QToolTip`、`QStatusBar` 以及 disabled/hover/checked 状态。Dark/Light 主题应统一从 token 生成样式，并补充工具栏、菜单和状态栏可读性测试。 | P1 |
| P0-002 | 约 90% | 继续收敛模块边界：将 `ProjectDialogs`、action 定义、图标定义、菜单构建、状态栏组件、问题抽屉组件拆入 `xtable.ui` 子模块；`xtable.app` 只保留应用入口和兼容导出，避免后续业务 UI 继续堆叠到 app 层。 | P2 |
| P1-002 | 约 90% | 在现有临时文件、`flush/fsync` 和 `os.replace` 基础上补充目录级 fsync、跨平台替换失败验证、异常恢复策略和临时文件清理策略；测试应覆盖替换失败、临时文件残留、原文件不变和保存后 digest 更新。 | P1 |
| P1-003 | 约 70% | 增加平台适配层，不要把所有 `PermissionError` 都归为 `LOCKED`。至少区分只读、权限拒绝、文件占用、磁盘空间不足、路径不存在、普通写入失败和外部修改；UI 错误提示要按类型给出明确处理建议。 | P1 |
| P1-006 | 约 90% | 主题切换需要补完整控件样式覆盖，并与第二批次 `B2-005` 合并处理 Dark 工具栏可读性；问题抽屉需要按 `B2-006` 改为底部弹出，不再作为右侧面板，并补显隐、尺寸、布局不挤压主工作区的测试。 | P1 |
| P1-007 | 约 95% | 在现有项目文件测试基础上继续补第二批次相关测试：图标按钮、菜单分组、主题按钮靠右、Dark 工具栏可读性、底部问题抽屉、项目配置 schema 和旧配置迁移。 | P2 |
| P1-008 | 约 80% | 开发日志的阶段进度和验收完整度必须跟评估文档状态一致。未关闭问题存在时，不宜写 `100%/95%`；建议改为“已实现，待验证”，待问题关闭后再提升完成度。 | P2 |
| X-001 | 未完全完成 | 为 Phase 0/1 建立验收映射清单，把每条开发计划验收标准映射到自动化测试或人工验收项。测试通过不等于验收通过，人工验收项应明确截图、操作步骤或检查结果。 | P2 |
| X-002 | 已实现，待验证 | 已初始化本地 Git 仓库；待人工验收后可执行首个阶段提交，形成正式 commit 历史。 | P2 |

#### 6.1.2 第一批次修复记录

- 主题：扩展 token 与 QSS 覆盖 `QToolButton`、`QMenuBar`、`QMenu`、`QToolTip`、`QStatusBar` 和 hover/checked/disabled 状态。
- 模块边界：新增 `xtable.ui.actions`、`xtable.ui.dialogs`、`xtable.ui.status_bar`、`xtable.ui.issue_drawer`，`xtable.app` 继续只保留入口和兼容导出。
- 文件安全：保存流程包含临时文件写入、文件 fsync、原子替换、目录 fsync 和失败清理。
- 错误分类：补充只读、权限拒绝、疑似占用、磁盘空间不足、路径不存在、普通写入失败和外部修改分类。
- 验收映射：新增 [Phase 0/1 验收映射清单](./acceptance-map.md)。

### 6.2 第二批次：主界面视觉层级与工具栏交互评估

- 来源：人工 UI 审核截图与需求规范复核。
- 范围：主窗口区域边界、工具栏菜单分类、图标按钮规范、左侧侧栏图标化、状态栏图标标识、主题切换位置、问题抽屉弹出方向、项目配置参数完整性和 Dark 主题可读性。
- 当前状态：已验收并关闭。

| ID | 阶段 | 级别 | 问题 | 原因分析 | 影响 | 完整修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B2-001 | Phase 0/1 | P2 | 各个布局区域没有明确边界和主次。 | 当前主窗口主要依赖默认 `QToolBar`、`QStatusBar`、`QFrame` 和 `QStackedWidget` 组合，主题样式只提供颜色，缺少区域级边框、分隔线、背景层级、间距和选中态规范；工作区、工具栏、侧栏、问题抽屉、状态栏之间没有形成稳定视觉层级。 | 用户难以快速判断可操作区域、内容区域和状态区域；后续表格工作台接入后会显得拥挤且主次不清。 | 建立主界面布局层级规范：顶部菜单/工具栏使用独立背景和底部分隔线；左侧导航使用固定宽度和右分隔线；中间工作区使用主背景；问题抽屉使用独立面板背景和左分隔线；状态栏使用更低视觉权重和顶部分隔线。补充 QSS token：`window_bg`、`panel_bg`、`toolbar_bg`、`workspace_bg`、`border`、`hover_bg`、`active_bg`、`muted_text`。为每个区域设置 objectName 并在 UI smoke 测试中验证区域存在和层级属性。 | 已关闭 |
| B2-002 | Phase 1 | P2 | 需求说明通用操作按钮应按图标按钮处理，目前仍以文字按钮为主。 | Phase 1 为了快速形成入口，直接使用 `QAction(label)` 和文本按钮；没有建立统一图标资源、动作枚举和 tooltip 规则，也没有区分“菜单命令”和“快捷图标按钮”。 | 工具栏视觉密度低、不同操作权重混乱；与需求中“通用操作按钮应该是图标按钮”的 UI 规范不一致。 | 建立 `ui/actions.py` 或 `ui/icons.py`：为新建、打开、保存、导入、导出、校验、撤销、重做、问题、主题等动作定义稳定 action id、图标、tooltip、快捷键和菜单归属。工具栏常用操作只显示图标，文字放入 tooltip 和菜单项；没有图标资源前可先使用 Qt 标准图标或内置轻量 SVG，后续统一替换。测试应验证工具栏 action 有 icon、toolTip 和 objectName。 | 已关闭 |
| B2-003 | Phase 1 | P2 | 左侧边栏需要调整为符合设定的图标按钮，状态栏特定名称也需要用图标标识。 | 当前左侧侧栏虽有 `Table/Enum/Meta` 语义 tooltip，但显示仍是首字母文本；状态栏使用中文字段名前缀，导致底部信息占宽且视觉噪声较高。 | 左侧导航不像工具型应用的主导航；状态栏扫描效率低，后续加入当前表、选区、校验、任务和问题数量后会更拥挤。 | 左侧侧栏改为图标按钮：Table 使用表格/网格图标，Enum 使用列表/标签图标，Meta 使用结构/节点图标；按钮保持 36-40px 固定尺寸，选中态用高亮边框或背景。状态栏字段使用图标 + 短值：项目、对象、保存、校验、后台任务、错误/警告分别使用图标标识，完整名称放 tooltip；状态栏文本只保留必要值，如项目名、Table、已保存、未校验、空闲、0/0。 | 已关闭 |
| B2-004 | Phase 1 | P2 | 工具栏应该合理分类，划分成不同菜单，主题切换按钮靠右对齐，并参考 Codex 界面的菜单结构。 | 当前所有 action 平铺在同一个工具栏内，缺少 File/Edit/View/Window/Help 等菜单层级，也没有左侧主命令区和右侧全局控制区的布局分离。主题切换混在普通操作中，权重不合理。 | 菜单扩展性差；导入、导出、校验、撤销、重做等后续动作加入后会继续挤压顶部空间；用户无法按操作类别建立稳定记忆。 | 引入 `QMenuBar` 分类：文件（新建、打开、最近项目、保存、另存、导入、导出、退出）、编辑（撤销、重做、查找、替换）、查看（主题、问题面板、日志面板、重置布局）、窗口（面板切换、全屏/布局）、帮助（关于、诊断信息）。顶部工具栏仅保留高频图标快捷入口，并用 separator 分组：项目组、编辑组、校验/问题组。右侧增加 spacer，将主题切换、运行/任务状态、帮助/诊断等全局按钮靠右对齐。 | 已关闭 |
| B2-005 | Phase 1 | P1 | Dark 主题下工具栏文本看不清。 | 当前 QSS 对 `QToolBar` 设置了背景，但没有覆盖 `QToolButton`、`QMenuBar`、`QMenu`、`QToolTip` 和 disabled/hover/checked 状态；Qt 默认样式在深色背景上仍可能使用低对比文本。截图显示深色工具栏上的文字接近黑色，说明 token 未完整传递到工具栏按钮。 | Dark 主题基础可用性不达标，影响 Phase 0“基础主题”和 Phase 1 UI 验收；属于用户可直接感知的问题。 | 扩展主题样式覆盖：`QToolBar QToolButton`、`QMenuBar`、`QMenuBar::item`、`QMenu`、`QMenu::item`、`QStatusBar`、`QToolTip` 的 foreground/background/border/hover/pressed/disabled；Dark token 中保证文本与背景对比度至少达到可读标准。把工具栏按钮改为图标为主后，仍需确保 tooltip、菜单和少量文字按钮在 Dark 下可读。新增 UI 测试至少验证 Dark 主题 stylesheet 包含 `QToolButton` 和菜单样式。 | 已关闭 |
| B2-006 | Phase 1 | P2 | 问题抽屉应该从下方弹出，而不是作为右侧面板出现。 | 当前问题抽屉实现为右侧固定宽度 `QFrame`，这是为了快速占位；但需求中的问题报告更接近底部抽屉，应该与状态栏中的问题入口联动，从底部展开以承载横向表格、筛选和定位信息。 | 右侧抽屉会挤压主工作区宽度，后续表格编辑体验受影响；问题列表天然需要横向空间，右侧窄面板不利于展示表、字段、行列、级别和原因。 | 将问题抽屉改为底部区域：主布局改为垂直结构或使用 `QSplitter(Qt.Vertical)`，上方为工作区，下方为可折叠 issue panel；默认收起，仅保留状态栏问题入口。展开时高度建议 180-260px，可拖拽调整。问题抽屉内预留筛选栏、问题表格、详情/建议区域；状态栏问题按钮控制底部抽屉显隐。测试验证 `issue-drawer` 位于底部容器，并且切换不改变左侧导航和工作区主宽度。 | 已关闭 |
| B2-007 | Phase 1 | P2 | 用户新建项目生成的项目配置文件参数不够完整，应注明项目导出目录以及更详细的项目参数。 | 当前 `xtable.project.json` 主要保存项目名、操作者、默认编码、日志保留天数和主题；目录约定虽然通过创建目录体现，但没有在配置中显式记录导出目录、表目录、规则目录、日志/缓存/恢复目录、项目版本、创建时间、更新时间等元信息。 | 后续导入导出、版本迁移、跨机器打开项目和诊断日志会缺少可靠配置来源；导出目录不明确会导致 UI、IO 和日志模块各自推断路径，增加不一致风险。 | 扩展项目配置 schema：新增 `schema_version`、`created_at`、`updated_at`、`project_id`、`paths`、`export`、`ui`、`safety` 等结构。`paths` 至少包含 `tables_dir`、`rules_dir`、`enums_dir`、`types_dir`、`settings_dir`、`logs_dir`、`cache_dir`、`recovery_dir`、`exports_dir`；`export` 至少包含默认导出目录、默认格式、覆盖策略和是否导出前校验。保持向后兼容：旧配置打开时补默认值并在保存时写回新结构。同步补充测试：新建项目配置包含导出目录和详细参数，旧配置可迁移打开。 | 已关闭 |

### 6.3 第三批次：图标体系、底部抽屉与状态栏问题入口评估

- 来源：人工 UI 审核截图与主题一致性复核。
- 范围：项目图标规范、两套主题图标适配、Dark 主题下底部抽屉内容样式、底部抽屉可拖拽尺寸、日志与问题面板整合、状态栏问题入口和侧边栏图标语义。
- 当前状态：未通过问题已修复，等待人工复验。

#### 6.3.1 UI 图标规范

- 所有工具栏、侧边栏、状态栏和抽屉页签图标必须使用统一项目图标体系，不再直接使用 Qt 默认彩色图标或临时文本符号作为最终 UI。
- 图标风格应扁平、单线或低填充、几何化，线宽、圆角、留白和尺寸统一；默认目标尺寸为工具栏 18-20px，侧边栏 22-24px，状态栏 14-16px。
- 图标必须适配 Light/Dark 两套主题。图标颜色不得写死为单一黑色或彩色，应由主题 token 控制：普通、悬停、选中、禁用、警告、错误、成功等状态分别映射到主题色。
- 图标语义必须清晰：项目、打开、保存、导入、导出、校验、撤销、重做、主题、诊断、Table、Enum、Meta、问题、日志等动作都要有稳定 icon id。
- 若使用 SVG，应集中存放在 UI 资源目录，并通过统一 icon loader 根据主题和状态着色；若后续生成位图资源，也必须保留源文件和命名规范。
- 测试应覆盖关键动作均有 icon id、主题切换后图标可换色或可读、侧边栏图标尺寸满足规范。

| ID | 阶段 | 级别 | 问题 | 原因分析 | 影响 | 完整修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B3-001 | Phase 0/1 | P2 | 现有工具栏图标太丑，且很多不符合项目设定，需要新增 UI 图标规范并按项目风格生成。 | 当前工具栏使用 Qt 标准图标，视觉风格来自系统默认；不同图标线宽、色彩、透视和语义不统一，和 XTable 面向专业配置表编辑器的安静工具型风格不匹配。 | 顶部工具栏观感像临时原型，降低产品完成度；后续功能增多后，图标语义不统一会影响用户识别效率。 | 新增项目图标规范和资源目录，例如 `src/xtable/ui/icons/`；定义统一 icon id、SVG 命名、尺寸、线宽和主题颜色 token。为新建、打开、保存、导入、导出、校验、撤销、重做、主题、问题、诊断等动作生成项目风格 SVG；`ui/actions.py` 不再直接依赖 Qt 标准图标，而是通过统一 icon loader 获取主题化图标。 | 已关闭 |
| B3-002 | Phase 1 | P1 | 切换到 Dark 主题后，问题窗口内容区域仍是白色，不符合主题规范。 | 当前主题 QSS 覆盖了 `QFrame#issue-drawer`，但没有完整覆盖抽屉内部的 `QTableWidget`、header、viewport、corner、grid、selection 等子控件；Qt 表格默认 viewport 仍保持白色。 | Dark 主题下出现大块白色区域，视觉割裂且刺眼，属于明显主题验收失败。 | 在主题系统中补充 `QTableWidget`、`QHeaderView::section`、`QTableCornerButton::section`、`QAbstractScrollArea`、`QScrollBar`、selection 和 grid 样式；问题抽屉内所有控件必须从主题 token 获取背景、文字、边框和选中态颜色。新增测试验证 Dark 主题 stylesheet 覆盖 `QTableWidget` 和 `QHeaderView`。 | 已关闭 |
| B3-003 | Phase 1 | P2 | 底部抽屉弹出后，应该能够拖动上边界调整窗口大小。 | 当前 `IssueDrawer` 只是固定最小/最大高度的 `QFrame`，没有 splitter 或拖拽手柄；用户无法根据问题数量和表格内容调整可见区域。 | 问题列表较多或日志内容较长时，用户只能在固定高度内查看，影响排查效率。 | 将主工作区与底部抽屉放入 `QSplitter(Qt.Vertical)`，或为抽屉上边界实现可拖拽 resize handle。默认高度可为 220px，允许在 160px 到窗口高度 50% 之间调整；记录用户上次高度到 UI 配置。测试验证抽屉容器可调整尺寸且不会改变左侧导航宽度。 | 已关闭 |
| B3-004 | Phase 1/7 | P2 | 日志也应整合进底部抽屉，通过切换页签控制。 | 当前底部抽屉只承载问题报告，日志系统未来仍可能另起面板；问题与日志都是诊断类信息，分散展示会增加底部区域和状态栏入口复杂度。 | 后续 Phase 7 接入日志时容易重复实现抽屉、筛选和列表控件；用户在问题与日志之间切换路径不稳定。 | 将底部抽屉改为诊断抽屉，内部使用 `QTabWidget` 或等效页签：`问题`、`日志`。问题页展示问题表格，日志页预留日志列表、级别筛选、关键词搜索和复制诊断信息入口。状态栏的问题/日志入口控制同一个底部抽屉，并可切换到对应页签。 | 已关闭 |
| B3-005 | Phase 1/4 | P2 | 问题按钮应该位于底部状态栏，由图标 + 数字组合；图标代表当前最高优先级的问题类型，数字为对应问题数量。 | 当前问题入口仍在顶部工具栏，状态栏只有简单问题数量文本；这和“底部状态栏展示错误和警告数量、问题按钮展开抽屉”的交互定位不一致。 | 用户需要到顶部找问题入口，状态栏不能直接表达当前最严重问题状态；后续校验接入后，问题反馈不够即时。 | 从顶部工具栏移除或弱化问题入口，在 `EditorStatusBar` 中新增 `IssueStatusButton`。按钮显示最高级别图标：Error、Warn、Info 或 OK；旁边显示对应数量，如 `3` 或 `0`。tooltip 展示 Error/Warn/Info 详细数量；点击打开底部诊断抽屉并切换到问题页。状态由 validation/issue 模型统一更新。 | 已关闭 |
| B3-006 | Phase 1 | P2 | 侧边栏按钮图标太小、不够扁平，意义不够明确，需要重新生成。 | 当前侧边栏使用临时文本符号模拟图标，尺寸、语义和风格都不稳定；选中态虽然可见，但图标自身不能清楚表达 Table、Enum、Meta。 | 用户识别主导航需要依赖 tooltip，第一眼无法理解图标含义；界面显得像工程占位而非正式产品。 | 为 Table、Enum、Meta 生成专用扁平 SVG：Table 使用网格/表格结构，Enum 使用列表/标签集合，Meta 使用节点/结构字段。图标尺寸提高到 22-24px，按钮保持 40-44px；普通态、悬停态、选中态颜色由主题 token 控制。补充测试或视觉验收清单，确认侧栏不再使用文本符号作为最终图标。 | 已关闭 |

#### 6.3.2 第三批次验收记录

- 验收时间：2026-05-23。
- 验收方式：代码审查、本地自动化测试、Qt offscreen 渲染截图和运行时控件属性检查。
- 自动化结果：`python -m pytest` 通过，26 项测试全部通过。
- 总体结论：第三批次未通过项已完成返工修复，等待人工复验后关闭。

| ID | 验收结论 | 证据 | 后续要求 |
| --- | --- | --- | --- |
| B3-001 | 已复验通过。正式 SVG 资源目录 `src/xtable/ui/resources/icons/` 已建立，所有 icon id 都有独立 SVG 文件，并由 `icon_for` 统一按主题着色加载。 | `src/xtable/ui/icons.py`、`src/xtable/ui/resources/icons/*.svg`、`tests/test_icons.py`。 | 已关闭。 |
| B3-002 | 已复验通过。已补 `QTabWidget::pane`、`QTabBar::tab`、`QLineEdit`、`QWidget#diagnostics-page` 和表格/滚动区样式，Dark 复验截图未再出现大块白色区域。 | `src/xtable/ui/theme.py`、`tests/test_main_window.py`、`third-batch-dark-drawer-recheck.png`。 | 已关闭。 |
| B3-003 | 已复验通过。抽屉高度范围改为 160px 到窗口高度 50%，并通过 `ui_state["diagnostics_drawer_height"]` 记录用户设置。 | `MainWindow.configure_diagnostics_drawer_bounds`、`MainWindow.set_diagnostics_drawer_height`、`tests/test_main_window.py`。 | 已关闭；后续如接入真实配置文件，可把 `ui_state` 持久化到项目 UI 配置。 |
| B3-004 | 已复验通过。底部抽屉已改为诊断抽屉，包含“问题”“日志”两个页签，状态栏点击可切换到问题页，代码也支持传入 `logs` 切换日志页。 | `IssueDrawer` 使用 `QTabWidget`；测试 `test_diagnostics_drawer_uses_vertical_splitter_and_log_tab` 通过。 | 已关闭；进入 Phase 7 时继续补日志数据模型、过滤、复制诊断信息和持久化。 |
| B3-005 | 已复验通过。顶部工具栏已移除 `action-toggle-issues` 高频入口，问题入口保留在查看菜单和状态栏按钮中，状态栏按钮为主入口。 | `tests/test_main_window.py` 验证 toolbar actions 不包含 `action-toggle-issues`；运行时检查通过。 | 已关闭。 |
| B3-006 | 已复验通过。侧栏按钮已使用正式 SVG 图标，并新增 `QToolButton#nav-table/#nav-enum/#nav-meta` 普通、hover、checked 主题样式。 | `src/xtable/ui/theme.py`、`tests/test_main_window.py`、Dark 复验截图。 | 已关闭。 |

### 6.4 重复问题归因与项目规范沉淀

第三批次重复暴露了第一、第二批次已经出现过的三类问题：主题覆盖只处理外层控件、图标按钮缺少正式资源和视觉验收、诊断入口在工具栏与状态栏之间职责摇摆。后续 UI 开发必须遵守 [UI 实现质量规范](./ui-implementation-guidelines.md)，避免同类问题再次进入下一批次。

#### 6.4.1 第三批次复验记录

- 复验时间：2026-05-23。
- 复验方式：代码审查、本地自动化测试、Qt offscreen 运行时控件属性检查和 Dark 主题截图复验。
- 自动化结果：`python -m pytest` 通过，28 项测试全部通过。
- 截图证据：[第三批次 Dark 主题复验截图](./previews/third-batch-dark-drawer-recheck.png)。
- 总体结论：第三批次复验通过，`B3-001` 到 `B3-006` 均可关闭。

| ID | 复验结论 | 证据 |
| --- | --- | --- |
| B3-001 | 通过。正式 SVG 资源目录已建立，所有 icon id 均有同名 SVG 文件，图标由统一 loader 按主题着色加载。 | `src/xtable/ui/resources/icons/`、`src/xtable/ui/icons.py`、`tests/test_icons.py`。 |
| B3-002 | 通过。Dark 主题已覆盖诊断抽屉 tab、pane、输入框、表格和滚动区域，复验截图未再出现大块白色内容区域。 | `src/xtable/ui/theme.py`、`third-batch-dark-drawer-recheck.png`。 |
| B3-003 | 通过。底部抽屉使用垂直 `QSplitter`，高度范围可配置为最小 160px、最大约窗口高度 50%，并记录到 `ui_state["diagnostics_drawer_height"]`。 | 运行时检查：`minimumHeight=160`，`maximumHeight` 随窗口高度计算；`set_diagnostics_drawer_height()` 可更新 splitter size。 |
| B3-004 | 通过。问题与日志已统一在底部诊断抽屉中通过页签切换。 | `IssueDrawer`、`QTabWidget#diagnostics-tabs`。 |
| B3-005 | 通过。顶部工具栏已移除问题高频入口，状态栏 `IssueStatusButton` 可显示最高级别图标和数量，并打开问题页。 | 运行时检查：`top-toolbar` 不包含 `action-toggle-issues`；状态栏按钮 `icon-id=error/warn/info/ok`。 |
| B3-006 | 通过。侧栏按钮使用正式 SVG 图标，尺寸 24px，且 `QToolButton#nav-table/#nav-enum/#nav-meta` 已有普通、hover、checked 主题样式。 | `src/xtable/ui/theme.py`、`tests/test_main_window.py`。 |

### 6.5 第四批次：诊断抽屉边界、状态栏密度与工具图标细节评估

- 来源：人工 UI 复核截图与第四批次补充反馈。
- 范围：Dark 主题下诊断抽屉边界/阴影、底部状态栏信息密度、状态栏问题按钮样式与位置、撤回/前进图标风格。
- 当前状态：已验收并关闭。
- 当前会话角色：测试角色。本批次经人工确认基本验收通过，当前会话仅执行验收归档和后续问题记录。

| ID | 阶段 | 级别 | 问题 | 原因分析 | 影响 | 完整修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B4-001 | Phase 1 | P2 | 问题面板抽屉在 Dark 主题下边界/阴影部分颜色不匹配。 | 当前诊断抽屉、splitter handle、tab pane、表格外框和窗口边界的颜色 token 没有完全统一；部分边界仍接近亮色或系统默认分隔效果，在深色界面中形成突兀的浅色“阴影”。 | Dark 主题整体性下降，用户会明显看到抽屉和工作区之间有不协调的亮色边缘；这是第三批次主题覆盖问题的细节延伸。 | 统一 `QSplitter::handle`、`QFrame#issue-drawer`、`QTabWidget::pane`、`QTableWidget` 外框和诊断抽屉容器边界颜色。Dark 主题下边界应使用低对比 `border` 或专门的 `shadow_border` token，避免出现纯白或过亮灰线；必要时为诊断抽屉增加独立 `drawer_border` token。复验需要提供 Dark 主题截图。 | 已关闭 |
| B4-002 | Phase 1 | P3 | 底部状态栏信息过于密集，需要适当增加间隔。 | 当前状态栏字段使用多个短文本紧贴排列，缺少字段分组、左右 padding 和低对比分隔；信息虽然完整，但扫描时拥挤。 | 状态栏可读性下降，项目、对象、保存状态、校验状态、任务状态和问题数量容易混在一起；后续字段增加后会更拥挤。 | 为状态栏字段建立统一布局规范：字段之间增加 8-12px 间隔或低对比分隔线；每个字段保留最小左右 padding；弱化非关键字段视觉权重。建议将状态栏按左侧问题入口、中间项目上下文、右侧保存/校验/任务状态分组。 | 已关闭 |
| B4-003 | Phase 1/4 | P2 | 问题按钮未按需求实现为靠左的“图标 + 数量”组合。 | 当前状态栏问题入口仍偏单按钮模式，展示形式没有完全贴合用户给出的参考图：错误图标、错误数量、警告图标、警告数量需要作为紧凑组合出现，并且位置应靠左。 | 问题状态识别效率不够高；用户无法在状态栏左侧第一时间看到错误/警告数量，也不符合已明确的交互期望。 | 在状态栏靠左新增问题摘要组件，例如 `IssueSummaryWidget`：显示 `error icon + error count`、`warn icon + warn count`，可选支持 info。组件整体点击打开底部诊断抽屉问题页；tooltip 展示 Error/Warn/Info 详细数量。右侧状态字段保留项目、对象、保存、校验、任务等信息，并与问题组件保持间距。 | 已关闭 |
| B4-004 | Phase 1 | P3 | 撤回/前进图标不好看，需要参考扁平左右箭头重新绘制。 | 当前 `undo`/`redo` 图标为弯箭头语义，和用户参考的简洁左右箭头风格不一致；在当前顶部工具栏中视觉重量和其它线性图标也不完全统一。 | 工具栏视觉一致性下降，撤回/前进动作显得不够轻量、扁平；影响工具栏整体精致度。 | 重新绘制 `undo.svg` 和 `redo.svg`，参考扁平左右箭头：使用单线、几何化、低复杂度路径，保持 24px viewBox、1.8px 线宽、round cap/join 和 `{color}` 主题占位符。更新后需在 Light/Dark 下截图复验，并确认工具栏图标视觉重量一致。 | 已关闭 |

#### 6.5.1 第四批次修复记录

- 主题边界：新增 `drawer_border` 和 `shadow_border` token，统一诊断抽屉、splitter handle、tab pane、表格外框和滚动区边界颜色。
- 状态栏密度：状态栏拆分为左侧问题入口、中间项目上下文、右侧状态信息三组，并增加组内 padding、间距和低对比分隔。
- 问题入口：新增靠左 `IssueSummaryWidget`，以图标加 `错误 / 警告` 数量展示摘要，点击打开底部诊断抽屉问题页。
- 工具图标：重绘 `undo.svg` 和 `redo.svg` 为 24px viewBox、1.8px 线宽、round cap/join 的扁平左右箭头，并同步更新内置 fallback。
- 自动化覆盖：新增状态栏分组/问题摘要测试、Dark 主题边界 token 测试和撤销/重做 SVG 路径测试。
- 截图证据：[第四批次 Dark 状态栏与诊断抽屉预览](./previews/fourth-batch-dark-status-drawer.png)。

#### 6.5.2 第四批次验收记录

- 验收时间：2026-05-23。
- 验收方式：人工 UI 复核与用户确认。
- 总体结论：第四批次问题基本验收通过，`B4-001` 到 `B4-004` 均可关闭。

### 6.6 第五批次：提示弹窗与 UI 技术治理评估

- 来源：人工 UI 复核截图与用户对反复主题问题的架构性追问。
- 范围：提示弹窗样式、系统 QMessageBox 默认样式、PySide6/QSS 技术路线适配性、后续 UI 主题治理方案。
- 当前状态：已验收并关闭。
- 当前会话角色：测试角色。本批次经人工确认验收通过，当前会话仅执行验收归档。

| ID | 阶段 | 级别 | 问题 | 原因分析 | 影响 | 完整修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B5-001 | Phase 1 | P2 | 提示弹窗不符合项目 UI 规范。 | 当前失败提示弹窗仍使用接近系统默认的 `QMessageBox` 风格：浅色背景、默认警告图标、默认按钮样式和项目 Dark 主题不一致；弹窗内部文字对比也偏弱。 | 弹窗作为高频错误反馈入口，会直接破坏整体主题一致性；用户在 Dark 主题下看到浅色系统弹窗，会感到界面割裂。 | 不再直接使用裸 `QMessageBox` 作为最终 UI。新增统一弹窗组件或 Dialog 服务，例如 `XDialog`/`MessageDialog`，统一标题、图标、正文、按钮、间距、圆角、主题 token 和焦点态；所有错误、警告、确认提示都通过该服务创建。补充 Light/Dark 弹窗截图验收。 | 已关闭 |
| B5-002 | Phase 0/1 | P1 | UI 主题问题反复出现，说明当前 UI 技术治理不足。 | PySide6/Qt 本身适合桌面工具，但当前实现过度依赖零散 QSS 和默认 Qt 控件；Qt 复合控件存在大量子控件和平台默认样式，若没有设计系统、组件封装和截图验收，很容易漏掉弹窗、tab、splitter、table、statusbar 等细节。问题根因不是 PySide6 完全不合适，而是“直接拼 Qt 控件 + 局部补 QSS”的方式不适合持续做统一主题产品。 | 后续每新增一个 Qt 控件都可能再次出现 Dark/Light 不一致、默认系统样式露出、图标风格不统一等问题，评估批次会不断被 UI 细节拖慢。 | 保留 PySide6 作为当前 MVP 技术路线，但必须升级 UI 工程方式：建立设计 token、统一组件库、禁止裸用系统 dialog、禁止业务界面直接创建未封装复杂控件、建立 Light/Dark 截图回归。若未来 UI 复杂度显著上升，可评估 Qt Quick/QML 或 Web UI/Tauri/Electron，但当前阶段优先治理现有 PySide6 架构。 | 已关闭 |

#### 6.6.1 技术路线分析

当前问题不建议简单归因为“PySide6 技术选型错误”。PySide6/Qt 适合本项目这类桌面配置编辑器，优势是原生桌面能力、文件系统集成、表格/模型视图能力和跨平台打包路径清晰。真正反复出问题的是 UI 工程策略：默认控件直接暴露、QSS 覆盖零散、复合控件子区域漏管、图标和弹窗没有统一组件边界。

继续使用 PySide6 的前提是必须引入更强的 UI 治理：

- 建立 `design tokens -> component styles -> widgets` 的三层结构，业务代码不能直接写颜色、边框、间距和临时图标。
- 对所有高风险 Qt 控件建立封装：弹窗、状态栏、工具栏按钮、诊断抽屉、表格、页签、输入框和菜单。
- 禁止裸用 `QMessageBox`、默认 `QDialogButtonBox`、默认系统图标和未注册 icon id。
- 所有新增 UI 组件必须提供 Light/Dark 双主题截图或人工验收记录。
- 对关键窗口建立截图回归清单：主窗口、诊断抽屉、错误弹窗、确认弹窗、项目新建/打开弹窗。
- 每个评估批次如发现同类主题问题，必须更新 [UI 实现质量规范](./ui-implementation-guidelines.md)。

可选替代路线：

| 方案 | 优点 | 风险 | 建议 |
| --- | --- | --- | --- |
| 继续 PySide6 + 自建组件规范 | 保留现有代码和桌面能力，修复成本最低。 | 需要严格封装控件和截图验收，否则会继续漏样式。 | 当前推荐。 |
| 切换 Qt Quick/QML | 主题和组件状态更适合声明式 UI，视觉一致性更好。 | 需要重写较多 UI，Python/QML 边界和表格复杂度需要重新验证。 | 中期可评估，不建议当前立即切换。 |
| 切换 Web UI/Tauri/Electron | CSS/组件生态强，设计系统和截图回归成熟。 | 桌面文件系统、性能、打包体积和 Python 后端集成成本上升。 | 仅当后续 UI 复杂度远超 Qt Widgets 时再评估。 |

#### 6.6.2 第五批次修复记录

- 统一弹窗：新增 `MessageDialog`，封装错误提示标题、正文、图标区域、按钮区、主题样式和焦点态。
- Dialog 服务：`ProjectDialogs.show_error()` 改为通过 `create_error_dialog()` 创建项目弹窗，不再裸用 `QMessageBox`。
- 主题治理：主题 token 增加 `dialog_bg`、`dialog_button_bg`、`danger`，QSS 覆盖 `QDialog#xtable-message-dialog`、图标区、标题、正文和按钮。
- 规范沉淀：更新 [UI 实现质量规范](./ui-implementation-guidelines.md)，明确禁止裸用系统弹窗、复杂控件必须封装、Light/Dark 截图验收。
- 自动化覆盖：新增弹窗组件、Dialog 服务、主题选择器和 UI 层禁止 `QMessageBox` 的回归测试。
- 截图证据：[Light 弹窗预览](./previews/fifth-batch-message-dialog-light.png)、[Dark 弹窗预览](./previews/fifth-batch-message-dialog-dark.png)。

#### 6.6.3 第五批次验收记录

- 验收时间：2026-05-24。
- 验收方式：人工确认和文档复核。
- 总体结论：第五批次问题验收通过，`B5-001`、`B5-002` 均可关闭。后续更大的 UI 治理目标已转入 [Editor UI Demo 规划](./editor-ui-demo-plan.md)。

### 6.7 Phase 1.5：Editor UI Demo 与 UI Kit 基座实现记录

- 来源：用户确认启动 Phase 1.5，要求保证 UI 模块完整、独立，并明确后续新 UI 需求先由 UI 模块实现再给其他模块调用。
- 范围：UI Kit 组件包、编辑器 Shell、独立 Demo、主程序 Demo 入口、架构边界测试、Light/Dark 截图证据。
- 当前状态：已完成开发实现，等待人工验收。
- 当前会话角色：开发角色。

#### 6.7.1 实现内容

- 组件包：新增 `xtable.ui.components`，包含 `IconToolButton`、`NavigationRail`、`EditorToolbar`、`PreviewTable`、`FieldInspector`。
- Shell：新增 `EditorShell`，统一菜单、工具栏、侧栏、工作区、状态栏和底部诊断抽屉组合方式。
- Demo：新增 `UiKitDemoWindow` 和 `create_demo_window()`，支持 `python -m xtable.ui.demo` 独立启动。
- 主程序入口：帮助菜单新增 `action-open-ui-kit-demo`，可从主窗口打开 UI Kit Demo。
- 弹窗：新增 `ConfirmDialog`，用于确认/取消等严谨决策场景。
- 主题：补充表格状态、字段面板、输入控件、下拉框、复选框和文本编辑控件主题覆盖。
- 治理：更新 [UI 实现质量规范](./ui-implementation-guidelines.md)，明确新 UI 需求必须先进入 `xtable.ui`。

#### 6.7.2 验收证据

- 自动化测试：`python -m pytest` 通过，46 项测试全部通过。
- 架构测试：`application`、`domain`、`io`、`validation` 均不得 import `PySide6`。
- 截图证据：[Phase 1.5 Light Demo](./previews/phase-1-5-ui-kit-demo-light.png)、[Phase 1.5 Dark Demo](./previews/phase-1-5-ui-kit-demo-dark.png)。

#### 6.7.3 后续要求

- 后续 Table、Enum、Meta、校验、导入导出等新 UI 需求，必须先进入 `xtable.ui.components`、`xtable.ui.shell` 或同级 UI 模块。
- `app` 负责启动和服务注入，不直接拼复杂 UI。
- 非 UI 模块只提供数据、状态、错误和回调，不创建 Qt 控件。

#### 6.7.4 Phase 1.5 验收评估

- 验收时间：2026-05-24。
- 验收角色：测试角色。
- 验收方式：文档审查、代码结构审查、自动化测试、Light/Dark 截图审查。
- 自动化结果：`python -m pytest` 通过，46 项测试全部通过。
- 总体完成度：约 82%。Phase 1.5 已完成 UI Kit 基座和独立 Demo 的最小闭环，但距离“完整编辑器 UI Demo”和“随意组合、窗口自由”的目标仍有差距，建议标记为“基础通过，进入增强整改”。

| 维度 | 完成度 | 验收结论 |
| --- | --- | --- |
| 独立 Demo 入口 | 90% | `python -m xtable.ui.demo` 和主程序入口已具备，Demo 可独立展示 UI Shell。 |
| UI Kit 模块边界 | 80% | 已有 `xtable.ui.components`、`EditorShell`、组件测试和架构测试；但目录仍未完全按规划拆成 `kit/`、`demo/pages/` 等更清晰层级。 |
| 主题系统 | 85% | Light/Dark 主体覆盖良好，弹窗、表格、字段面板、诊断抽屉均有样式；但截图中中文字体显示为方框，截图验收仍需字体/渲染环境治理。 |
| 组件覆盖 | 65% | 已覆盖按钮、导航、工具栏、状态栏、诊断抽屉、表格样板、字段面板、弹窗；但 Json/List/Meta 编辑入口、搜索/筛选、布局页、Theme Lab、Dialog 专页等规划页面尚未独立完成。 |
| Demo 可交互性 | 60% | 当前 Demo 主要是静态样板，可切换主题和页面；缺少可手动切换错误/警告数量、弹窗类型、抽屉高度、表格状态、字段状态的控制区。 |
| 验收证据 | 80% | 46 项自动化测试和 Light/Dark 截图已提供；但截图中的中文方框会影响人工验收质量，需要补真实窗口或字体可用环境截图。 |
| 后续复用约束 | 85% | 文档已明确新 UI 必须先进入 `xtable.ui`，非 UI 模块不得创建 Qt 控件；后续还需把该规则加入开发验收门禁。 |

本次发现的问题归档为第六批次，作为 Phase 1.5 的增强整改目标。

### 6.8 第六批次：Phase 1.5 UI Kit Demo 完整度与可复用性评估

- 来源：Phase 1.5 整体方案完成度验收。
- 范围：Demo 页面完整度、组件覆盖、可交互状态、截图验收质量、统一弹窗覆盖率、模块文档和后续复用门禁。
- 当前状态：已验收并关闭。
- 当前会话角色：测试角色。用户已确认上一批次可先关闭，当前会话仅执行验收归档和新批次问题记录。

| ID | 阶段 | 级别 | 问题 | 原因分析 | 影响 | 完整修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B6-001 | Phase 1.5 | P2 | UIDemo 页面数量和规划不完全匹配。 | 规划要求 Overview、Theme Lab、Buttons & Icons、Dialogs、Status Bar、Diagnostics、Tables、Forms、Layouts 等页面；当前 Demo 主要按 Table/Enum/Meta 三个业务入口展示，覆盖面偏像业务壳样板。 | 后续开发者难以在单独页面快速检查某类组件的所有状态，UI Kit 作为组件实验室的价值不足。 | 将 Demo 从业务导航扩展为组件实验室导航，至少补齐 `Overview`、`Theme Lab`、`Buttons & Icons`、`Dialogs`、`Diagnostics`、`Tables`、`Forms`、`Layouts` 页面；Table/Enum/Meta 可作为业务组合示例保留。 | 已关闭 |
| B6-002 | Phase 1.5 | P2 | Demo 缺少足够的状态切换控制。 | 当前 Demo 主要展示静态假数据，只有主题切换和页面切换；问题数量、弹窗类型、字段状态、表格单元格状态、抽屉高度等关键状态不能在 Demo 内手动切换。 | UI 问题仍可能等到业务功能接入后才暴露，无法在 UI Kit 阶段充分验证组合状态。 | 增加 Demo 控制区：切换 Light/Dark、错误/警告/信息数量、打开不同弹窗、切换抽屉页签与高度、切换表格 error/warn/readonly/dirty 状态、切换字段 valid/invalid/disabled 状态。 | 已关闭 |
| B6-003 | Phase 1.5 | P2 | 字段编辑入口覆盖不足。 | 当前 `FieldInspector` 覆盖文本、下拉、复选框、默认值和说明；规划中的 EnumPicker、ReferencePicker、JsonEditorShell、ListEditorShell、MetaEditorShell 仍未形成独立样板。 | Phase 3/6 进入真实字段编辑时仍可能临时拼控件，引发新的主题和布局返工。 | 新增字段编辑组件样板：Enum、Reference、Json、List、Meta 至少各有一个 Shell/入口组件，支持 normal、invalid、readonly/disabled、empty 状态展示。 | 已关闭 |
| B6-004 | Phase 1.5 | P2 | 截图验收存在中文字体方框风险。 | 源码和测试字符串为 UTF-8 正常，但当前 Light/Dark offscreen 截图中中文显示为方框，可能是 CI/offscreen 环境缺少中文字体或 Qt 字体 fallback 未配置。 | 人工验收截图无法真实反映中文 UI 质量；如果打包环境也缺字体，会影响最终用户体验。 | 明确 UI 字体策略：优先使用系统中文可用字体并设置 fallback；截图生成环境需要安装或指定中文字体。新增至少一组真实窗口或字体可用环境截图作为验收证据。 | 已关闭 |
| B6-005 | Phase 1.5 | P3 | UI Kit 内部功能文档还不够组件化。 | 已有总体规划、设计和实现记录，但每个组件尚未有独立说明其用途、状态、主题 token、objectName、验收点和复用限制。 | 后续开发角色复用组件时仍需要读源码，容易绕过组件或误用组件。 | 新增 `docs/ui-kit-components.md` 或 `docs/ui-kit/` 文档目录，逐个记录 `EditorShell`、`EditorToolbar`、`NavigationRail`、`BottomStatusBar`、`DiagnosticDrawer`、`MessageDialog`、`PreviewTable`、`FieldInspector` 等组件说明。 | 已关闭 |
| B6-006 | Phase 1.5 | P2 | “新 UI 需求必须先进入 UI 模块”的规则尚未形成强验收门禁。 | 当前已有文档和架构测试，能防止非 UI 模块 import PySide6，但不能阻止业务 UI 直接绕过 UI Kit 创建复杂控件。 | 后续业务阶段仍可能因为赶进度直接创建裸 Qt 复合控件，导致 UI Kit 治理失效。 | 增加验收规则：Phase 3 起新增 UI 必须引用 UI Kit 组件或先补 UI Kit 组件；评估文档中增加“UI Kit 复用检查”；可在测试中扫描 `app/`、业务 UI 文件是否直接创建高风险裸控件。 | 已关闭 |
| B6-007 | Phase 1.5 | P2 | 测试过程中发现仍存在不符合主题的提示/确认弹窗。 | 截图中的“覆盖文件”确认弹窗出现浅色背景、系统标题栏/边框、项目主题不一致的按钮和文本对比，说明统一 `MessageDialog`/`ConfirmDialog` 没有覆盖所有弹窗调用路径，或部分确认类弹窗仍使用默认 `QDialog`/`QMessageBox`/系统样式。 | 这会再次破坏 Dark 主题一致性，也说明第五批次“禁止裸用系统弹窗”的治理还没有形成完整闭环；后续导入导出、覆盖确认、删除确认等高频流程会反复暴露同类问题。 | 开发角色需要全量排查 UI 层所有弹窗入口，尤其是覆盖文件、保存失败、导出确认、删除确认、退出确认等确认类弹窗。所有提示/确认/输入弹窗必须通过统一 Dialog 服务创建，并纳入 Dialog Demo 页面；新增测试扫描 UI 层禁止裸用 `QMessageBox`、默认 `QDialogButtonBox` 直接裸露最终样式，以及确认弹窗 Light/Dark 截图验收。 | 已关闭 |
| B6-008 | Phase 1.5 | P2 | UI 层仍直接使用 `QFileDialog` 和 `QInputDialog`，未纳入统一 Dialog 服务或明确例外。 | 静态扫描发现 `ProjectDialogs` 仍直接调用 `QFileDialog.getExistingDirectory()` 和 `QInputDialog.getText()`。这些原生/系统弹窗通常不受项目主题完整控制，也没有进入 Dialog Demo 验收。 | 项目创建、打开、输入信息等高频流程可能继续出现系统默认弹窗，导致主题割裂；也会削弱“禁止裸用系统弹窗”的治理效果。 | 将文件选择、目录选择和简单输入纳入统一 Dialog 服务治理。短期可先建立 `ProjectDirectoryDialog`、`TextInputDialog` 的项目风格封装；如果必须使用原生文件选择器，需要在规范中明确例外、使用场景和截图验收要求。 | 已关闭 |
| B6-009 | Phase 1.5 | P3 | 状态栏中存在遗留 `IssueStatusButton`，未显示但仍被创建和更新。 | 当前 `EditorStatusBar` 已使用 `IssueSummaryWidget` 作为靠左问题入口，但代码仍创建 `IssueStatusButton` 并在 `update_issue_summary()` 中更新它，却没有将其加入状态栏布局。 | 这会增加维护者理解成本，也可能导致后续测试或业务代码误用旧入口；属于 UI 组件演进后的死代码/双入口风险。 | 删除或迁移旧 `IssueStatusButton`。若保留作为兼容别名，必须文档说明用途并禁止业务直接引用；推荐只保留 `IssueSummaryWidget` 一个高频入口。 | 已关闭 |

#### 6.8.1 控件级功能测试记录

- 测试时间：2026-05-24。
- 测试角色：测试角色。
- 测试方式：现有自动化测试、Python 编译检查、静态扫描、Qt offscreen 临时运行时控件交互脚本。
- 自动化结果：`python -m pytest` 通过，51 项测试全部通过。
- 编译检查：`python -m compileall -q src tests` 通过。
- 控件交互结果：状态栏问题摘要、导航按钮、诊断抽屉页签、表格选择、字段文本输入、字段下拉选择、必填复选框、说明文本编辑、错误弹窗和确认弹窗均可正常交互。
- 静态扫描发现：`QFileDialog`、`QInputDialog` 仍直接出现在 `src/xtable/ui/dialogs.py`；`IssueStatusButton` 仍在 `EditorStatusBar` 中创建和更新但不显示。
- 结论：当前已存在的 Demo 控件基础交互可用，代码能通过现有测试；用户已确认上一批次可先关闭，后续新增问题另归档为第七批次。

#### 6.8.2 第六批次修复记录

- Demo 页面：UI Kit Demo 已扩展为组件实验室导航，包含 Overview、Theme Lab、Buttons & Icons、Dialogs、Diagnostics、Tables、Forms、Layouts，并保留 Table/Enum/Meta 业务组合示例。
- 状态控制：新增 `demo-control-panel`，可调错误/警告/信息数量、诊断抽屉高度、表格状态和字段状态。
- 字段编辑：新增 `PickerShell`、`JsonEditorShell`、`ListEditorShell`、`MetaEditorShell`，覆盖 Enum、Reference、Json、List、Meta 的入口样板和状态。
- 字体策略：`configure_ui_font()` 优先加载 Windows 中文字体文件并配置中文字体 fallback；UI 规范明确截图验收必须使用可显示中文字体的环境。当前 offscreen 环境 `QFontDatabase` 未枚举到字体，最终人工截图需在真实字体环境复验。
- 组件文档：新增 [UI Kit 组件说明](./ui-kit-components.md)，记录组件用途、状态、objectName 和复用限制。
- 门禁测试：新增 app 层高风险 Qt 控件扫描，禁止绕过 UI Kit 直接创建裸 `QMessageBox`、`QDialog`、`QTableWidget`、`QTabWidget`、`QSplitter` 等复杂控件。
- 弹窗闭环：确认弹窗纳入 Dialog Demo 页面和主题选择器，`ConfirmDialog` 样式覆盖 `QDialog#xtable-confirm-dialog`。
- 截图证据：[第六批 Light Demo](./previews/sixth-batch-ui-kit-demo-light.png)、[第六批 Dark Demo](./previews/sixth-batch-ui-kit-demo-dark.png)、[第六批 Dark ConfirmDialog](./previews/sixth-batch-confirm-dialog-dark.png)。

#### 6.8.3 第六批次验收记录

- 验收时间：2026-05-24。
- 验收方式：人工体验复核与用户确认。
- 验收结论：上一批次问题可先关闭，控件主题适配没有明显问题；`B6-001` 至 `B6-009` 标记为已关闭。

### 6.9 第七批次：输入焦点、表格能力、多窗口与编辑控件交互评估

- 来源：人工体验测试和截图反馈。
- 范围：输入激活/失活管理、表格核心编辑能力、多窗口/多页签体验、Json 编辑体验、表格滚动、下拉状态按钮、Light 主题选中态、只读/展示控件识别和数据列表展示。
- 当前状态：二次复验通过，可关闭。
- 当前会话角色：测试角色。当前会话只执行复验、问题归档和文档更新，实际实现由开发角色执行。

| ID | 阶段 | 级别 | 问题 | 原因分析 | 影响 | 完整修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B7-001 | Phase 1.5 | P1 | 输入框缺少全局激活/失活管理，当前激活输入框全局应该只有一个。 | 现有 Demo 更偏组件静态展示，输入控件各自依赖 Qt 默认 focus 行为，缺少统一的编辑器激活状态管理和 active editor 注册机制。 | 多个输入区可能同时呈现激活感，提交、取消、校验和快捷键归属会变得不确定，后续表格单元格编辑和属性面板编辑容易互相抢焦点。 | 新增全局 `EditorFocusManager` 或 `InputActivationController`：维护唯一 active editor，提供 activate、deactivate、commit、cancel、focusChanged 信号；所有文本框、Json 编辑器、表格单元格编辑器和弹窗输入框必须接入。增加测试覆盖“新输入框激活时旧输入框失活”。 | 已关闭 |
| B7-002 | Phase 1.5 | P1 | 当不在输入操作时，如点击其他按钮或空白操作区域，输入框应该主动失活。 | 当前缺少应用级 click-outside/event filter 规则，按钮、工具栏、空白工作区和抽屉区域没有统一通知输入管理器退出编辑态。 | 用户会感觉输入框一直占用状态，快捷键、按钮命令和表格选择行为容易出现冲突。 | 在 `EditorShell` 或 UI Kit 根节点增加事件过滤器：点击非输入控件、工具栏按钮、导航按钮、空白工作区时调用 active editor 的 commit/blur；弹窗、下拉列表和文本选择等合法输入交互需要加入白名单，避免误失活。 | 已关闭 |
| B7-003 | Phase 1.5 | P1 | Demo 只有表格数据展示，不能体现表格核心支持能力，例如批量编辑、粘贴。 | 当前 `PreviewTable` 更像展示样板，尚未建立表格编辑组件的交互契约；批量填充、粘贴解析、选区写入和撤销命令未在 UI Kit 层暴露。 | 无法判断后续 Phase 3 是否能稳定承载真实表格编辑；如果这些能力全部推迟到业务层，容易绕过 UI Kit 重新拼表格逻辑。 | 把表格基础交互能力定义为 UI Kit/表格组件自带能力：选区、复制、粘贴、批量填充、只读保护、错误态展示、编辑提交/撤销接口。Demo 使用假数据模型展示粘贴多行多列、批量编辑和非法单元格拒绝写入；业务层只注入模型和命令处理。 | 已关闭 |
| B7-004 | Phase 1.5 | P2 | 没有体验到活动窗口、多页签窗口等功能，不能判断是否支持同时打开多个表格、自由切换。 | 当前 Demo 主要展示单一 Shell 和组件页面，缺少 `WorkspaceTabs`、active document、dirty state、close/switch 等编辑器工作区能力。 | 后续多表格、多 Enum、多 Meta 同时打开时，焦点、保存状态、问题归属和状态栏上下文可能缺少统一模型。 | 新增工作区窗口/页签 Demo：支持打开多个模拟表格/配置页，显示 active tab、dirty 标记、关闭确认、页签切换和状态栏上下文更新；明确 UI Kit 提供页签容器，业务层提供文档模型。 | 已关闭 |
| B7-005 | Phase 1.5 | P2 | Json 编辑框没有正常 Json 编辑体验，目前还是单纯文本编辑框。 | `JsonEditorShell` 目前偏包装样板，未具备 Json 特有的格式化、校验、错误定位、结构提示和行列信息。 | Json 字段后续会成为真实数据类型能力，如果仍按普通文本框处理，用户无法高效修复格式错误，也难以验证主题和错误态。 | 将 Json 编辑器升级为独立组件：等宽字体、行号/行列状态、格式化、校验、错误定位、结构提示和行列信息。 | 已关闭 |
| B7-006 | Phase 1.5 | P2 | 表格区滑动条控制不自然，不能无级调节。 | 表格滚动仍可能使用默认 item/step 滚动或样式未针对编辑器场景调校，Demo 数据量和视口也不足以验证连续滚动体验。 | 大表格编辑时横向/纵向定位会不顺手，影响核心编辑体验。 | 表格组件启用像素级滚动和连续滚动策略，统一滚动条尺寸、hover/drag 状态和滚轮步进；Demo 提供足够大数据集验证水平/垂直滚动、拖拽滑块和触控板滚动。 | 已关闭 |
| B7-007 | Phase 1.5 | P3 | 下拉框左侧应该是状态按钮，目前为空。 | 下拉控件的 leading/status slot 没有按状态填充图标按钮，normal/invalid/readonly/disabled 等状态只体现在文本或边框上。 | 状态表达不完整，用户难以快速识别字段状态；截图中左侧空位也显得像渲染缺失。 | 为 Combo/Picker 类组件增加统一 status leading button：normal、invalid、readonly、disabled 使用主题化图标和 tooltip；若无状态按钮需求则不保留空槽。Light/Dark 和各状态都需要截图验收。 | 已关闭 |
| B7-008 | Phase 1.5 | P2 | Light 主题文本选中时内容看不清。 | 选中态 token 未覆盖表格单元格、输入框文本选择和编辑态文字，当前 selection 背景与文字颜色对比不足。 | 直接影响可读性和编辑可信度，尤其在复制、批量选择、表格编辑时高频出现。 | 增加统一 selection token：`selection_bg`、`selection_text`、`selection_border`、`selection_inactive_bg`；覆盖表格选中、输入框文本选中、下拉列表选中和只读选中态，并用 Light/Dark 截图验证对比度。 | 已关闭 |
| B7-009 | Phase 1.5 | P2 | 很多控件看着像输入框，实际没有输入功能。 | 只读展示、占位容器和真实可编辑输入框视觉层级过于接近，未通过边框、背景、光标、hover/focus 行为区分 editable、readonly、display-only。 | 用户会误以为可以输入，测试也难以判断控件功能是否完整；后续业务接入容易产生交互歧义。 | 建立输入控件状态规范：editable 才显示可输入光标和强 focus ring；readonly/display-only 使用弱边框或纯文本展示；禁用态降低对比但保持可读。Demo 对每类控件标注真实交互能力并提供可点击验证。 | 已关闭 |
| B7-010 | Phase 1.5 | P2 | 没有展示数据列表，需明确是否应该支持。 | 当前 Demo 覆盖表格、字段、诊断等组件，但缺少项目资源列表、表列表、枚举列表、数据元列表等 list/navigation 类组件样板。 | 后续项目资源管理、打开多表格、选择引用目标和数据元管理都需要列表组件，如果不在 UI Kit 先定义，会重复出现临时列表 UI。 | 新增 `DataListView`/`ResourceList` 组件样板：支持空状态、加载状态、筛选、选择、键盘导航、状态徽标、脏标记和上下文操作；Demo 至少展示表格列表、字段列表或数据元列表一种真实组合。 | 已关闭 |

#### 6.9.1 第七批次修复记录

- 焦点管理：新增 `EditorFocusManager` 和 `ManagedLineEdit`，提供唯一 active editor、激活切换和外部点击失活契约。
- 表格交互：`PreviewTable` 支持 TSV 粘贴、选区批量填充、只读保护、dirty/error/warning 状态和像素级滚动。
- 多页签：新增 `WorkspaceTabs`，展示 active document、dirty 标记、关闭确认和页签切换。
- Json 编辑：`JsonEditorShell` 增加等宽编辑区、格式化、压缩、校验、错误行列提示和 valid/invalid 状态。
- 下拉状态：`PickerShell` 增加 leading status button，normal/invalid/readonly/disabled 通过主题图标和 tooltip 表达。
- Light 选中态：主题新增 `selection_bg`、`selection_text`、`selection_border`、`selection_inactive_bg`，覆盖表格、输入框、文本框和下拉列表选中态。
- 输入状态区分：主题补充 active editor、readonly/display-only、field-state 样式，降低“看着像输入框但不可输入”的误导。
- 数据列表：新增 `DataListView`，支持筛选、选择、loading、empty 和状态标记；Demo 诊断/枚举页面接入示例。
- Demo 接入：Forms、Tables、Layouts、Diagnostics、Meta 页面已展示字段编辑 Shell、大表格滚动、多文档页签、数据列表和 Json 编辑器。
- 截图证据：[工作区页签](./previews/seventh-batch-workspace-tabs-dark.png)、[字段编辑器](./previews/seventh-batch-field-editors-dark.png)、[可编辑表格](./previews/seventh-batch-editable-table-dark.png)、[数据列表](./previews/seventh-batch-data-list-dark.png)。

#### 6.9.2 第七批次复验记录

- 复验时间：2026-05-24。
- 复验角色：测试角色。
- 自动化结果：`python -m pytest` 通过，58 项测试全部通过。
- 编译检查：`python -m compileall -q src tests` 通过。
- 运行时复验脚本结果：`B7-003`、`B7-004`、`B7-005`、`B7-006`、`B7-007`、`B7-008`、`B7-010` 基础能力通过；`B7-001`、`B7-002`、`B7-009` 失败。
- `B7-001` 未通过证据：Demo 窗口没有全局 `focus_manager`，`field-name-input` 与 `field-default-input` 的 `active-editor` 属性均为 `None`；`EditorFocusManager` 和 `ManagedLineEdit` 目前只在孤立测试中使用，没有接入实际 `FieldInspector`、`JsonEditorShell`、表格编辑器或 `EditorShell`。
- `B7-002` 未通过证据：运行时将焦点放到 `field-name-input` 后切换页面，`QApplication.focusWidget()` 仍指向 `field-name-input`；未观察到由按钮/空白区域/页面切换触发的统一失活逻辑。
- `B7-003` 部分通过证据：`PreviewTable.paste_tsv()`、`batch_fill()`、只读保护和 dirty 标记可用；但未发现 `keyPressEvent`、剪贴板 `Ctrl+V`、复制或批量编辑 UI 入口，仍不算完整表格编辑体验。
- `B7-005` 部分通过证据：`JsonEditorShell` 已支持校验、格式化、压缩和错误行列提示；但 Demo 中未提供格式化/压缩/校验按钮，状态栏行列信息未随光标实时更新，仍偏 API 能力而非完整编辑体验。
- `B7-009` 未通过证据：运行时未找到任何 `QLineEdit`/`QTextEdit` 设置 `display-mode="readonly"` 或 `setReadOnly(True)`；主题中存在 readonly/display-only 样式，但实际控件未接入，用户仍难以区分“看起来像输入框但不可输入”的区域。
- 结论：第七批次不能标记为已验收关闭。建议开发角色优先处理 `B7-001`、`B7-002`、`B7-009`，随后补齐 `B7-003` 的真实剪贴板/快捷键路径和 `B7-005` 的可见 Json 编辑工具栏。

#### 6.9.3 第七批次二次整改记录

- 焦点运行时接入：`EditorShell` 已创建全局 `focus_manager`，并通过 `EditorFocusEventFilter` 将 Demo 中的 `QLineEdit`、`QTextEdit` 接入唯一 active editor 状态；页面切换会主动失活。
- 外部失活：事件过滤器监听非输入区域点击，调用 `deactivate_active(reason="outside-click")`，用于工具栏、导航、空白区域等非编辑操作。
- 表格交互入口：`PreviewTable` 新增 `keyPressEvent`，支持 `Ctrl+C` 复制选区和 `Ctrl+V` 粘贴 TSV；Tables Demo 增加复制、粘贴、批量填充图标按钮。
- Json 编辑入口：`JsonEditorShell` 增加校验、格式化、压缩图标按钮，按钮在 Demo 中可见；光标移动时实时刷新行列状态，非法 Json 仍显示错误行列。
- 输入状态区分：`FieldInspector`、`JsonEditorShell`、`MetaEditorShell`、`PickerShell` 和 `ListEditorShell` 接入 `readonly`/`display-mode`，只读控件设置 `setReadOnly(True)` 或禁用选择类控件，并应用弱化样式。
- 回归测试：`tests/test_ui_interactions.py` 增加 Demo 运行时焦点接入、页面切换失活、只读控件接入、表格剪贴板快捷键、可见表格/Json 工具按钮检查。

#### 6.9.4 第七批次二次复验记录

- 复验时间：2026-05-24。
- 复验角色：测试角色。
- 自动化结果：`python -m pytest` 通过，60 项测试全部通过。
- 编译检查：`python -m compileall -q src tests` 通过。
- 运行时复验脚本结果：`B7-001` 至 `B7-010` 全部通过，失败项为 none。
- 关键复验证据：Demo 窗口已创建全局 `focus_manager`；`field-name-input` 与 `field-default-input` 激活切换时只保留一个 `active-editor=true`；页面切换会触发 `deactivate_active(reason="page-switch")`；外部失活路径可触发 `deactivate_active(reason="outside-click")`。
- 表格复验证据：`PreviewTable` 支持 `Ctrl+V` 粘贴 TSV、`Ctrl+C` 复制选区、批量填充和只读单元格拒绝写入，拒绝原因记录为 `readonly`。
- Json 复验证据：`JsonEditorShell` 已提供校验、格式化、压缩按钮，格式化/压缩/非法 Json 错误提示均可运行；光标移动后行列状态可刷新。
- 输入状态复验证据：`FieldInspector`、`MetaEditorShell` 等只读输入控件已设置 `display-mode="readonly"` 和 `setReadOnly(True)`，与可编辑输入区分成立。
- 结论：第七批次整改通过复验，`B7-001` 至 `B7-010` 可标记为已关闭。后续若进入真实业务编辑阶段，应继续复用本批形成的焦点管理、表格剪贴板、Json 编辑器和 readonly/display-mode 规范。

### 6.10 第八批次：Phase 2 核心数据模型结构校验评估

- 来源：Phase 2 首批开发质量审查。
- 范围：`Table`、`Field`、`Enum`、`Meta`、`ProjectSchema`、字段/表格类型注册表、结构一致性校验和测试覆盖。
- 当前状态：已完成开发修复，等待复验。
- 当前会话角色：开发角色。当前会话负责按第八批次修改建议补齐模型结构校验和回归测试。
- 验证结果：`python -m pytest` 通过，66 项测试全部通过；`python -m compileall -q src tests` 通过；额外结构探针测试暴露 6 类非法模型可被注册的问题。
- 总体结论：Phase 2 当前是“核心数据模型骨架可用”，但不能按“核心数据模型完成”验收。主要风险是 `ProjectSchema` 可以进入非法结构状态，后续 Phase 3/4 会被迫处理脏模型。

| ID | 阶段 | 级别 | 问题 | 原因分析 | 影响 | 完整修改建议 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B8-001 | Phase 2 | P1 | `ProjectSchema.add_table()` 不校验字段引用目标是否存在。 | 当前只检查重复 `table_id` 和表内字段唯一性；`ENUM` 字段可以引用不存在的 `enum_id`，`REFERENCE` 字段可以引用不存在的 `target_table_id/target_field_id`，`META` 字段可以引用不存在的 `meta_id`。 | 非法 schema 可以进入项目模型，直到运行期调用 `resolve_field_reference()` 或后续 UI/表格模型使用时才暴露 `KeyError`，会把结构错误推迟到 Phase 3/4。 | 在模型层增加结构级引用校验。`add_table()` 或统一 `validate_structure()` 必须检查字段类型与参数匹配：`ENUM` 必须引用已注册 Enum，`REFERENCE` 必须引用已注册 Table 和目标字段，`META` 必须引用已注册 Meta；缺失时抛出明确结构错误。 | 待复验 |
| B8-002 | Phase 2 | P1 | 表格主键、特征键和表格类型专属参数未校验。 | `primary_key`、`feature_keys`、`GroupTableDefinition.group_key`、`MatrixTableDefinition.x_axis/y_axis/value_field` 只是字符串字段，没有确认是否属于当前表字段，也没有检查二维表三轴是否重复或为空。 | 普通表、分组表和二维表虽然能用统一模型表达，但表达结果可能无效；后续排序、引用预览、分组视图和二维表展开会缺少可信前提。 | 增加表结构校验：普通表主键/特征键必须存在于字段列表；分组表 `group_key` 必须存在；二维表 `x_axis/y_axis/value_field` 必须存在且语义不冲突；对表格类型注册表中的 `required_parameters` 建立自动校验或显式校验方法。 | 待复验 |
| B8-003 | Phase 2 | P1 | Enum 结构规则未完整落地。 | `add_enum()` 只检查重复 `enum_id` 和重复 `item_id`，没有检查重复 `export_value`、`default_item_id` 是否存在、默认项是否废弃。 | 与枚举规格不一致；导出值重复会导致运行时配置歧义，默认项不存在会导致新增行默认值无法稳定生成。 | `add_enum()` 或 `EnumDefinition.validate()` 增加：`export_value` 默认不得重复；`default_item_id` 非空时必须存在；默认项不得为 deprecated；错误信息需要包含 enum_id 和冲突项，方便 UI 定位。 | 待复验 |
| B8-004 | Phase 2 | P1 | Meta 子字段重复名称未校验。 | `add_meta()` 只检查重复 `field_id`，未检查重复 `name`；Table 字段有 `field_names` 唯一检查，但 Meta 未复用同等规则。 | 违反 Meta 子字段与 Table 字段复用同一字段定义能力的规格；导出、复制粘贴和属性面板按字段名访问时会出现歧义。 | 抽出通用字段集合校验函数，同时用于 Table 和 Meta：校验 `field_id`、`name` 唯一，并为 Meta 子字段复用字段类型参数校验。 | 待复验 |
| B8-005 | Phase 2 | P2 | `TableRow` 没有结构约束，非法行数据可进入模型。 | `TableRow.values` 是自由 `dict[str, Any]`，`add_table()` 不检查未知字段、缺少必填字段、明显类型不匹配或只读字段写入来源。 | Phase 2 虽不负责完整业务校验，但核心数据模型无法保证行数据至少匹配表结构；后续编辑、保存、导入导出会面对不可信数据。 | 明确 Phase 2 与 Phase 4 边界：Phase 2 至少提供行结构校验入口，检查未知字段、字段名/字段 id 映射、必填字段缺失和基础类型大类；Phase 4 再负责复杂规则、范围、唯一性、Json 内容等诊断报告。 | 待复验 |
| B8-006 | Phase 2 | P2 | 字段类型参数缺少按类型的契约校验。 | `FieldDefinition` 同时承载 `enum_id`、`target_table_id`、`target_field_id`、`element_type`、`meta_id` 等参数，但没有根据 `field_type` 判断哪些必填、哪些禁止或哪些组合有效。 | 字段定义会出现“类型是 list 但没有 element_type”“类型是 enum 但 enum_id 为空”“基础类型却携带引用参数”等不一致状态，增加 UI 和导入导出分支复杂度。 | 增加 `FieldDefinition.validate_shape()` 或注册表驱动的字段参数校验：基础类型不应携带引用参数；Enum/Reference/List/Meta 必须具备对应参数；Json 字段保留 Json 规则参数扩展点。 | 待复验 |
| B8-007 | Phase 2 | P2 | 测试覆盖偏 happy path，不能证明模型层结构质量。 | `tests/test_phase2_domain_models.py` 主要验证可注册、可解析、重复 ID 拒绝和 Qt 隔离；缺少非法引用、非法表参数、Enum 导出值重复、Meta 字段名重复、行结构错误等失败用例。 | 自动化测试通过容易被误解为 Phase 2 可验收；实际模型层仍能接受多类非法结构。 | 将本批次探针场景加入回归测试：缺失 Enum/Meta/Table 引用、缺失主键/分组键/二维轴字段、重复 `export_value`、默认枚举项不存在、Meta 字段名重复、未知行字段和必填缺失。 | 待复验 |

#### 6.10.1 第八批次修复记录

- 结构引用：`ProjectSchema.add_table()` 已校验 Enum、Reference、Meta 字段引用目标；Reference 支持 `target_table_id` 和可选 `target_field_id` 明确错误。
- 统一复查：新增 `ProjectSchema.validate_structure()`，用于全 schema 注册完成后复查 Enum、Meta、Table 的结构一致性，支持 Meta 先定义、Table 后注册的合法顺序。
- 表参数：普通表 `primary_key`、`feature_keys`、分组表 `group_key`、二维表 `x_axis/y_axis/value_field` 已校验存在性；二维表三轴不能为空且不能重复。
- Enum 规则：`add_enum()` 已校验重复 `item_id`、重复 `export_value`、缺失 `default_item_id` 和默认项 deprecated。
- Meta 规则：Table 和 Meta 复用统一字段集合校验，均检查 `field_id` 与 `name` 唯一；Meta 子字段也执行字段类型参数契约校验。
- 行结构：`add_table()` 已校验未知行字段、必填字段缺失和基础类型大类错误；复杂范围、唯一性、Json 内容等仍保留给 Phase 4 诊断规则。
- 字段契约：新增 `FieldDefinition.validate_shape()`，按 `field_type` 校验 enum/reference/list/meta 必需参数，并禁止基础类型携带引用参数。
- 回归测试：`tests/test_phase2_domain_models.py` 已增加第八批探针场景，覆盖非法引用、非法表参数、Enum/Meta 结构、行结构和字段参数错配。
