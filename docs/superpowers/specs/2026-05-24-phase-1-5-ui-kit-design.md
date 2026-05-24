# Phase 1.5 UI Kit Design

## 1. 背景

Phase 0/1 已完成 XTable 的主窗口骨架、项目文件流程、主题、图标、状态栏、诊断抽屉和统一弹窗雏形。前五批评估反复暴露同一类问题：UI 细节散落在主窗口和局部 QSS 中，默认 Qt 控件样式容易露出，业务界面未来如果继续直接拼控件，会持续产生主题、图标、弹窗和布局一致性返工。

Phase 1.5 的目标是在进入真实业务编辑功能前，先建立独立、完整、可复用、可验收的 UI Kit 和编辑器 Demo。后续 Table、Enum、Meta、校验、导入导出等新 UI 需求，必须先进入 `xtable.ui` 模块实现为组件、页面、Dialog 或 Shell 能力，再由其他模块调用。

## 2. 目标

- 提供独立 UI Demo 入口：`python -m xtable.ui.demo`。
- 在主程序中提供 UI Kit Demo 入口，例如菜单 `帮助 -> 开发预览 -> UI Kit Demo`。
- 建立可复用 UI Kit 组件边界，包含编辑器外壳、工具栏、侧栏、状态栏、诊断抽屉、表格样板、字段面板和弹窗样板。
- 强化主题治理，确保 Light/Dark 覆盖 Dialog、Table、Tab、Splitter、StatusBar、ToolBar、Menu、Input、ScrollArea 等高风险 Qt 控件。
- 固化 UI 职责边界：后续新 UI 需求先由 `xtable.ui` 实现，再给 `app`、`application` 或业务模块调用。
- 提供自动化测试和 Light/Dark 截图证据，作为 Phase 1.5 验收依据。

## 3. 非目标

- 不实现真实 Table/Enum/Meta 业务数据模型。
- 不实现真实保存、导入、导出、校验和日志业务流程。
- 不实现 Phase 3 的单元格编辑、复制粘贴、筛选排序、撤销重做等真实编辑行为。
- 不引入 Qt Quick/QML、Tauri 或 Electron；当前阶段继续治理 PySide6/Qt Widgets 架构。

## 4. 模块拆分

Phase 1.5 后，`xtable.ui` 应从“主窗口实现集合”升级为独立 UI Kit 层。

### 4.1 `xtable.ui.demo`

职责：

- 提供独立 Demo 启动入口。
- 组装 UI Kit 样板窗口。
- 展示 Light/Dark 主题切换、工具栏、侧栏、状态栏、诊断抽屉、表格样板、字段面板、错误弹窗和确认弹窗。
- 使用静态示例数据，不依赖真实项目服务。

### 4.2 `xtable.ui.shell`

职责：

- 提供编辑器外壳组件，例如 `EditorShell`。
- 统一组合菜单、工具栏、左侧导航、中央工作区、右侧或内嵌字段面板、底部诊断抽屉和状态栏。
- 接收外部注入的 action handler 和页面 widget。
- 不直接调用项目保存、导入、校验等业务流程。

对外能力：

- `EditorShell` 接收 action 映射、页面定义和状态更新接口，负责把通用编辑器布局拼装起来。
- `EditorShell.set_workspace_page(key)` 切换中央页面，并同步左侧导航选中态和状态栏当前对象。
- `EditorShell.apply_theme(theme)` 统一刷新窗口 QSS、action 图标、导航图标、弹窗和子组件视觉状态。
- `EditorShell.update_issue_summary(errors, warnings, infos)` 更新状态栏问题摘要，并让诊断抽屉显示对应问题页。
- `EditorShell.open_diagnostics(tab)` 打开底部诊断抽屉并切换 `issues` 或 `logs` 页签。

边界：

- `EditorShell` 不读取项目文件，不保存配置，不生成校验结果。
- `EditorShell` 不直接创建业务表格模型，只接收 UI 页面 widget 或静态 Demo widget。
- 主程序可以继承或组合 `EditorShell`，但业务逻辑必须通过 handler 或服务注入。

### 4.3 `xtable.ui.components`

职责：

- 承载可复用 UI 组件。
- 首批组件包括：
  - `IconToolButton`
  - `NavigationRail`
  - `EditorToolbar`
  - `EditorStatusBar`
  - `DiagnosticsDrawer`
  - `MessageDialog`
  - `ConfirmDialog`
  - `PreviewTable`
  - `FieldInspector`
- 所有复杂 Qt 控件必须先进入组件层封装，再被页面或主窗口使用。

首批组件职责：

| 组件 | 职责 | 不负责 | 关键验收点 |
| --- | --- | --- | --- |
| `IconToolButton` | 提供统一图标按钮尺寸、tooltip、accessibleName、icon-id 和主题刷新接口。 | 不决定业务动作含义，不直接连接业务服务。 | 图标来自 `icon_for`，Light/Dark 可读，文本不直接显示在按钮上。 |
| `NavigationRail` | 承载 Table/Enum/Meta 等主导航入口，管理选中态和页面切换信号。 | 不创建中央页面内容，不读取业务模型。 | 固定宽度、稳定 objectName、图标尺寸统一、选中态明确。 |
| `EditorToolbar` | 组合高频 action 图标按钮、分组 separator、右侧全局入口。 | 不直接实现保存、导入、校验等动作。 | action 有 icon-id、tooltip、菜单与工具栏语义一致。 |
| `EditorStatusBar` | 展示问题摘要、项目上下文、当前对象、保存状态、校验状态和后台任务。 | 不计算问题数量，不执行校验。 | 左侧问题入口、中间上下文、右侧状态分组清晰。 |
| `DiagnosticsDrawer` | 统一承载问题、日志和诊断信息页签，支持底部展开和高度调整。 | 不生成日志内容，不执行问题定位。 | 底部抽屉、可切页、可调高度、Dark 无浅色露出。 |
| `MessageDialog` | 展示错误、警告、信息类提示，统一标题、正文、图标和按钮样式。 | 不做复杂确认分支。 | 替代裸 `QMessageBox`，Light/Dark 一致。 |
| `ConfirmDialog` | 展示需要用户严谨决策的确认/取消弹窗。 | 不承载普通提示信息。 | 使用明确文本按钮，默认焦点和取消路径清晰。 |
| `PreviewTable` | 展示表格 UI 样板，包括表头、单元格、只读、错误、警告和选中态。 | 不实现真实 `QAbstractTableModel`，不保存单元格编辑。 | 表格、header、corner、selection、grid、scrollbar 都有主题覆盖。 |
| `FieldInspector` | 展示字段属性编辑面板样板，如字段名、类型、必填、默认值、说明。 | 不校验真实字段规则，不写回领域模型。 | 输入控件、下拉框、复选框、分组标题和说明在双主题下可读。 |

组件 API 原则：

- 组件构造参数只接收显示配置、静态示例数据、回调函数或轻量 view model。
- 组件对外暴露明确方法，例如 `apply_theme(theme)`、`set_items(items)`、`set_status(...)`。
- 组件内部可以使用 PySide6，组件外的非 UI 模块不能 import PySide6。
- 组件必须设置稳定 objectName，供自动化测试和截图验收定位。

### 4.4 `xtable.ui.theme`

职责：

- 继续作为设计 token 和 QSS 生成入口。
- Phase 1.5 需要把 token 按用途分组：基础色、文本、边界、状态、组件。
- 业务 UI 不得直接写颜色、边框、圆角或临时样式。

需要覆盖的组件级 token：

- Shell：窗口背景、工作区背景、面板背景、主分隔线、弱分隔线。
- Toolbar/Menu：工具栏背景、菜单背景、hover、pressed、disabled。
- Navigation：导航按钮普通、hover、checked、图标颜色。
- StatusBar：分组分隔、问题摘要、上下文字段、弱文本。
- Diagnostics：抽屉边界、splitter handle、tab、表格、日志区域。
- Dialog：弹窗背景、图标容器、标题、正文、按钮、焦点态。
- Form/Input：输入框、下拉框、复选框、说明文本、禁用态。
- Table：表头、corner、grid、selection、readonly、error、warning。

### 4.5 `xtable.ui.actions`

职责：

- 继续管理 action id、icon id、tooltip、菜单归属和快捷键。
- Demo 和主窗口复用 action 定义。
- action handler 由调用方注入。

Action 定义必须包含：

- `action_id`：稳定对象名，例如 `action-save-project`。
- `label`：菜单文字。
- `icon_id`：统一图标 id。
- `tooltip`：工具栏和辅助说明。
- `menu`：所属菜单。
- `shortcut`：可选快捷键。
- `toolbar_group`：可选工具栏分组，用于 `EditorToolbar` 自动布局。

调用方只提供 handler，不重新定义 action 的视觉信息。

### 4.6 `xtable.ui.resources`

职责：

- 集中管理 SVG 图标和后续 UI 静态资源。
- 所有工具栏、侧栏、状态栏和弹窗图标必须通过统一 icon loader 获取。

资源规则：

- SVG 必须使用 `{color}` 占位符，由主题 loader 注入颜色。
- 新图标必须加入 icon registry，并补测试确认资源文件存在。
- Demo 截图放入 `docs/previews/`，不作为运行时资源。

## 5. 调用方向

模块调用方向必须保持单向：

```text
app -> ui -> application/domain 数据接口
application/domain/io/validation 不反向依赖 ui
业务新 UI 需求 -> 先做 ui 组件或页面 -> 再由 app/application 注入数据和动作
```

约束：

- `xtable.app` 只负责启动、创建主窗口、注入项目服务和 Dialog 服务。
- `xtable.application` 只负责用例编排，返回数据、状态、错误和问题列表。
- `xtable.domain`、`xtable.io`、`xtable.validation`、`xtable.table_engine` 不 import `PySide6`。
- 禁止业务模块直接创建 `QMessageBox`、`QTableWidget`、`QDialog`、`QTabWidget`、`QSplitter` 等复杂 UI 控件。
- 新 UI 需求必须先进入 `xtable.ui.components`、`xtable.ui.shell` 或同级 UI 模块。

## 6. Demo 结构

Phase 1.5 Demo 应展示一个完整但静态的编辑器壳：

- 顶部菜单和图标工具栏。
- 左侧 `Table`、`Enum`、`Meta` 导航。
- 中央 `PreviewTable`，展示表头、普通单元格、只读单元格、错误单元格、警告单元格和选中态。
- 字段编辑或属性面板 `FieldInspector`，展示字段名、类型、是否必填、默认值、说明等静态输入控件。
- 底部 `EditorStatusBar`，展示问题摘要、项目上下文、保存状态、校验状态和后台任务。
- 底部 `DiagnosticsDrawer`，展示问题页和日志页。
- 统一 `MessageDialog` 和 `ConfirmDialog` 样板。
- Light/Dark 切换后，所有组件同步更新主题。

Demo 不需要保存用户输入，也不需要把示例数据传回业务层。

Demo 页面组成：

- `table` 页面：`PreviewTable` + `FieldInspector`，展示典型配置表编辑布局。
- `enum` 页面：静态列表样板 + 详情面板，验证导航页面可替换。
- `meta` 页面：静态结构字段样板 + 说明面板，验证复杂类型页面入口。
- `diagnostics` 抽屉：问题表、日志表和示例诊断文本。
- `dialogs` 触发入口：工具栏或菜单中提供“错误弹窗”和“确认弹窗”预览动作。

Demo 数据：

- 使用内置静态 Python 数据结构。
- 示例中必须包含正常、只读、错误、警告和选中状态。
- 示例文字使用真实 XTable 场景，例如字段名、字段类型、默认值、枚举引用和校验提示。

## 7. 按钮与弹窗规则

- 通用操作默认使用图标按钮，文本进入 tooltip、accessibleName 和菜单项。
- 需要用户严谨确认的场景，例如确认、取消、删除、覆盖、退出，使用明确文本按钮。
- 错误、警告、确认类提示必须使用统一 Dialog 组件，不直接使用系统默认弹窗。
- 弹窗必须具备稳定 objectName，便于测试和截图验收。

## 8. 验收标准

Phase 1.5 完成后必须满足：

- `python -m xtable.ui.demo` 可启动独立 UI Kit Demo。
- 主程序菜单可打开 UI Kit Demo。
- Demo 不依赖真实项目文件和业务数据。
- Demo 中可见菜单、工具栏、侧栏、状态栏、诊断抽屉、表格样板、字段面板和弹窗样板。
- Light/Dark 均可切换，关键控件无系统默认浅色样式露出。
- `xtable.ui` 提供可复用组件和 Demo，后续业务 UI 优先复用。
- `xtable.app` 不直接拼复杂 UI。
- `application`、`domain`、`io`、`validation` 不 import `PySide6`。
- 新增 UI 模块边界测试、Demo 启动 smoke 测试和 Light/Dark Demo 截图。
- 更新开发日志、开发计划、UI 实现规范和阶段评估记录。

## 9. 测试策略

- 单元测试：验证 UI 模块导出、action 定义、主题 token、组件 objectName 和 icon-id。
- 架构测试：扫描非 UI 模块，确保不 import `PySide6`。
- Demo smoke 测试：offscreen 启动 Demo，检查核心组件存在、主题切换生效、弹窗可创建。
- 截图证据：生成并保存 Light/Dark Demo 截图。
- 回归测试：保留已有主窗口、图标、弹窗、状态栏和项目文件测试。

## 10. 实施顺序

1. 更新文档状态，标记 Phase 1.5 开始。
2. 新建组件包结构和导出边界。
3. 抽出或包装现有状态栏、诊断抽屉、弹窗、动作和主题能力。
4. 新增 `PreviewTable` 和 `FieldInspector` 静态样板组件。
5. 新增 `EditorShell`，让 Demo 和主窗口能复用同一套壳层能力。
6. 新增独立 Demo 入口和主程序菜单入口。
7. 补自动化测试、架构测试和截图证据。
8. 更新开发日志、开发计划、UI 实现规范和阶段评估记录。
