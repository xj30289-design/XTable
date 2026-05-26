# XTable 开发日志

本文档是 XTable 项目的持续开发记录，也是项目规范的一部分。后续任何开发阶段启动、范围调整、验收完成或需求变更，都必须同步更新本文档。

## 1. 当前状态

- 当前阶段：Phase 3 - 表格编辑工作台
- 当前 Sprint：Sprint 3 - 表格编辑工作台
- 当前负责人：Codex
- 当前会话协作角色：测试角色；负责复验 Phase 3 表格工作台大表滚动方向状态反馈并更新验收记录
- 最近更新时间：2026-05-26
- 总体进度：55%
- 验收完整度：Phase 2 核心数据模型测试验收通过；Phase 3 第十批次整改已复验关闭，第十一批次 `TableWorkbench` 筛选/查找入口已复验关闭，第十二批次替换入口已复验关闭，第十三批次排序入口已复验关闭；第十四批次单格粘贴撤销/重做闭环已复验关闭；第十五批次多格粘贴撤销/重做闭环已复验关闭；第十六批次插入删除撤销/重做闭环已复验关闭；第十七批次批量填充撤销/重做闭环已复验关闭；第十八批次键盘复制/粘贴/撤销/重做工作流已复验关闭；第十九批次只读写入拒绝反馈已复验关闭；第二十批次可见编辑提交/取消体验已复验关闭；第二十一批次大表批量编辑反馈已复验关闭；第二十二批次大表批量操作后定位反馈已复验关闭；第二十三批次大表首尾快速导航已复验关闭；第二十四批次大表横向首尾快速导航已复验关闭；第二十五批次大表滚动位置反馈已复验关闭；第二十六批次大表可见范围反馈已复验关闭；第二十七批次大表可见范围状态文本已复验关闭；第二十八批次大表滚动进度状态文本已复验关闭；第二十九批次大表滚动方向状态反馈已复验关闭

## 2. 状态枚举

阶段和 Sprint 只能使用以下状态：

- `未开始`
- `进行中`
- `阻塞`
- `待验收`
- `已完成`
- `延期`

## 3. 阶段进度

| 阶段 | 状态 | 进度 | 验收完整度 | 备注 |
| --- | --- | --- | --- | --- |
| 文档规范与需求拆分 | 已完成 | 100% | 100% | 已建立开发计划、开发日志和独立规格文档 |
| Phase 0：工程骨架与技术基线 | 已完成 | 100% | 100% | 第一、第二、第三批次相关问题均已关闭 |
| Phase 1：项目与文件系统 | 待验收 | 97% | 97% | 第一至第五批次评估问题均已关闭；Editor UI Demo 规划作为后续 UI 基座前置目标 |
| Phase 1.5：Editor UI Demo 与 UI Kit 基座 | 待验收 | 97% | 96% | 第七批次二次复验通过并关闭；本次 UI 规范扫描将 Demo 非确认场景文本按钮替换为图标按钮，并补充门禁测试 |
| Phase 2：核心数据模型 | 已完成 | 100% | 95% | 最新功能测试验收通过：引用索引、默认值模板、结构变更影响检查、模型复制派生和 schema 迁移入口均已补齐；剩余复杂规则和真实编辑工作流转入 Phase 3/4/5 |
| Phase 3：表格编辑工作台 | 进行中 | 90% | 88% | 第十批次整改复验通过；筛选、查找、替换和排序入口均已复验通过；单格粘贴、多格粘贴、插入删除、批量填充、键盘复制/粘贴/撤销/重做工作流、只读写入拒绝反馈、可见编辑提交/取消体验、大表批量编辑反馈、大表批量操作后定位反馈、大表首尾快速导航、大表横向首尾快速导航、大表滚动位置反馈、大表可见范围反馈、大表可见范围状态文本、大表滚动进度状态文本和大表滚动方向状态反馈均已复验关闭；大表真实拖拽手感和阶段验收仍需后续收口 |
| Phase 4：规则与校验系统 | 未开始 | 0% | 0% | 依赖 Phase 3 |
| Phase 5：导入导出 | 未开始 | 0% | 0% | 依赖 Phase 4 |
| Phase 6：Enum、Meta 与高级类型能力 | 未开始 | 0% | 0% | 依赖 Phase 5 |
| Phase 7：日志与诊断系统 | 未开始 | 0% | 0% | 依赖核心业务事件 |
| Phase 8：稳定性、性能与验收打磨 | 未开始 | 0% | 0% | 依赖功能集成 |

## 4. 当前 Sprint 记录

### Sprint 0：文档体系建立

- 目标：建立独立开发计划、开发日志、类型规格文档，并把主需求文档调整为总览与索引。
- 开始日期：2026-05-23
- 结束日期：待定
- 范围：
  - 新建 `docs/development-plan.md`。
  - 新建 `docs/development-log.md`。
  - 新建 `docs/specs/table-types.md`。
  - 新建 `docs/specs/field-types.md`。
  - 新建 `docs/specs/enums.md`。
  - 新建 `docs/specs/meta-types.md`。
  - 新建 `docs/specs/validation-rules.md`。
  - 更新 `docs/requirements.md` 为总览与索引。
- 已完成：
  - 明确文档体系和长期维护规范。
  - 明确 Python + PySide6/Qt + Qt Model/View 技术路线。
  - 完成主需求文档索引化。
  - 完成表格类型、字段类型、枚举、数据元和校验规则规格文档。
- 未完成：
  - 代码开发未开始。
- 风险：
  - 类型规格持续扩展时，主需求文档和独立规格文档可能发生重复或不一致。
- 验收结果：
  - 本地文档验收通过，等待进入 Phase 0。

### Sprint 1：项目与文件系统

- 目标：完成 Phase 1 项目与文件系统，并补齐可运行工程基线。
- 开始日期：2026-05-23
- 结束日期：2026-05-23
- 范围：
  - 新建 Python 工程配置 `pyproject.toml`。
  - 建立 `xtable` 包结构和应用入口。
  - 实现 PySide6 主窗口骨架、顶部项目工具栏、左侧功能栏、状态栏。
  - 实现项目配置模型、项目创建、项目打开、项目保存。
  - 实现推荐项目目录结构、最近项目记录、外部修改检测、只读检测、疑似占用和写入失败冲突提示。
  - 扩展项目配置 schema，记录项目 ID、创建/更新时间、路径、导出、UI 和安全策略。
  - 新增项目文件服务测试、异常文件测试、主窗口 UI smoke 测试和验收入口测试。
- 已完成：
  - 用户可创建本地项目目录并生成 `xtable.project.json`。
  - 用户可重新打开项目并恢复项目设置。
  - 保存使用临时文件写入、flush/fsync 和原子替换；失败时保持原配置文件不变。
  - 保存时会区分外部修改、只读文件、权限拒绝、疑似占用、磁盘空间不足、路径不存在和普通写入失败。
  - 最近项目记录会去重并按最近打开顺序保存。
  - 主窗口提供菜单栏、图标工具栏、新建、打开、保存、导入、导出、校验、撤销、重做、主题切换和问题抽屉入口。
  - 侧栏 Table、Enum、Meta 入口已图标化，并具备稳定对象名、工具提示和占位页面切换。
  - 状态栏使用短值和 tooltip 承载当前项目、当前对象、保存状态、校验状态、后台任务和问题数量。
  - 问题抽屉改为底部弹出，不挤压左侧导航和主工作区宽度。
  - Dark/Light 主题覆盖工具栏、菜单、提示、状态栏和 hover/checked/disabled 状态。
  - 新增统一项目图标体系，工具栏、侧栏和状态栏图标由主题 token 着色。
  - 新增正式 SVG 图标资源目录 `src/xtable/ui/resources/icons/`。
  - 底部诊断抽屉使用可拖拽垂直 splitter，并包含问题和日志两个页签。
  - 诊断抽屉高度支持 160px 到窗口高度 50% 的范围，并记录用户设置。
  - 状态栏新增问题按钮，用最高级别图标和数量打开诊断抽屉。
  - 顶部工具栏移除问题高频入口，状态栏问题按钮成为主要入口。
  - 第四批次已补齐 Dark 诊断抽屉边界 token、状态栏分组间距、靠左问题摘要入口和扁平撤销/重做图标。
  - 第五批次已新增统一 `MessageDialog`，错误提示不再裸用 `QMessageBox`，并补充弹窗主题 token、回归测试和 Light/Dark 截图证据。
  - 新增 Phase 0/1 验收映射清单，区分自动化测试和人工验收项。
- 未完成：
  - 暂未实现复杂导入导出和版本工具集成命令，符合 Phase 1 明确不做范围。
  - 第五批次 UI 细节问题已完成开发修复，等待人工验收。
- 风险：
  - Windows、macOS 和 Linux 对只读/占用文件的底层行为不同，需要在后续打包阶段补充跨平台手工验收。
- 验收结果：
  - 第一至第四批次评估问题已关闭；第五批次问题已完成开发修复，当前等待人工验收。

### Sprint 1.5：Editor UI Demo 与 UI Kit 基座

- 目标：在进入真实业务编辑功能前，完成独立、可复用、可验收的 UI Kit 和编辑器 Demo。
- 开始日期：2026-05-24
- 结束日期：2026-05-24
- 范围：
  - 新增 `xtable.ui.components` 组件包。
  - 新增 `EditorShell` 统一编辑器外壳。
  - 新增 `python -m xtable.ui.demo` 独立 Demo 入口。
  - 主程序帮助菜单新增 UI Kit Demo 入口。
  - 补充 UI-first 架构规则：新 UI 需求必须先进入 `xtable.ui`。
  - 新增组件、Demo、架构边界和弹窗测试。
- 已完成：
  - `IconToolButton`、`NavigationRail`、`EditorToolbar`、`PreviewTable`、`FieldInspector` 已形成组件边界。
  - `ConfirmDialog` 已补齐严谨确认场景的文本按钮弹窗。
  - `UiKitDemoWindow` 展示菜单、工具栏、侧栏、状态栏、诊断抽屉、表格样板、字段面板和弹窗样板。
  - Light/Dark Demo 截图已生成：[Light](./previews/phase-1-5-ui-kit-demo-light.png)、[Dark](./previews/phase-1-5-ui-kit-demo-dark.png)。
  - 自动化测试已覆盖非 UI 模块不得 import `PySide6`。
  - 第六批次已扩展 Demo 组件实验室页面、状态控制区、字段编辑 Shell、Dialog 专页和 UI Kit 组件文档。
  - 第六批次已新增 app 层高风险 Qt 控件扫描，强化 UI-first 门禁。
  - 第七批次已新增焦点管理器、表格 TSV 粘贴/批量填充/只读保护、工作区页签、Json 格式化/校验、数据列表和 selection token。
  - 第七批次二次整改已将焦点管理接入 `EditorShell` Demo 运行时，补齐页面切换/外部点击失活、表格 Ctrl+C/Ctrl+V 与工具按钮、Json 校验/格式化/压缩按钮、只读/display-mode 控件状态。
- 未完成：
  - 未接入真实 Table/Enum/Meta 业务数据，符合 Phase 1.5 明确不做范围。
  - 未实现真实导入导出和校验流程，后续 Phase 2/3/4 执行。
  - 当前 offscreen 截图环境没有枚举到中文字体，已补字体 fallback 代码和规范；最终人工截图仍需在真实字体环境复验。
- 风险：
  - 当前 Demo 是静态 UI 样板，后续真实业务页面接入时仍需继续保持 UI-first 组件边界。
  - 后续业务阶段仍需持续执行 UI-first 门禁，避免绕过 UI Kit 直接拼复杂 Qt 控件。
- 验收结果：
  - 第六批次增强已由人工确认关闭，控件主题适配没有明显问题。
  - 第七批次二次复验通过，`B7-001` 至 `B7-010` 均已关闭；Phase 1.5 仍保持待验收，等待后续整体人工确认。

### Sprint 2：核心数据模型

- 目标：建立 Table、Field、Enum、Meta 的统一纯业务模型，为后续表格编辑、校验、导入导出提供稳定数据契约。
- 开始日期：2026-05-24
- 结束日期：待定
- 范围：
  - 新增字段类型枚举和字段定义。
  - 新增普通表、分组表、二维表定义。
  - 新增全局枚举定义、枚举项定义。
  - 新增 Meta 定义和子字段复用契约。
  - 新增项目级 `ProjectSchema` 注册和引用解析。
  - 新增字段类型注册表和表格类型注册表。
- 已完成：
  - `xtable.domain.models` 提供 `FieldDefinition`、`TableDefinition`、`NormalTableDefinition`、`GroupTableDefinition`、`MatrixTableDefinition`、`EnumDefinition`、`MetaDefinition`、`ProjectSchema`。
  - `FieldTypeRegistry.mvp()` 已覆盖 `string`、`int`、`float`、`bool`、`enum`、`id`、`reference`、`list`、`meta`、`json`。
  - `TableTypeRegistry.mvp()` 已覆盖普通表、分组表和二维表，并声明表格类型必要参数。
  - 新增 `tests/test_phase2_domain_models.py`，覆盖模型注册、引用解析、重复 ID 拒绝、分组/二维表参数和 domain 不依赖 Qt。
  - UI 规范收尾：Demo 非确认/取消场景的文本按钮已替换为图标按钮，并新增架构测试防止回退。
  - 第八批次已补齐 `ProjectSchema` 结构级校验、`FieldDefinition.validate_shape()`、`validate_structure()` 和非法结构回归测试。
- 未完成：
  - 尚未实现模型序列化、持久化读写和导入导出解析。
  - 尚未实现完整业务校验规则；后续 Phase 4 负责范围、唯一性、Json 内容、跨表诊断报告等复杂规则，Phase 2 只提供结构契约。
  - 尚未接入真实 UI 编辑器和表格模型；后续 Phase 3 执行。
- 风险：
  - 字段类型参数后续会随校验、导入导出继续扩展，需要保持 registry 元数据向后兼容。
  - 字段类型参数后续会随校验、导入导出继续扩展，需要保持 registry 元数据向后兼容。
- 验收结果：
  - 第八批次结构校验、第九批次 schema 持久化和 Phase 2 整体验收均已通过。
  - Phase 2 当前开发清单已达到进入 Phase 3 表格编辑工作台的条件；复杂业务校验、导入导出和真实编辑工作流继续在 Phase 3/4/5 推进。

### Sprint 3：表格编辑工作台

- 目标：基于 Phase 2 领域模型建立可编辑表格工作台，覆盖表格模型适配、单元格编辑、选择、复制粘贴、批量填充、插入删除、查找替换、筛选排序和撤销重做。
- 开始日期：2026-05-25
- 结束日期：待定
- 范围：
  - 建立基于 `QAbstractTableModel` 的表格模型适配层。
  - 接入 Phase 2 `TableDefinition`、`FieldDefinition` 和 `TableRow` 数据结构。
  - 实现单元格编辑、提交、取消和只读保护。
  - 实现选择、复制、粘贴、批量填充和插入删除。
  - 实现查找、替换、筛选、排序。
  - 实现撤销/重做命令栈。
  - 实现错误、警告、只读和引用标记的单元格状态展示。
- 已完成：
  - Phase 3 已启动，输入条件已满足：Phase 2 数据模型可用，Phase 1.5 UI Kit 可作为真实编辑界面复用基础。
- 未完成：
  - 尚未建立表格模型适配层。
  - 尚未接入真实表定义、字段定义和行数据。
  - 尚未实现真实编辑命令、撤销重做、查找替换、筛选排序和单元格状态映射。
- 风险：
  - 新增 UI 必须先复用或补齐 `xtable.ui` 组件，避免业务界面绕过 UI Kit 直接创建复杂 Qt 控件。
  - 表格编辑命令需要尽早形成可测试边界，否则复制粘贴、批量编辑和撤销重做会互相耦合。
- 验收结果：
  - 阶段刚启动，等待首批开发任务和自动化测试覆盖。

## 5. 进度记录规则

- 每次开始新阶段，必须更新“当前状态”和“阶段进度”。
- 每次完成阶段任务，必须更新阶段进度、已完成内容和未完成内容。
- 每次完成验收，必须更新验收完整度，并记录验收结果。
- 每次阶段审核、代码评审、架构复盘或人工验收后，必须同步更新 [阶段开发评估记录](./development-review.md)。
- 阶段进度和验收完整度必须与 [阶段开发评估记录](./development-review.md) 中未关闭问题保持一致。
- 每次需求范围变化，必须在“变更记录”中记录，并链接对应需求文档。
- 开发日志不得替代 Git commit message；提交代码或文档时仍需保留清晰提交信息。
- 如果阶段被阻塞，必须记录阻塞原因、影响范围和下一步处理方式。

## 6. 变更记录

| 日期 | 类型 | 内容 | 关联文档 |
| --- | --- | --- | --- |
| 2026-05-23 | 文档规范 | 建立开发计划与开发日志规范，要求后续开发持续维护进度和验收完整度 | [开发计划](./development-plan.md) |
| 2026-05-23 | 需求拆分 | 将表格类型、字段类型、枚举、数据元和校验规则拆分为独立规格文档 | [主需求文档](./requirements.md) |
| 2026-05-23 | 阶段验收 | Sprint 0 文档体系本地验收通过，下一阶段为 Phase 0 工程骨架与技术基线 | [开发日志](./development-log.md) |
| 2026-05-23 | 需求变更 | 字段类型新增 Json，要求支持 Json 内容校验和相关 UI 功能 | [字段类型规格](./specs/field-types.md) |
| 2026-05-23 | 阶段开发 | 完成 Phase 0 必要工程基线和 Phase 1 项目与文件系统，进入待验收 | [开发计划](./development-plan.md) |
| 2026-05-23 | 文档规范 | 新增阶段开发评估记录，要求每次阶段审核记录问题、影响、建议和处理状态，并作为后续开发目标参考 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 阶段审核 | 记录 Phase 0 与 Phase 1 审核问题，并下调 Phase 1 验收完整度以反映未关闭问题 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 返工修复 | 根据阶段开发评估补齐项目目录结构、原子保存、错误分类、UI 主题、侧栏切换、结构化状态栏、问题抽屉和测试覆盖 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 阶段审核 | 新增第二批次 UI 评估，记录布局边界、图标按钮、侧栏与状态栏图标化、工具栏菜单分类、主题按钮位置和 Dark 主题可读性问题 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 阶段审核 | 补充第二批次问题：问题抽屉应从底部弹出，新建项目配置需记录导出目录和更完整参数；同时关闭第一批次中已确认 100% 完成的问题 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 修改建议 | 补充第一批次未达 100% 问题的集中修改建议，作为后续修复安排依据 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 返工修复 | 按第一批次未达 100% 和第二批次 UI 评估建议完成修复，并新增 Phase 0/1 验收映射清单 | [验收映射清单](./acceptance-map.md) |
| 2026-05-23 | 阶段审核 | 第一批次与第二批次问题标记为已验收关闭，并新增第三批次图标体系、底部抽屉、日志页签和状态栏问题入口评估 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 阶段验收 | 完成第三批次验收：日志整合通过，其余问题部分通过或未完全通过；新增 UI 实现质量规范，约束主题覆盖、图标按钮、诊断抽屉和截图验收 | [UI 实现质量规范](./ui-implementation-guidelines.md) |
| 2026-05-23 | 返工修复 | 第三批次已完成一轮实现，但验收确认仍需继续修复主题覆盖、抽屉高度范围、顶部问题入口和侧栏按钮视觉样式 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 阶段复验 | 第三批次复验通过：正式 SVG 图标、Dark 诊断抽屉、可调高度、日志页签、状态栏问题入口和侧栏图标样式均已关闭 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 文档规范 | 新增项目角色协作规范，明确角色按会话区分：当前会话为测试角色，另一个会话可作为开发角色；开发角色负责实际代码执行，测试角色只负责评估、找 bug、验收、复验和更新文档 | [项目角色协作规范](./project-role-guidelines.md) |
| 2026-05-23 | 阶段审核 | 新增第四批次 UI 细节评估，归档诊断抽屉 Dark 边界、状态栏密度、靠左问题按钮和撤回/前进图标问题；当前会话仅作为测试角色记录问题 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 返工修复 | 完成第四批次 UI 细节修复：统一诊断抽屉边界 token，优化状态栏分组与靠左问题摘要入口，重绘撤销/重做扁平图标，并补充自动化测试 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 阶段验收 | 第四批次问题经人工确认基本验收通过并关闭 | [阶段开发评估记录](./development-review.md) |
| 2026-05-23 | 阶段审核 | 新增第五批次评估：提示弹窗不符合项目 UI 规范，并补充 UI 主题问题反复出现的技术路线与治理方案分析 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 返工修复 | 完成第五批次修复：新增统一 MessageDialog，替换裸 QMessageBox，补充弹窗主题 token、治理规范、自动化测试和 Light/Dark 截图证据 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 阶段开发 | 完成 Phase 1.5 UI Kit 与 Demo：新增 UI 组件包、EditorShell、独立 Demo、主程序入口、架构边界测试和 Light/Dark 截图证据 | [Phase 1.5 设计](./superpowers/specs/2026-05-24-phase-1-5-ui-kit-design.md) |
| 2026-05-24 | UI 规划 | 新增 Editor UI Demo 规划，梳理编辑器 UI Kit、Demo 页面、主题系统、通用组件、诊断组件、弹窗服务和验收标准，作为后续业务 UI 的前置基座 | [Editor UI Demo 规划](./editor-ui-demo-plan.md) |
| 2026-05-24 | 阶段验收 | 第五批次提示弹窗与 UI 技术治理问题经人工确认验收通过并关闭，后续治理目标转入 Editor UI Demo 规划 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 阶段验收 | 完成 Phase 1.5 UI Kit 与 Demo 验收评估：基础闭环通过，完整度约 82%，新增第六批次增强问题 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 阶段审核 | 补充第六批次问题：测试过程中发现仍存在不符合主题的“覆盖文件”确认弹窗，需要全量排查并统一弹窗调用路径 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 返工修复 | 完成第六批次增强修复：扩展 UI Kit Demo 页面和状态控制，补字段编辑 Shell、组件文档、字体策略、弹窗主题闭环和 UI-first 门禁测试 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 阶段验收 | 完成 Phase 1.5 控件级功能测试：51 项自动化测试、编译检查和运行时控件交互通过；补充系统文件/输入弹窗治理和遗留状态栏组件风险 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 阶段验收 | 第六批次问题经人工确认关闭，控件主题适配未见明显问题 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 阶段审核 | 新增第七批次评估：归档输入框全局激活/失活、表格批量编辑与粘贴、多窗口/多页签、Json 编辑体验、表格滚动、下拉状态按钮、Light 选中态、伪输入控件和数据列表展示问题 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 返工修复 | 完成第七批次修复：新增焦点管理、表格粘贴/批量填充、多文档页签、Json 校验格式化、数据列表、下拉状态按钮和 selection token | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 阶段复验 | 第七批次复验未完全通过：自动化测试 58 项通过，但实际 Demo 中输入框未接入全局焦点管理，点击/切页未失活，伪输入控件区分未落地；表格粘贴和 Json 编辑体验仍需补真实交互入口 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 返工修复 | 按第七批次最新复验建议完成二次整改：EditorShell 接入全局焦点管理和外部失活，表格补 Ctrl+C/Ctrl+V 与工具按钮，Json 补可见工具栏和实时行列，只读/display 控件状态落地 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 阶段复验 | 第七批次二次复验通过：自动化测试 60 项通过，编译检查通过，运行时脚本验证 B7-001 至 B7-010 全部通过并关闭 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | UI 规范收尾 | 完成 UI 规范扫描，将 Demo 非确认场景文本按钮替换为图标按钮，并新增架构门禁测试防止通用操作回退到文本按钮 | [UI Kit 组件说明](./ui-kit-components.md) |
| 2026-05-24 | 阶段开发 | 启动 Phase 2 核心数据模型：新增纯 domain 模型、字段/表格类型注册表、Table/Field/Enum/Meta/ProjectSchema 契约和自动化测试 | [开发计划](./development-plan.md) |
| 2026-05-24 | 阶段审核 | 新增第八批次 Phase 2 审查：记录核心数据模型结构校验缺口，包括字段引用完整性、主键/特征键/表类型参数、Enum 导出值与默认项、Meta 字段名、行结构和失败用例覆盖不足 | [阶段开发评估记录](./development-review.md) |
| 2026-05-24 | 返工修复 | 完成第八批次开发修复：补齐 ProjectSchema 结构校验、FieldDefinition 参数契约、Enum/Meta/Table/Row 非法结构拦截和失败用例回归测试 | [阶段开发评估记录](./development-review.md) |
| 2026-05-25 | 阶段开发 | 完成 Phase 2 Schema 持久化本地方案与执行：新增 `xtable.domain.serialization`、`settings/schema.json` 保存/加载、`schema_digest` 外部修改检测、Meta 循环阻塞与 Table 循环发现；验证 `python -m pytest` 81 项通过，`python -m compileall -q src tests` 通过。 | [Schema 持久化设计](./superpowers/specs/2026-05-25-phase-2-schema-persistence-design.md)、[实施计划](./superpowers/plans/2026-05-25-phase-2-schema-persistence.md) |
| 2026-05-25 | 阶段验收 | 完成 Phase 2 Schema 持久化新增内容验收：自动化测试 81 项通过、编译通过；新增第九批次 P1 问题，记录未加载 schema 时 `schema_digest` 为空导致已有 schema 可被覆盖的风险。 | [阶段开发评估记录](./development-review.md) |
| 2026-05-25 | 返工修复 | 修复第九批次 `B9-001`：`save_schema()` 在已有 schema 文件且 `schema_digest` 为空时拒绝保存，避免未先 `load_schema()` 的项目覆盖现有 `settings/schema.json`；新增回归测试覆盖该场景，状态标记为待验证。 | [阶段开发评估记录](./development-review.md) |
| 2026-05-25 | 阶段复验 | 第九批次 `B9-001` 复验通过：定向测试、Phase 2 相关 34 项测试、编译检查和独立探针均通过，`schema_digest` 空基线覆盖风险已关闭；当时发现的跨阶段 UI 剪贴板失败已记录为 `X-003`，并在后续整体验收中关闭。 | [阶段开发评估记录](./development-review.md) |
| 2026-05-25 | 文档规范 | 补齐 Phase 0 至 Phase 8 开发清单，并将各阶段测试评估验收清单独立拆分到 `docs/phase-checklists/` 子目录；后续每个 Phase 必须同步维护开发清单和独立验收清单。 | [开发计划](./development-plan.md)、[阶段清单目录](./phase-checklists/phase-2-domain-models.md) |
| 2026-05-25 | 阶段开发 | 完成 Phase 2 剩余开发清单：新增引用索引与依赖查询、字段默认值与新行模板、结构变更影响检查、模型复制派生与 schema 迁移入口；验证 `python -m pytest` 87 项通过，`python -m compileall -q src tests` 通过。 | [开发计划](./development-plan.md)、[Phase 2 验收清单](./phase-checklists/phase-2-domain-models.md) |
| 2026-05-25 | 阶段验收 | 验证 Phase 2 最新功能：Phase 2 相关 39 项测试通过、全量 87 项测试通过、编译检查通过、独立运行时探针通过；Phase 2 核心数据模型标记为已完成，跨阶段 `X-003` 剪贴板问题复验关闭。 | [阶段开发评估记录](./development-review.md)、[Phase 2 验收清单](./phase-checklists/phase-2-domain-models.md) |
| 2026-05-25 | 阶段开发 | 推进 Phase 3 表格编辑工作台首批能力：新增 `xtable.table_engine` 表格模型适配层，接入 Phase 2 表定义与行数据，支持 Qt 行列/表头/取值/编辑/只读 flags、基础复制粘贴、插入删除、单元格状态映射和单元格编辑撤销重做；验证 `python -m pytest` 94 项通过，`python -m compileall -q src tests` 通过。 | [开发计划](./development-plan.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段审核 | 新增第十批次 Phase 3 首批能力评估：自动化 94 项通过，但缺少可见表格工作台 UI，人工操作测试被阻塞；同时记录字段类型转换、单元格状态刷新、撤销重做视图通知、ID 类型契约和越界保护问题。 | [阶段开发评估记录](./development-review.md) |
| 2026-05-25 | 返工修复 | 修复第十批次 `B10-001` 至 `B10-006`：新增可见 `TableWorkbench`/`QTableView` Demo 入口，补字段类型解析与非法输入拒绝，状态更新和撤销重做改由 Qt 模型发出刷新信号，ID 测试数据与 Phase 2 契约对齐，并补范围边界保护；问题状态标记为待验收。继续推进 Phase 3 查找、替换、筛选、排序和批量填充底层能力；验证 `python -m pytest` 97 项通过，`python -m compileall -q src tests` 通过。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段复验 | 第十批次 `B10-001` 至 `B10-006` 复验通过：全量 97 项测试、编译检查、B10 定向 16 项测试和运行时探针均通过；Phase 3 可进入有限表格操作测试，查找、替换、筛选、排序和完整业务闭环继续后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段开发 | 推进 Phase 3 表格工作台操作入口：`TableWorkbench` 新增筛选输入、清除筛选、查找输入和查找下一个按钮；筛选会隐藏不匹配行，清除后恢复全部行，查找会定位到匹配单元格。新增 UI 回归测试覆盖筛选和查找路径，并固定 pytest 的 Qt offscreen 环境以稳定剪贴板快捷键测试；验证 `python -m pytest` 98 项通过，`python -m compileall -q src tests` 通过。当前交接为待测试验收；替换和排序 UI 仍为后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段复验 | 第十一批次 `TableWorkbench` 筛选与查找入口复验通过：定向测试 1 项、Phase 3/UI 组合回归 25 项、全量 98 项测试、编译检查和运行时控件探针均通过；筛选/清除筛选/查找定位已关闭，替换、排序和完整业务编辑闭环继续后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段开发 | 推进 Phase 3 表格工作台替换入口：`TableWorkbench` 新增替换输入和替换全部按钮，`replace_all_matches()` 使用查找文本执行替换并定位首个变更单元格；`QtTableModel.replace_all()` 发出 `dataChanged` 保障视图刷新。验证 Phase 3/UI 组合回归 27 项通过、全量 100 项通过、编译检查通过，运行时探针确认替换 `Potion -> Hi-Potion` 后定位到变更单元格。当前交接为待测试验收；排序 UI 和完整业务编辑闭环仍待后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段复验 | 第十二批次替换入口复验通过：定向测试 2 项、Phase 3/UI 组合回归 27 项、全量 100 项测试、编译检查和运行时探针均通过；替换按钮存在，替换后单元格值、定位和 `dataChanged` 信号均符合预期。排序 UI 和完整业务编辑闭环继续后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段开发 | 推进 Phase 3 表格工作台排序入口：`TableWorkbench` 新增当前列升序/降序按钮，`sort_by_current_column()` 按当前列排序并定位到第一行；`QtTableModel.sort_by_column()` 发出 layout 信号并保持单元格状态跟随原行。验证 Phase 3/UI 组合回归 29 项通过、全量 102 项通过、编译检查通过，运行时探针确认 Count 列升降序和状态迁移符合预期。当前交接为待测试验收；完整业务编辑闭环仍待后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段复验 | 第十三批次排序入口复验通过：定向测试 2 项、Phase 3/UI 组合回归 29 项、全量 102 项测试、编译检查和运行时探针均通过；升序/降序按钮、Count 列排序、状态迁移和 layout 信号均符合预期。完整业务编辑闭环继续后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段开发 | 推进 Phase 3 表格工作台完整业务编辑闭环：`TableWorkbench.paste_clipboard()` 的单格粘贴路径改为进入 `EditCommandStack`，使可见粘贴、撤销按钮和重做按钮形成闭环；新增 UI 回归测试覆盖粘贴 `Mega Potion` 后撤销恢复 `Potion`、重做恢复 `Mega Potion`。验证定向测试 1 项通过、表格/UI 组合回归 25 项通过、全量 103 项通过、编译检查通过。当前交接为待测试验收；多格粘贴、插入删除和批量填充的命令化撤销仍待后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段复验 | 第十四批次单格粘贴撤销/重做闭环复验通过：定向测试 1 项、Phase 3/UI 组合回归 30 项、全量 103 项测试、编译检查和 offscreen 运行时探针均通过；粘贴后值、撤销恢复、重做恢复和命令栈状态均符合预期。多格粘贴、插入删除和批量填充命令化撤销继续后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段开发 | 推进 Phase 3 表格工作台多格粘贴撤销/重做闭环：`EditCommandStack` 新增批量 cell edit 命令和 `paste_tsv()`，`TableWorkbench.paste_clipboard()` 的 TSV 路径改为进入命令栈；新增 UI 回归测试覆盖 2x2 TSV 粘贴、撤销恢复原值、重做恢复新值。验证定向测试 2 项通过、表格/UI 组合回归 26 项通过、全量 104 项通过、编译检查通过，offscreen 运行时探针确认按钮路径有效。当前交接为待测试验收；插入删除和批量填充的命令化撤销仍待后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段复验 | 第十五批次多格粘贴撤销/重做闭环复验通过：定向测试 1 项、Phase 3/UI 组合回归 31 项、全量 104 项测试、编译检查和 offscreen 运行时探针均通过；2x2 TSV 粘贴后值、撤销恢复、重做恢复和命令栈状态均符合预期。插入删除和批量填充命令化撤销继续后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段开发 | 推进 Phase 3 表格工作台插入删除撤销/重做闭环：`EditCommandStack` 新增行插入/删除命令，保存受影响行数据并通过 Qt 模型行插入/删除信号恢复；`TableWorkbench` 插入行和删除行按钮改为进入命令栈。新增 UI 回归测试覆盖插入、撤销、重做、删除、撤销、重做完整路径。验证定向测试 1 项通过、表格/UI 组合回归 27 项通过、全量 105 项通过、编译检查通过，offscreen 运行时探针确认按钮路径有效。当前交接为待测试验收；批量填充的命令化撤销仍待后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段复验 | 第十六批次插入删除撤销/重做闭环复验通过：定向测试 1 项、Phase 3/UI 组合回归 32 项、全量 105 项测试、编译检查和 offscreen 运行时探针均通过；插入行、撤销插入、重做插入、删除行、撤销删除、重做删除和命令栈状态均符合预期。批量填充命令化撤销继续后续批次。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段开发 | 推进 Phase 3 表格工作台批量填充撤销/重做闭环：`TableWorkbench` 新增批量填充输入和按钮，选区填充通过 `EditCommandStack.batch_fill()` 记录变更单元格并支持撤销/重做；`QtTableModel.batch_fill()` 统一发出变更信号。新增 UI 回归测试覆盖选中两行 Count 列、填充 `7`、撤销恢复 `10/2`、重做恢复 `7/7`。验证定向测试 1 项通过、表格/UI 组合回归 28 项通过、全量 106 项通过、编译检查通过，offscreen 运行时探针确认按钮路径有效。当前交接为待测试验收。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-25 | 阶段复验 | 第十七批次批量填充撤销/重做闭环复验通过：定向测试 1 项、Phase 3/UI 组合回归 33 项、全量 106 项测试、编译检查和 offscreen 运行时探针均通过；批量填充、撤销恢复、重做恢复和命令栈状态均符合预期。完整业务编辑体验继续后续阶段验收。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台键盘快捷工作流：`TableWorkbench` 为表格视图接入 Ctrl+C、Ctrl+V、Ctrl+Z、Ctrl+Y，键盘操作复用已有复制、粘贴、撤销和重做命令链路。新增 UI 回归测试覆盖键盘复制 `Potion`、粘贴 `Mega Potion`、撤销恢复 `Elixir`、重做恢复 `Mega Potion`。验证定向测试 1 项通过、表格/UI 组合回归 29 项通过、全量 107 项通过、编译检查通过，offscreen 运行时探针确认键盘路径有效。当前交接为待测试验收。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段复验 | 第十八批次键盘复制/粘贴/撤销/重做工作流复验通过：定向测试 1 项通过，Phase 3/UI 组合回归 34 项通过，全量 107 项通过，编译检查通过，offscreen 运行时探针确认 Ctrl+C、Ctrl+V、Ctrl+Z、Ctrl+Y 均复用命令链路；本批次关闭，完整业务编辑体验继续进入阶段验收收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台只读写入拒绝反馈：`TableWorkbench` 初始化 `last-rejected-write` 状态，单格粘贴写入只读单元格失败时记录 `readonly`，成功写入时清空拒绝状态，避免只读保护只在底层静默失败。新增 UI 回归测试覆盖只读 ID 列粘贴 `9999` 后原值保持 `1001`、拒绝原因为 `readonly` 且不产生撤销历史。验证定向测试 1 项通过、表格/UI 聚焦回归 30 项通过。当前交接为待测试验收；编辑提交/取消体验仍需后续批次或阶段验收收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段复验 | 第十九批次只读写入拒绝反馈复验通过：定向测试 1 项通过，Phase 3/UI 组合回归 35 项通过，全量 108 项通过，编译检查通过，offscreen 运行时探针确认只读 ID 列粘贴后值保持 `1001`、拒绝原因为 `readonly` 且不产生撤销历史；本批次关闭，编辑提交/取消体验继续后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台可见编辑提交/取消体验：`TableWorkbench` 新增单元格编辑输入框、提交按钮和取消按钮，选中单元格后同步当前值；取消会恢复输入框且不改数据、不生成撤销历史；提交通过 `EditCommandStack.edit_cell()` 写入并进入撤销历史。新增 UI 回归测试覆盖选中 `Potion`、编辑后取消仍保持原值、再次提交变更为 `Mega Potion` 并产生撤销历史。验证定向测试 1 项通过、表格/UI 聚焦回归 31 项通过。当前交接为待测试验收；大表手感和阶段人工验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段复验 | 第二十批次可见编辑提交/取消体验复验通过：定向测试 1 项通过，Phase 3/UI 组合回归 36 项通过，全量 109 项通过，编译检查通过，offscreen 运行时探针确认编辑输入初值为 `Potion`、取消后输入和数据仍为 `Potion` 且无撤销历史、提交后值为 `Mega Potion` 并产生撤销历史；本批次关闭，大表手感和阶段人工验收继续后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台大表批量编辑反馈：`TableWorkbench` 初始化并维护 `last-batch-edit-count`，批量填充完成后记录实际变更单元格数量，方便大表跨行批量操作后确认生效范围。新增 UI 回归测试构造 250 行大表，验证表格保持像素级滚动，跨行选择 3 个 Count 单元格填充 `7` 后返回 3 个变更坐标、记录变更计数为 3，并确认远端第 249 行写入成功。验证定向测试 1 项通过、表格/UI 聚焦回归 32 项通过。当前交接为待测试验收；大表人工手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段复验 | 第二十一批次大表批量编辑反馈复验通过：定向测试 1 项通过，Phase 3/UI 组合回归 37 项通过，全量 110 项通过，编译检查通过，offscreen 运行时探针确认像素级滚动、跨行批量填充返回 3 个变更坐标、`last-batch-edit-count=3` 且第 249 行写入 `7`；本批次关闭，大表真实人工滚动手感和 Phase 3 阶段验收继续后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台大表批量操作后定位反馈：`TableWorkbench.batch_fill_selection()` 在批量填充产生变更后，将当前索引和滚动位置定位到最后一个实际变更单元格，便于跨远端行批量操作后确认结果。新增 UI 回归测试覆盖 250 行大表跨行填充后当前索引定位到第 249 行 Count 单元格。验证定向测试 2 项通过、Phase 3/UI 组合回归 38 项通过、全量 111 项通过、编译检查通过，offscreen 探针确认 `current=249,2`。当前交接为待测试验收；大表真实人工滚动手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段复验 | 第二十二批次大表批量操作后定位反馈复验通过：定向测试 1 项通过，相关定向测试 2 项通过，Phase 3/UI 组合回归 38 项通过，全量 111 项通过，编译检查通过，offscreen 探针确认跨行批量填充后 `last-batch-edit-count=3`、当前索引定位到 `249,2` 且第 249 行写入 `7`；本批次关闭，大表真实人工滚动手感和 Phase 3 阶段验收继续后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台大表首尾快速导航：`TableWorkbench` 为表格视图接入 Ctrl+End 和 Ctrl+Home，保持当前列并滚动定位到最后/第一行，减少大表人工滚动定位成本。新增 UI 回归测试覆盖 250 行大表从第 127 行 Count 列执行 Ctrl+End 到 `249,2`，再执行 Ctrl+Home 回 `0,2`。验证定向测试 2 项通过、Phase 3/UI 组合回归 39 项通过、全量 112 项通过、编译检查通过，offscreen 探针确认 `end=249,2`、`home=0,2`。当前交接为待测试验收；大表真实滚轮/拖拽滑块手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段复验 | 第二十三批次大表首尾快速导航复验通过：定向测试 1 项通过，相关键盘组合定向 2 项通过，Phase 3/UI 组合回归 39 项通过，全量 112 项通过，编译检查通过，offscreen 探针确认 Ctrl+End 定位到 `249,2`、Ctrl+Home 回到 `0,2`；本批次关闭，大表真实滚轮/拖拽滑块手感和 Phase 3 阶段验收继续后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台大表横向首尾快速导航：`TableWorkbench` 为表格视图接入 Ctrl+Right 和 Ctrl+Left，保持当前行并滚动定位到末列/首列，减少宽表横向滚动定位成本。新增 UI 回归测试覆盖 9 列宽表从第 17 行第 3 列执行 Ctrl+Right 到 `17,8`，再执行 Ctrl+Left 回 `17,0`。验证键盘定向测试 3 项通过、Phase 3/UI 组合回归 40 项通过、全量 113 项通过、编译检查通过，offscreen 探针确认 `right=17,8`、`left=17,0`。当前交接为待测试验收；大表真实滚轮/拖拽滑块手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段验收 | 复验 Phase 3 表格工作台大表横向首尾快速导航：定向测试 1 项通过，相关键盘组合定向 3 项通过，Phase 3/UI 组合回归 40 项通过，全量 113 项通过，编译检查通过；offscreen 探针确认 `Ctrl+Right` 后索引为 `17,8`、`Ctrl+Left` 后索引为 `17,0`。第二十四批次已关闭；大表真实滚轮/拖拽滑块手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台大表滚动位置反馈：`TableWorkbench` 新增 `scroll-position` 属性，记录垂直/水平滚动条当前值和最大值，并在滚动条变化时同步更新，便于验收确认滚轮/拖拽滑块后的实际位置。新增 UI 回归测试覆盖 320 行、13 列宽表滚动到中段后的状态反馈。验证大表定向测试 5 项通过、Phase 3/UI 组合回归 41 项通过、全量 114 项通过、编译检查通过，offscreen 探针确认 `{'horizontal': 108, 'horizontal-maximum': 216, 'vertical': 4720, 'vertical-maximum': 9440}`。当前交接为待测试验收；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段验收 | 复验 Phase 3 表格工作台大表滚动位置反馈：定向测试 1 项通过，大表相关回归 5 项通过，Phase 3/UI 组合回归 41 项通过，全量 114 项通过，编译检查通过；offscreen 探针确认 `scroll-position` 为 `{'horizontal': 108, 'horizontal-maximum': 216, 'vertical': 4720, 'vertical-maximum': 9440}`。第二十五批次已关闭；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台大表可见范围反馈：`TableWorkbench` 新增 `visible-range` 属性，记录当前视口首行、末行、首列和末列，并随垂直/水平滚动条变化同步更新。新增 UI 回归测试覆盖 360 行、17 列宽表滚动到中段后的可见范围反馈。验证大表相关回归 6 项通过、Phase 3/UI 组合回归 42 项通过、全量 115 项通过、编译检查通过，offscreen 探针确认初始范围为 `{'first-column': 0, 'first-row': 0, 'last-column': 5, 'last-row': 14}`，滚动后范围为 `{'first-column': 3, 'first-row': 177, 'last-column': 13, 'last-row': 182}`。当前交接为待测试验收；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段验收 | 复验 Phase 3 表格工作台大表可见范围反馈：定向测试 1 项通过，大表相关回归 6 项通过，Phase 3/UI 组合回归 42 项通过，全量 115 项通过，编译检查通过；offscreen 探针确认 `visible-range` 初始范围为 `{'first-column': 0, 'first-row': 0, 'last-column': 5, 'last-row': 14}`，滚动后范围为 `{'first-column': 3, 'first-row': 177, 'last-column': 13, 'last-row': 182}`。第二十六批次已关闭；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台大表可见范围状态文本：`TableWorkbench` 新增 `table-workbench-visible-range-label`，把 `visible-range` 转换为 1 基行列范围文本，滚动后同步展示，便于人工拖拽验收直接确认当前视口范围。新增 UI 回归测试覆盖 360 行、17 列宽表滚动后状态文本与 `visible-range` 一致。验证大表相关回归 7 项通过、Phase 3/UI 组合回归 43 项通过、全量 116 项通过、编译检查通过，offscreen 探针确认状态文本从 `行 1-15 / 列 1-6` 更新为 `行 178-183 / 列 4-14`。当前交接为待测试验收；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段验收 | 复验 Phase 3 表格工作台大表可见范围状态文本：定向测试 1 项通过，大表相关回归 7 项通过，Phase 3/UI 组合回归 43 项通过，全量 116 项通过，编译检查通过；offscreen 探针确认状态文本从 `行 1-15 / 列 1-6` 更新为 `行 178-183 / 列 4-14`。第二十七批次已关闭；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台大表滚动进度状态文本：`TableWorkbench` 新增 `table-workbench-scroll-progress-label`，把 `scroll-position` 转换为纵向/横向滚动百分比，滚动后同步展示，便于人工拖拽验收确认滑块进度。新增 UI 回归测试覆盖 360 行、17 列宽表滚动后状态文本与 `scroll-position` 一致。验证大表相关回归 8 项通过、Phase 3/UI 组合回归 44 项通过、全量 117 项通过、编译检查通过，offscreen 探针确认状态文本从 `纵向 0% / 横向 0%` 更新为 `纵向 50% / 横向 50%`。当前交接为待测试验收；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段验收 | 复验 Phase 3 表格工作台大表滚动进度状态文本：定向测试 1 项通过，大表相关回归 8 项通过，Phase 3/UI 组合回归 44 项通过，全量 117 项通过，编译检查通过；offscreen 探针确认状态文本从 `纵向 0% / 横向 0%` 更新为 `纵向 50% / 横向 50%`。第二十八批次已关闭；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段开发 | 推进 Phase 3 表格工作台大表滚动方向状态反馈：`TableWorkbench` 新增 `last-scroll-axis` 属性和 `table-workbench-scroll-axis-label`，垂直/水平滚动条变化后记录最近滚动方向并展示 `最近滚动：纵向` 或 `最近滚动：横向`，便于人工拖拽验收区分方向响应。新增 UI 回归测试覆盖 360 行、17 列宽表先纵向后横向滚动的方向状态。验证定向测试 1 项通过、大表相关回归 9 项通过、Phase 3/UI 组合回归 45 项通过、全量 118 项通过、编译检查通过，offscreen 探针确认 `vertical|最近滚动：纵向` 和 `horizontal|最近滚动：横向`。当前交接为待测试验收；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
| 2026-05-26 | 阶段验收 | 复验 Phase 3 表格工作台大表滚动方向状态反馈：定向测试 1 项通过，大表相关回归 9 项通过，Phase 3/UI 组合回归 45 项通过，全量 118 项通过，编译检查通过；offscreen 探针确认先垂直滚动后为 `vertical|最近滚动：纵向`，再水平滚动后为 `horizontal|最近滚动：横向`。第二十九批次已关闭；滚动条真实拖拽手感和 Phase 3 阶段验收仍需后续收口。 | [阶段开发评估记录](./development-review.md)、[Phase 3 验收清单](./phase-checklists/phase-3-table-workbench.md) |
