# 增量 Merge Prompt

## 目标
当用户提供新材料时，判定这些新材料应追加到哪个部分（memories / persona / 两者），并生成增量 patch（以供写入）。

## 流程
1. 将新材料拆成条目（按时间/句子）。
2. 对比现有 memories.md / persona.md：
   - 如果是新事实（新日期/事件/偏好） → append 到 memories
   - 如果是沟通风格/口头禅/情感反应 → append 到 persona
   - 如果冲突 → 标注冲突并提示用户选择（保留/更新/都保留并标注时间）
3. 输出格式（示例）：

=== memories.md 更新 ===
[追加到"重要时刻"]
- 2026-05-01: 一起去看电影...

=== persona.md 更新 ===
[追加到"Layer 2/口头禅"]
- 新口头禅:"哎呀"

本次更新摘要：
- memories: +N 条
- persona: +M 条
