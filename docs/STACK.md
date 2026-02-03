# 技术栈与工作方式（V0）

## 技术栈选择
- 后端：FastAPI（Python）
- 前端：Vue
- 存储：本地磁盘（后续可替换对象存储）
- 切片读取：OpenSlide（优先覆盖其可读格式）

## 开发方式
- coder（gpt-5.2-mini）：优先用于脚手架与日常施工
- 主模型：阶段性 code review；如 coder 效果不佳，切换主模型直接 coding

## 约定
- 所有设计文档输出在 `/home/project/docs`
- 需求文档输出在 `/home/project/requirements`
- 图输出在 `/home/project/diagrams`
