# 系统架构（简要）

本文件说明人格蒸馏系统的总体架构与数据流，供开发者参考。

- Parser 层：负责将原始数据（聊天导出、社交媒体导出、照片）解析成统一的消息条目。
- 分析层：使用 prompts（memories_analyzer / persona_analyzer / role_selector）对统一条目进行抽取与分类。
- 生成层：将结构化输出通过 builder prompts 转化为可读的 memories.md、persona.md。
- 持久化层：使用 skill_writer 将文件写入 personalities/{role}/{slug}/，并由 version_manager 管理历史版本。
- 用户记忆：user_memory_manager 提供 per-user 长期记忆存储与简单 API。
- RAG：memory_embeddings 提供记忆向量化与语义检索接口（占位实现）。

