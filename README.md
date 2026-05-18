# 人格蒸馏系统 (Personality Distillation System)

🎯 **将任何人的聊天记录转化为 AI 人格模型**

> 从微信、iMessage、短信、社交媒体中蒸馏一个人的独特人格，让 AI 能像他们一样思考、说话、行动。

## ✨ 核心特性

### 🎭 多人格系统
- **日常状态** - 正常聊天、温柔、耐心
- **吵架模式** - 冷战、已读不回、讽刺
- **醉酒状态** - 话多、诚实、容易哭
- **自定义人格** - 支持任意数量的人格组合

### 👥 多角色支持
- ❤️ **前任** - 情感线、依恋方式、浪漫回忆
- 👯 **朋友** - 玩笑、共同经历、相互支持
- 👨‍👩‍👧 **家人** - 家庭故事、关心方式、生活习惯
- 🎓 **导师** - 教学风格、专业特长、重要教导
- 💼 **同事** - 工作风格、项目经历、职业特色

### 🧠 智能记忆系统
- **共同记忆库** - 所有用户共享的记忆
- **用户专属记忆** - 每个用户独立的长期记忆
- **自动档案提取** - 智能识别用户身份信息
- **交互历史记录** - 完整的对话追踪和学习

### 📚 数据导入支持

| 来源 | 格式 | 状态 |
|------|------|------|
| **微信** | txt/html (WechatExporter) | ✅ 支持 |
| **iMessage** | chat.db / 导出文件 | ✅ 支持 |
| **短信** | XML/CSV (Android Backup) | ✅ 支持 |
| **照片** | JPEG/PNG (EXIF 元数据) | ✅ 支持 |
| **微博** | JSON 导出 | ✅ 支持 |
| **豆瓣** | JSON/HTML 导出 | ✅ 支持 |
| **小红书** | JSON 导出 | ✅ 支持 |
| **Instagram** | JSON 数据导出 | ✅ 支持 |
| **钉钉** | 导出文件 | ✅ 支持 |
| **QQ** | 导出文件 | ✅ 支持 |

## 🚀 快速开始

### 1️⃣ 安装

```bash
# 克隆项目
git clone https://github.com/muhammadazizisyahputra-coder/icroservice-Log-Agent.git
cd icroservice-Log-Agent

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 创建第一个人格

```bash
# 启动交互式创建向导
python create_personality.py

# 或使用 Claude Code（推荐）
/create-personality
```

### 3️⃣ 使用已创建的人格

```bash
# 调用完整人格（Memories + Persona）
/{slug}

# 仅调用共同记忆
/{slug}-memories

# 仅调用人物性格
/{slug}-persona

# 调用特定人格状态
/{slug}/angry  # 吵架模式
/{slug}/drunk  # 醉酒状态
```

## 📁 项目结构

```
icroservice-Log-Agent/
├── README.md                          # 本文件
├── SKILL.md                           # Claude Code 入口点
├── requirements.txt                   # Python 依赖
│
├── prompts/                           # 📌 Prompt 模板库（核心）
│   ├── intake.md                      # 基础信息录入问卷
│   ├── role_selector.md               # 角色类型识别（新增）
│   ├── memories_analyzer.md           # 共同记忆提取维度
│   ├── persona_analyzer.md            # 性格行为分析
│   ├── memories_builder.md            # memories.md 生成模板
│   ├── persona_builder.md             # persona.md 生成模板（支持多人格）
│   ├── personality_selector.md        # 人格切换规则（新增）
│   ├── merger.md                      # 增量 Merge 逻辑
│   └── correction_handler.md          # 对话纠正处理
│
├── tools/                             # 📌 工具库
│   ├── wechat_parser.py               # 微信解析
│   ├── imessage_parser.py             # iMessage 解析
│   ├── sms_parser.py                  # 短信解析
│   ├── photo_analyzer.py              # 照片元数据分析
│   ├── social_media_parser.py         # 社交媒体解析
│   ├── dingtalk_parser.py             # 钉钉解析（新增）
│   ├── qq_parser.py                   # QQ 解析（新增）
│   ├── skill_writer.py                # Skill 文件管理（支持多人格）
│   ├── version_manager.py             # 版本管理
│   ├── user_memory_manager.py         # 用户记忆管理（新增）
│   └── memory_embeddings.py           # 向量化与 RAG 检索（可选）
│
├── personalities/                     # 生成的人格库（自动创建）
│   ├── {role_type}/                   # 按角色分类
│   │   └── {slug}/
│   │       ├── SKILL.md               # 完整人格 Skill
│   │       ├── memories.md            # 共同记忆
│   │       ├── persona.md             # 多人格定义
│   │       ├── meta.json              # 元数据
│   │       ├── versions/              # 版本存档
│   │       ├── knowledge/             # 原始数据
│   │       └── user_memories/         # 用户专属记忆（新增）
│   │           └── {user_id}.json
│
├── docs/                              # 文档和指南
│   ├── ARCHITECTURE.md                # 系统架构设计
│   ├── MULTI_PERSONALITY.md           # 多人格系统指南
│   ├── MULTI_ROLE.md                  # 多角色支持指南
│   ├── LONG_TERM_MEMORY.md            # 长期记忆系统
│   ├── RAG_RETRIEVAL.md               # RAG 检索系统
│   ├── API_REFERENCE.md               # API 参考
│   └── EXAMPLES.md                    # 使用示例
│
├── tests/                             # 测试套件
│   ├── test_parsers.py                # 数据解析测试
│   ├── test_personality.py            # 人格生成测试
│   ├── test_memory.py                 # 记忆系统测试
│   └── test_integration.py            # 集成测试
│
├── examples/                          # 示例项目
│   ├── ex_skill_example.md            # 前任 Skill 示例
│   ├── friend_skill_example.md        # 朋友 Skill 示例
│   └── mentor_skill_example.md        # 导师 Skill 示例
│
└── config/                            # 配置文件（可选）
    └── default_config.json            # 默认配置
```

## 🎯 核心概念

### 人格结构（Persona）

每个人格由 **5 层结构** 组成：

```
Layer 0: 核心规则
  └─ 在什么情况下会怎么做（优先级最高）

Layer 1: 身份
  └─ 职业、MBTI、依恋类型、生活背景

Layer 2: 表达风格
  └─ 口头禅、高频词、句式、emoji 使用习惯

Layer 3: 情感逻辑
  └─ 什么触发什么情绪、如何表达不开心

Layer 4: 关系行为
  └─ 怎么处理冲突、怎么表达爱意、关系期望
```

### 共同记忆库（Memories）

```
关系时间线（何时发生）
  ├─ 重要日期：在一起、第一次...、分手
  ├─ 里程碑：见家长、同居、重要旅行
  └─ 转折点：重大争吵、冷战、复合

共同日常与仪式（怎么相处）
  ├─ 日常活动：周末做什么、每天怎么过
  ├─ 共同爱好：一起看什么、一起玩什么
  ├─ 专属仪式：晚安消息、纪念日庆祝
  └─ 专属语言：昵称、inside jokes、暗号

她的偏好（什么最开心）
  ├─ 吃：喜欢的食物、常去的餐厅、奶茶口味
  ├─ 玩：喜欢的地方、旅行风格、娱乐类型
  └─ 送礼：喜欢什么、送礼风格、仪式感

情感模式（什么时候怎样）
  ├─ 开心��：什么让她开心、表现方式
  ├─ 不开心时：什么让她生气、信号识别
  ├─ 吵架时：导火索、升级方式、冷战特点、和解方式
  └─ 想你时：怎么表达思念、频率
```

## 📊 数据流程

```
原始数据 (微信/iMessage/照片/等)
    ↓
[Parser 层] — 统一格式转换
    ↓
[双轨分析]
    ├─ Track A: memories_analyzer → 共同记忆
    ├─ Track B: persona_analyzer → 人物性格
    └─ Track C: user_profile_extractor → 用户档案 (新增)
    ↓
[生成层] — 结构化输出
    ├─ memories.md (共同记忆)
    ├─ persona.md (多人格定义)
    ├─ user_memories/{user_id}.json (用户专属) (新增)
    └─ meta.json (元数据)
    ↓
[组装层] — 生成 Skill
    ├─ SKILL.md (完整 Skill，包含人格选择器)
    └─ versions/ (版本存档)
    ↓
✅ 完成！可以调用使用
```

## 🔄 使用流程

### 创建流程（5 步）

```
Step 1: 基础信息录入 (3 个问题)
  ├─ Q0: 她是谁？(角色类型)
  ├─ Q1: 昵称/代号
  └─ Q2: 基本信息 + Q3: 性格画像

Step 2: 原材料导入 (可选，可混用)
  ├─ A: 微信聊天记录
  ├─ B: iMessage / 短信
  ├─ C: 照片
  ├─ D: 社交媒体
  └─ E: PDF / 图片 / 直接粘贴

Step 3: 分析原材料
  ├─ Track A: 提取共同记忆
  ├─ Track B: 分析人物性格
  └─ Track C: 提取用户档案

Step 4: 生成并预览
  ├─ 展示记忆摘要
  ├─ 展示人格摘要
  └─ 展示人格列表

Step 5: 写入文件并发布
  ├─ 创建目录结构
  ├─ 写入 memories.md
  ├─ 写入 persona.md (包含多人格)
  ├─ 写入 meta.json
  └─ 生成 SKILL.md (包含人格选择器)
```

## 🛠️ API 参考

### 核心函数

#### Parser 函数

```python
# 微信
parse_wechat(file_path, target_name) -> list[dict]

# iMessage
parse_imessage(file_path, target) -> list[dict]
parse_chat_db(target) -> list[dict]  # 直接读取

# 短信
parse_sms(file_path, target) -> list[dict]

# 照片
analyze_photos(directory) -> list[dict]

# 社交媒体
parse_weibo(file_path, target) -> list[dict]
parse_douban(file_path, target) -> list[dict]
parse_xiaohongshu(file_path, target) -> list[dict]
parse_instagram(file_path, target) -> list[dict]
```

## 📝 使用示例

### 示例 1：创建前任 Skill

```bash
/create-personality
> 她是谁？→ 前任
> 昵称？→ 小美
> 基本信息？→ 在一起三年 大学同学 分手一年 她做设计
> 性格画像？→ ENFP 双子座 焦虑型 爱撒娇 翻旧账

# 生成 personalities/ex/xiaomei/SKILL.md
# 调用方式：/ex/xiaomei
```

## 📄 许可证

MIT License

## 👤 作者

**muhammadazizisyahputra-coder**

基于 **perkfly/ex-skill** 的启发和扩展
