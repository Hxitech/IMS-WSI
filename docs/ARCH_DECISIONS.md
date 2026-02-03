# 架构决策记录（ADR 摘要）

## 1) 切片格式支持策略
- 目标：先满足 OpenSlide（及其可用 fork/扩展）可覆盖的主流格式范围，作为 V0/V1 的兼容基线。
- 计划：
  - V0：验证 OpenSlide 对 svs、tiff、ndpi、mrxs 等的读取与多层金字塔访问；对无法直接读取的格式暂不承诺。
  - V1：引入 Bio-Formats/厂商 SDK 作为补充（待评估授权与部署复杂度）。

## 2) 模型分工
- 主模型：架构顾问（模块拆解、数据模型、接口边界、风险控制、验收设计）
- coder（gpt-5.2-mini）：前后端施工（脚手架、CRUD、队列 worker、测试、CI）

## 3) 核心技术路线（初稿）
- Viewer：OpenSeadragon（tile 渲染）
- Ingest：分片上传 → 入库任务 → 转码/索引/标签识别 → 元数据落库
- 存储：对象存储（S3/MinIO/本地）+ DB（Postgres/MySQL）+ Redis（队列/缓存）
- 标签识别：OCR + 条码/二维码 + 文件名规则引擎

