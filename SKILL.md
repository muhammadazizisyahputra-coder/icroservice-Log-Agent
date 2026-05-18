---
name: create-personality
description: "蒸馏任何人的人格模型 - 支持多人格、多角色、长期记忆。从聊天记录到 AI 人格 Skill。"
argument-hint: "[personality-name-or-slug]"
version: "1.0.0"
user-invocable: true
allowed-tools: "Read, Write, Edit, Bash"
---

> **Language / 语言**: This skill supports both English and Chinese. Detect the user's language from their first message and respond in the same language throughout.
>
> 本 Skill 支持中英文。根据用户第一条消息的语言，全程使用同一语言回复。

# 人格蒸馏系统 - 创建器（Claude Code 版）

## 触发条件

当用户说以下任意内容时启动：
- `/create-personality`
- `/create`
- "帮我创建一个人格"
- "我想蒸馏一个人格"
- "给我做一个 XX 的 skill"

当用户对已有人格 Skill 说以下内容时，进入进化模式：
- "我有新聊天记录" / "追加"
- "这不对" / "不对" / "她不会这样"
- `/update-personality {slug}`

当用户说 `/list-personalities` 时列出所有已生成的人格。

---

## 工具使用规则

本 Skill 运行在 Claude Code 环境，使用以下工具：

| 任务 | 使用工具 |
|------|----------|
| 读取 PDF 文档 | `Read` 工具（原生支持 PDF） |
| 读取图片截图 | `Read` 工具（原生支持图片） |
| 读取 MD/TXT 文件 | `Read` 工具 |
| 解析微信聊天记录 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/wechat_parser.py` |
| 解析 iMessage | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/imessage_parser.py` |
| 解析短信 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/sms_parser.py` |
| 分析照片元数据 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/photo_analyzer.py` |
| 解析社交媒体导出 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/social_media_parser.py` |
| 解析钉钉记录 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/dingtalk_parser.py` |
| 解析 QQ 记录 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/qq_parser.py` |
| 写入/更新 Skill 文件 | `Write` / `Edit` 工具 |
| 版本管理 | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |
| 列出已有 Skill | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list` |

**基础目录**：Skill 文件写入 `./personalities/{role_type}/{slug}/`（相对于本项目目录）。

---

## 主流程：创建新人格 Skill

### Step 1：基础信息录入（4 个问题）

参考 `${CLAUDE_SKILL_DIR}/prompts/intake.md` 的问题序列，只问 4 个问题：

1. **角色类型**（新增）：前任、朋友、家人、导师、同事、其他
2. **昵称/代号**（必填）
3. **基本信息**（一句话，根据角色类型动态调整）
4. **性格画像**（一句话：MBTI、星座、依恋类型、恋爱标签、你对她的印象）

除昵称外均可跳过。收集完后汇总确认再进入下一步。

### Step 2：原材料导入

[同原始 SKILL.md，支持所有数据格式]

### Step 3：分析原材料

将收集到的所有原材料和用户填写的基础信息汇总，按以下三条线分析：

**线路 A（Memories Skill）**：
- 参考 `${CLAUDE_SKILL_DIR}/prompts/memories_analyzer.md`
- 根据角色类型调整提取维度（role_selector.md）

**线路 B（Persona）**：
- 参考 `${CLAUDE_SKILL_DIR}/prompts/persona_analyzer.md`
- 自动识别多个人格（personality_selector.md）

**线路 C（用户档案）**【新增】：
- 参考 `${CLAUDE_SKILL_DIR}/prompts/user_profile_extractor.md`
- 为后续长期记忆系统准备基础

### Step 4：生成并预览

参考 `${CLAUDE_SKILL_DIR}/prompts/memories_builder.md` 生成 Memories Skill 内容。
参考 `${CLAUDE_SKILL_DIR}/prompts/persona_builder.md` 生成 Persona 内容（支持多人格）。

向用户展示摘要（各 5-8 行），询问：
```
共同记忆摘要：
  - 关系类型：{role_type}
  - 在一起/认识：{duration}
  - 重要时刻：{N} 个
  - 日常仪式：{xxx}
  ...

Persona 摘要：
  - 人格总数：{N} 个
  - 默认人格：{日常状态}
  - 包含人格：{列表}
  - 核心特征：{xxx}
  ...

确认生成？还是需要调整？
```

### Step 5：写入文件

用户确认后，执行以下写入操作：

**1. 创建目录结构**（用 Bash）：
```bash
mkdir -p personalities/{role_type}/{slug}/versions
mkdir -p personalities/{role_type}/{slug}/knowledge/chats
mkdir -p personalities/{role_type}/{slug}/knowledge/photos
mkdir -p personalities/{role_type}/{slug}/knowledge/social
mkdir -p personalities/{role_type}/{slug}/user_memories
```

**2. 写入核心文件**（用 Write 工具）：
- 路径：`personalities/{role_type}/{slug}/memories.md`
- 路径：`personalities/{role_type}/{slug}/persona.md`
- 路径：`personalities/{role_type}/{slug}/meta.json`
- 路径：`personalities/{role_type}/{slug}/SKILL.md`

**3. meta.json 结构**：
```json
{
  "name": "{name}",
  "slug": "{slug}",
  "role_type": "{role_type}",
  "created_at": "{ISO时间}",
  "updated_at": "{ISO时间}",
  "version": "v1",
  "profile": {
    "role_type": "{role_type}",
    "duration": "{duration}",
    "how_met": "{how_met}",
    "relationship_status": "{status}",
    "occupation": "{occupation}"
  },
  "tags": {
    "personality": [...],
    "attachment_style": "{attachment_style}"
  },
  "personalities": {
    "normal": "日常状态",
    "angry": "吵架模式",
    "drunk": "醉酒状态"
  },
  "impression": "{impression}",
  "knowledge_sources": [...已导入文件列表],
  "memory_mode": "multi-user",
  "corrections_count": 0
}
```

**4. 生成完整 SKILL.md**（用 Write 工具）：
路径：`personalities/{role_type}/{slug}/SKILL.md`

SKILL.md 结构：
```markdown
---
name: {role_type}_{slug}
description: {name}，{identity}
user-invocable: true
---

# {name}

{identity}

---

## PART A：共同记忆

{memories.md 全部内容}

---

## PART B：人物性格

### 人格选择器

{personality_selector.md 的人格切换规则}

### 人格定义

{persona.md 全部内容}

---

## 运行规则

Step 0: 识别用户身份（user_id）【新增】
  - 加载该用户的长期记忆

Step 1: 判断应该用哪个人格
  - 根据用户消息的语义
  - 选择最匹配的人格

Step 2: 判断会不会回答
  - 该人格的 Layer 0 规则

Step 3: 调用共同记忆
  - 所有用户共享的记忆
  - 融合用户专属记忆【新增】

Step 4: 输出回答
  - 用该人格的表达风格
  - 记录交互历史【新增】

**PART B 的 Layer 0 规则永远优先，任何情况下不得违背。**
```

告知用户：
```
✅ 人格 Skill 已创建！

文件位置：personalities/{role_type}/{slug}/
触发词：/{role_type}/{slug}（完整版）
       /{role_type}/{slug}/normal（日常状态）
       /{role_type}/{slug}/angry（吵架模式）
       /{role_type}/{slug}-memories（仅共同记忆）
       /{role_type}/{slug}-persona（仅人物性格）

如果用起来感觉哪里不对，直接说"她不会这样"，我来更新。
```

---

## 进化模式：追加文件

[同原始 SKILL.md，支持增量 Merge 和版本管理]

---

## 进化模式：对话纠正

[同原始 SKILL.md，支持全局纠正和用户特有纠正]

---

## 管理命令

`/list-personalities`：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py --action list --base-dir ./personalities
```

`/personality-rollback {role_type}/{slug} {version}`：
```bash
python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py --action rollback --slug {role_type}/{slug} --version {version} --base-dir ./personalities
```

`/delete-personality {role_type}/{slug}`：
确认后执行：
```bash
rm -rf personalities/{role_type}/{slug}
```
