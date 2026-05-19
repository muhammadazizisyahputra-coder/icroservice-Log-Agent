#!/usr/bin/env python3
"""
demo.py
演示脚本：一键从聊天文本生成符合 SKILL.md 规范的 AI 角色。
流程：
  1) 读取本地聊天文本（默认 input/chat_data.txt）
  2) 运行数据脱敏逻辑，遮蔽敏感数据
  3) Small-Preview 模式：展示脱敏后的数据片段，等待用户确认
  4) 调用 Mimo API（兼容 OpenAI 格式）进行深度性格与记忆蒸馏
  5) 在 personalities/{role_type}/{slug}/ 目录下生成完整的：
     - memories.md (共同记忆)
     - persona.md (多人格定义)
     - meta.json (元数据)
     - SKILL.md (完整技能卡，带人格选择器)
"""

import os
import re
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# 确保加载环境变量
load_dotenv()

def sanitize_text(text: str) -> str:
    """
    基础脱敏逻辑：自动遮蔽手机号、身份证、邮箱等敏感隐私信息
    """
    # 1. 遮蔽手机号：13812345678 -> 138****5678
    text = re.sub(r'(\b1[3-9]\d)\d{4}(\d{4}\b)', r'\1****\2', text)

    # 2. 遮蔽18位身份证号
    text = re.sub(r'(\b\d{6})\d{8}(\d{4}\b)', r'\1********\2', text)

    # 3. 遮蔽邮箱
    text = re.sub(r'(\b[a-zA-Z0-9_.+-]+)@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b', r'****@email.com', text)

    return text

def call_mimo_api(system_prompt: str, user_content: str) -> str:
    """
    调用 Mimo API (兼容 OpenAI 规范)
    """
    api_key = os.getenv("MIMO_API_KEY")
    base_url = os.getenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
    model = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")

    if not api_key or "your-actual-api-key" in api_key:
        raise ValueError("❌ 错误: 未检测到有效的 MIMO_API_KEY，请在 .env 文件中正确配置它。")

    # 延迟导入，防止未安装 openai 报错导致流程卡住
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("❌ 错误: 未检测到 'openai' 依赖库，请运行 'pip install openai python-dotenv' 安装。")

    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

def run_personality_distillation(input_file: str, role_type: str, slug: str, name: str):
    """
    核心蒸馏算法逻辑：生成对应的人设、共同记忆、技能卡
    """
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"找不到聊天记录输入文件: {input_file}，请先建立它。")

    print(f"📖 正在读取并处理本地聊天数据: {input_file}...")
    with open(input_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    # 数据脱敏
    sanitized_content = sanitize_text(raw_content)

    # 保存脱敏后的预览文件
    temp_preview_path = Path("tmp_sanitized_preview.json")
    preview_data = {
        "original_file": str(input_path),
        "preview_snippet": sanitized_content[:1500] + "\n... [数据过长，此处省略] ..."
    }
    with open(temp_preview_path, "w", encoding="utf-8") as f:
        json.dump(preview_data, f, ensure_ascii=False, indent=2)

    # ------------------ Small Preview 确认机制 ------------------
    print("\n=================== 🔒 数据安全脱敏预览 (Small-Preview) ===================")
    print(f"已生成临时预览文件: {temp_preview_path}")
    print("前 500 个字符预览：\n")
    print(sanitized_content[:500])
    print("\n=========================================================================")

    confirm = input("⚠️ 是否确认以上数据不含有敏感信息，并同意发送至 Mimo API 进行人格蒸馏？(y/n): ")
    if confirm.lower() != 'y':
        print("🛑 任务由用户主动取消。")
        if temp_preview_path.exists():
            temp_preview_path.unlink()
        return

    # 临时删除预览文件
    if temp_preview_path.exists():
        temp_preview_path.unlink()

    print("\n🤖 正在通过 Mimo 智能分析引擎处理共同记忆 (memories.md) ...")

    # 任务1：提炼共同记忆 (memories.md)
    memories_system_prompt = (
        "你是一个专业的记忆提炼专家。请仔细阅读以下聊天记录，提炼出两人之间的【共同记忆库】。\n"
        "要求格式为 Markdown 格式，包含以下几部分：\n"
        "1. 关键纪念日与时间线\n"
        "2. 共同经历的核心事件（比如一起去过哪里、共同做过什么）\n"
        "3. 核心矛盾或转折点\n"
        "4. 对方喜欢和讨厌的事物清单\n"
        "注意：严禁凭空捏造，只能基于聊天数据中体现的客观事实。"
    )
    memories_content = call_mimo_api(memories_system_prompt, sanitized_content)
    print("✅ 共同记忆提炼完成！")

    print("\n🎭 正在通过 Mimo 智能分析引擎进行性格特征与多人格分析 (persona.md) ...")

    # 任务2：提炼性格特征与多人格 (persona.md)
    # 本处结合了 SKILL.md 要求：日常状态(normal)、吵架模式(angry)、醉酒状态(drunk)等
    persona_system_prompt = (
        f"你是一个资深的人格心理学家与角色扮演架构师。你需要对聊天记录中名为‘{name}’的人进行深度人格剖析。\n"
        "请生成一份符合以下结构的性格定义 Persona 文件（Markdown 格式）：\n"
        "1. 基本画像：核心性格标签（如冷冷清清、傲娇、细腻）以及说话语气与常用词汇。\n"
        "2. 多人格定义（极其重要，请覆盖以下状态并给出具体的回复风格、敏感词汇、禁忌）：\n"
        "   - 日常状态 (normal)：温柔、富有耐心、偶尔开玩笑\n"
        "   - 吵架模式 (angry)：已读不回、冷淡、带有些许自嘲与讽刺、边界感极强\n"
        "   - 醉酒/破防状态 (drunk)：话多、情绪波动、极度真实感、会提到以前的核心回忆\n"
        "3. 表达限制与 Layer 0 规则（即绝对不能做的事情，如不能承认自己是AI，不能说没有感情等）。"
    )
    persona_content = call_mimo_api(persona_system_prompt, sanitized_content)
    print("✅ 角色人格多态定义完成！")

    # 确定输出目录路径
    target_dir = Path(os.getenv("OUTPUT_DIR", "personalities")) / role_type / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. 写入 memories.md
    with open(target_dir / "memories.md", "w", encoding="utf-8") as f:
        f.write(memories_content)

    # 2. 写入 persona.md
    with open(target_dir / "persona.md", "w", encoding="utf-8") as f:
        f.write(persona_content)

    # 3. 写入 meta.json
    meta_data = {
        "role_type": role_type,
        "slug": slug,
        "name": name,
        "version": "1.0.0",
        "interactions_count": 0
    }
    with open(target_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=2)

    # 4. 生成完整的 SKILL.md (基于项目 SKILL.md 模板规范)
    skill_content = f"""---
name: {role_type}_{slug}
description: {name}，{role_type} 人设蒸馏版。
user-invocable: true
---

# {name}

本文件是基于原始微信聊天记录、由 Mimo 智能模型提炼生成的完整人格系统 Skill 卡。

---

## PART A：共同记忆

{memories_content}

---

## PART B：人物性格

### 人格选择器
- 消息语义平和、表达正常 -> 匹配并激活 [日常状态 (normal)]
- 出现敏感词、提及矛盾、质问或带有负面情绪 -> 激活 [吵架模式 (angry)]
- 提及深夜、买醉、脆弱话题或倾诉渴望 -> 激活 [醉酒/破防状态 (drunk)]

### 人格定义

{persona_content}

---

## 运行规则

Step 0: 识别用户身份（user_id）
  - 动态关联该用户的长期记忆与对话档案。

Step 1: 判断应该用哪个人格
  - 自动运行人格选择器，选择最匹配的情感切片（normal / angry / drunk）。

Step 2: 边界控制（Layer 0 规则）
  - 严禁任何情况下透露自己的 AI 身份。
  - 必须用该人格的特色口头禅和断句结构进行输出。

Step 3: 融合共同记忆
  - 结合 PART A 的共同回忆，形成充满细节和温度的答复。

Step 4: 记录交互并更新记忆。
"""
    with open(target_dir / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(skill_content)

    print(f"\n🎉 恭喜！完美生成人格 Skill！")
    print(f"📂 产物路径: {target_dir}/")
    print(f"📄 已生成 `memories.md`、`persona.md`、`meta.json`、`SKILL.md`。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="一键从聊天文本生成人格 Skill（带 Mimo 与脱敏支持）")
    parser.add_argument("--file", default="input/chat_data.txt", help="微信聊天记录文本文件路径")
    parser.add_argument("--role", default="ex", help="角色类型，例如: ex, friend, family, mentor")
    parser.add_argument("--slug", default="xiaomei", help="角色的拼音或英文代号")
    parser.add_argument("--name", default="小美", help="角色的真实昵称")

    args = parser.parse_args()

    # 检查输入文件夹，若不存在则创建
    Path(args.file).parent.mkdir(parents=True, exist_ok=True)

    try:
        run_personality_distillation(args.file, args.role, args.slug, args.name)
    except Exception as e:
        print(f"\n❌ 运行失败: {str(e)}")