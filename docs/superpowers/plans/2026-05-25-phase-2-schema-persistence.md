# Phase 2 Schema 持久化实施计划

> **给 agentic worker 的要求：** 实施本计划时需要使用 `superpowers:subagent-driven-development`（推荐）或 `superpowers:executing-plans`。任务使用复选框语法跟踪。

**目标：** 通过带版本号的 JSON schema 文件保存并重新加载 Phase 2 的 `ProjectSchema` 结构，同时实现 Meta 循环引用阻塞和 Table 引用循环发现。

**架构：** 新增 `xtable.domain.serialization` 负责纯模型与字典转换；`xtable.domain.models` 继续负责结构校验和引用图能力；`ProjectService` 增加 schema 文件加载与保存方法，并复用现有原子写入和冲突检测模式。业务 schema 保存到 `settings/schema.json`，与 `xtable.project.json` 分离。

**技术栈：** Python 3.11+、dataclass、标准库 `json`/`pathlib`、pytest、现有 XTable domain/application 模块。

---

## 文件结构

- 新建 `src/xtable/domain/serialization.py`
  - 负责 `project_schema_to_dict` 和 `project_schema_from_dict`。
  - 不包含文件 I/O，不导入 PySide6。
- 修改 `src/xtable/domain/models.py`
  - 增加 Meta 循环引用校验。
  - 增加 Table 引用图和引用循环发现方法。
- 修改 `src/xtable/domain/project.py`
  - 为 `Project` 增加 `schema_digest`。
- 修改 `src/xtable/application/project_service.py`
  - 增加 schema 路径、加载和保存方法。
  - 为 schema 文件使用原子 JSON 写入。
- 修改 `src/xtable/domain/__init__.py`
  - 导出 schema 序列化辅助函数。
- 新建 `tests/test_phase2_schema_serialization.py`
  - 覆盖 codec 往返、非法类型、Meta 循环、Table 循环发现。
- 修改 `tests/test_project_files.py`
  - 覆盖 `ProjectService` schema 保存、加载和外部修改冲突。

## Task 1：领域 schema 序列化 codec

**文件：**

- 新建 `src/xtable/domain/serialization.py`
- 新建测试 `tests/test_phase2_schema_serialization.py`

**步骤：**

- [x] 先写失败测试：构造包含 Enum、Meta、普通表、分组表、二维表、字段、行数据和 tuple 字段的 `ProjectSchema`，断言 `project_schema_to_dict` 与 `project_schema_from_dict` 可以完整往返。
- [x] 运行 `python -m pytest tests/test_phase2_schema_serialization.py -v`，确认失败原因为缺少 `xtable.domain.serialization`。
- [x] 新增 `project_schema_to_dict(schema)`，输出顶层 `schema_format_version`、`enums`、`metas`、`tables`。
- [x] 新增 `project_schema_from_dict(data)`，按版本号恢复 `ProjectSchema`，并执行 `validate_structure()`。
- [x] 将 `FieldType`、`TableType`、`element_type` 保存为字符串，加载时恢复为枚举。
- [x] 将 tuple 字段保存为数组，加载时恢复为 tuple。
- [x] 运行 `python -m pytest tests/test_phase2_schema_serialization.py -v`，确认 codec 测试通过。

## Task 2：Meta 循环阻塞与 Table 循环发现

**文件：**

- 修改 `src/xtable/domain/models.py`
- 修改 `tests/test_phase2_schema_serialization.py`

**步骤：**

- [x] 先写失败测试：`Meta A -> Meta B -> Meta A` 调用 `validate_structure()` 时应抛出包含 `Meta reference cycle` 的 `ValueError`。
- [x] 先写失败测试：Table 互相引用时，`table_reference_graph()` 应返回引用图，`find_table_reference_cycles()` 应返回循环路径，但 `validate_structure()` 不应阻塞。
- [x] 运行定向测试，确认失败原因为缺少引用图方法和 Meta 环校验。
- [x] 在 `ProjectSchema` 中新增 `table_reference_graph()`。
- [x] 在 `ProjectSchema` 中新增 `find_table_reference_cycles()`。
- [x] 新增内部 `_find_cycles(graph)`，使用 DFS 发现并规范化循环路径。
- [x] 新增 `_validate_meta_reference_cycles()`，并在 `validate_structure()` 末尾调用。
- [x] 调整反序列化逻辑：加载 tables 时先放入 `schema.tables`，再统一执行 `validate_structure()`，支持从文件恢复表之间的互相引用。
- [x] 运行 `python -m pytest tests/test_phase2_schema_serialization.py -v`，确认通过。

## Task 3：ProjectService schema 文件持久化

**文件：**

- 修改 `src/xtable/domain/project.py`
- 修改 `src/xtable/application/project_service.py`
- 修改 `tests/test_project_files.py`

**步骤：**

- [x] 先写失败测试：`ProjectService.save_schema(project, schema)` 应创建 `settings/schema.json`，并设置 `schema_digest`。
- [x] 先写失败测试：`ProjectService.load_schema(project)` 应从 `settings/schema.json` 恢复 `ProjectSchema`。
- [x] 先写失败测试：schema 文件不存在时，`load_schema()` 返回空 `ProjectSchema`。
- [x] 先写失败测试：schema 文件被外部修改后，旧 `schema_digest` 保存应抛出 `ProjectConflictError`，类型为 `EXTERNALLY_MODIFIED`。
- [x] 运行定向测试，确认失败原因为缺少 `schema_digest`、`save_schema` 和 `load_schema`。
- [x] 在 `Project` 上增加 `schema_digest: str = ""`。
- [x] 在 `ProjectService` 中增加 `schema_path(project)`，默认指向 `settings/schema.json`。
- [x] 在 `ProjectService` 中增加 `load_schema(project)`，不存在文件时返回空 schema，存在文件时读取 JSON 并调用 `project_schema_from_dict`。
- [x] 在 `ProjectService` 中增加 `save_schema(project, schema)`，保存前执行 `schema.validate_structure()`，并拒绝只读或外部修改文件。
- [x] 增加 `_write_json_atomic(path, payload)`，用于 schema JSON 原子写入。
- [x] 运行 `python -m pytest tests/test_project_files.py -v`，确认通过。

## Task 4：包导出与全量验证

**文件：**

- 修改 `src/xtable/domain/__init__.py`

**步骤：**

- [x] 检查 `src/xtable/domain/__init__.py`，确认已有 domain API 导出。
- [x] 导出 `project_schema_from_dict` 和 `project_schema_to_dict`。
- [x] 运行 `python -m pytest`。
- [x] 运行 `python -m compileall -q src tests`。
- [x] 保留既有未提交文档改动，不自动混入提交。

## 验证结果

已执行：

```bash
python -m pytest
python -m compileall -q src tests
```

结果：

```text
81 passed
compileall exit 0
```

## 自检

- 设计覆盖：版本化 schema 格式、完整结构往返、表子类恢复、Meta 循环阻塞、Table 循环发现、应用层 schema 保存加载、外部修改冲突和全量验证均已覆盖。
- 占位检查：本文档没有保留待补内容。
- 类型一致性：计划和实现统一使用 `ProjectSchema`、`Project.schema_digest`、`ProjectService.schema_path`、`ProjectService.load_schema`、`ProjectService.save_schema`、`project_schema_to_dict` 和 `project_schema_from_dict`。
