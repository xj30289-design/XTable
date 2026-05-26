# Phase 2 Schema 持久化设计

## 目标

为 Phase 2 核心数据模型补齐稳定的持久化路径，使项目能够保存并重新加载完整的 `Table`、`Field`、`Enum`、`Meta` 和 `ProjectSchema` 结构，同时不让领域模型直接耦合文件读写或 UI 代码。

## 架构边界

本设计保持三层职责分离：

- `xtable.domain.models` 负责业务模型、结构约束和引用关系校验。
- `xtable.domain.serialization` 负责 `ProjectSchema` 与带版本号的 JSON 兼容字典之间的转换。
- `xtable.application.project_service` 负责项目文件路径、原子写入、外部修改检测和错误分类。

`xtable.project.json` 继续作为项目配置文件，只保存项目元信息、路径约定、导出默认值、UI 设置和安全策略。业务 schema 单独保存到 `settings/schema.json`，使用现有项目目录约定。这样可以避免配置文件膨胀为业务数据容器，也给后续阶段拆分表格行数据、枚举、Meta 类型和规则文件留下空间。

## 文件布局

```text
xtable.project.json        # 项目元信息、路径约定、导出默认值、UI、安全策略
settings/schema.json       # Phase 2 schema：表、字段、枚举、Meta、引用关系
tables/                    # 后续阶段承载真实表格行数据
enums/                     # 后续如有需要，可拆分枚举文件
types/                     # 后续如有需要，可拆分 Meta/类型文件
rules/                     # Phase 4 校验规则
```

Phase 2 中，`settings/schema.json` 保存整个项目的结构定义。由于当前领域模型已经包含 `TableRow`，小规模样例行或测试行可以随表定义一起序列化。大量生产行数据不在本阶段长期放入 schema 文件，后续 Phase 3/5 应移动到 `tables/`。

## JSON 格式

`settings/schema.json` 包含以下顶层字段：

- `schema_format_version`：schema 持久化文件格式版本号。
- `tables`：普通表、分组表、二维表定义列表。
- `enums`：枚举定义和枚举项列表。
- `metas`：Meta 定义和子字段列表。

`field_type`、`table_type`、`element_type` 等枚举值使用字符串值序列化。tuple 字段保存为 JSON 数组，加载时恢复为 tuple。可选字段沿用现有 dataclass 默认值。

## 校验与循环引用

反序列化必须先构建 `ProjectSchema`，再执行结构校验，只有结构合法后才返回。非法文件应尽早失败，并由领域层给出清晰的 `ValueError`；应用层后续可以把这些错误包装为项目文件错误。

Meta 引用环在 Phase 2 中视为非法。例如 `Meta A -> Meta B -> Meta A` 必须被拒绝，因为它会破坏编辑器展开、默认值生成、导出结构计算和校验遍历。

Table 引用环在 Phase 2 中可以被发现，但默认不阻塞加载。配置表之间互相引用可能是合法业务关系，因此领域层提供引用图和循环发现能力，不在本阶段一刀切拒绝。Phase 4 校验系统再根据规则把具体表循环判定为错误、警告或允许模式。

## 应用服务接入

`ProjectService` 新增 schema 专用方法：

- `schema_path(project) -> Path`
- `load_schema(project) -> ProjectSchema`
- `save_schema(project, schema) -> Project`

`save_schema` 使用与项目配置保存一致的原子写入风格。schema 文件维护独立 digest，避免保存业务 schema 时误用 `xtable.project.json` 的 digest。`Project` 增加 `schema_digest`，当 schema 文件不存在时默认为空字符串。

`load_schema` 在 `settings/schema.json` 不存在时返回空的 `ProjectSchema`，让新建项目可以在尚未创建任何业务结构时正常打开。

## 测试范围

测试需要覆盖：

- 字段、枚举、Meta、普通表、分组表、二维表、行数据和 tuple 字段的往返序列化。
- 根据 `table_type` 恢复正确的表子类。
- 拒绝非法字段类型和表类型字符串。
- 拒绝 Meta 引用循环。
- 能报告 Table 引用循环，但不因此拒绝 schema。
- 通过 `ProjectService` 保存和加载 schema 文件。
- `settings/schema.json` 被外部修改后拒绝过期保存。
- 领域模块继续不依赖 PySide6。

## 非目标

本设计不实现 UI 编辑、Excel/CSV 解析、完整校验诊断、业务规则文件或大规模表格行数据存储。这些仍然属于 Phase 3、Phase 4 和 Phase 5。
