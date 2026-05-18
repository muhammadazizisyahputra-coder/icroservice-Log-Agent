#!/usr/bin/env python3
"""
Builder: 将 simple_analyzer 输出和 prompts 模板渲染为 memories.md 和 persona.md，
然后调用 tools/skill_writer.py 生成最终 Skill 文件。

用法示例：
  python tools/builder.py --role ex --slug xiaomei --name "小美" --analysis-dir ./tmp --base-dir ./personalities

如果你有 LLM，可把 prompts/*.md 内容和分析数据发送给 LLM 来生成高质量结果；当前脚本做最小化渲染。
"""
import argparse
from pathlib import Path
import json
import subprocess


def render_memories(name, mem_obj, template_path: Path=None):
    lines = []
    lines.append(f"# {name} — 共同记忆\n")
    lines.append("## 关系概览\n")
    lines.append(f"首次记录：{mem_obj.get('first_seen','')}，最近记录：{mem_obj.get('last_seen','')}\n")
    lines.append("---\n")
    lines.append("## 重要时刻\n")
    for d in mem_obj.get('important_dates',[]):
        lines.append(f"- {d}: (见聊天记录)\n")
    lines.append("---\n")
    lines.append("## 日常与仪式\n")
    lines.append("### 你们的日常\n")
    if mem_obj.get('daily_habits'):
        for h in mem_obj['daily_habits']:
            lines.append(f"- {h}\n")
    else:
        lines.append("- （暂无足够信息，建议追加聊天记录）\n")
    lines.append("\n### 共同爱好\n")
    lines.append("- （由聊天记录推断）\n")
    lines.append("\n### 只有你们懂的\n")
    lines.append("- （inside jokes / 昵称）\n")
    lines.append("---\n")
    lines.append("## 她/他/TA 的偏好\n")
    lines.append("### 吃\n")
    prefs = mem_obj.get('preferences',[])
    if prefs:
        for p in prefs:
            lines.append(f"- {p}\n")
    else:
        lines.append("- （暂无）\n")
    lines.append("---\n")
    lines.append("## 情感模式\n")
    lines.append("### 不开心的时候\n")
    conf = mem_obj.get('conflict_signals',[])
    if conf:
        for c in conf:
            lines.append(f"- 常见信号：{c}\n")
    else:
        lines.append("- （暂无）\n")
    lines.append("\n## 记忆使用说明\n")
    lines.append("当用户提到某个日期 / 吃什么 / 吵架等话题时，优先调用对应节。\n")
    return "\n".join(lines)


def render_persona(name, persona_obj, template_path: Path=None):
    lines = []
    lines.append(f"# {name} — Persona\n")
    lines.append("---\n")
    lines.append("## 人格列表\n")
    # normal
    lines.append("### 人格：normal （日常）\n")
    lines.append("Layer 0：核心规则\n")
    lines.append("- 在大多数日常场景中，保持温和、略带撒娇。\n")
    lines.append("Layer 1：身份\n")
    lines.append(f"- 常见说话者：{', '.join(persona_obj.get('top_senders',[]))}\n")
    lines.append("Layer 2：表达风格\n")
    lines.append(f"- 高频词：{', '.join(persona_obj.get('top_words',[])[:10])}\n")
    es = persona_obj.get('expression_style',{})
    lines.append(f"- 平均句长：{es.get('avg_len',0)} 字；emoji 频率：{es.get('emoji_freq',0)}；感叹号频率：{es.get('exclaim_freq',0)}\n")
    lines.append("Layer 3：情感逻辑\n")
    lines.append(f"- 爱的信号示例：{', '.join(persona_obj.get('love_signals',[]))}\n")
    lines.append(f"- 生气信号示例：{', '.join(persona_obj.get('anger_signals',[]))}\n")
    lines.append("Layer 4：关系行为\n")
    lines.append("- 吵架模式：依据聊天记录可能有冷战/短句反应等（建议人工校验）\n")
    # additional personalities placeholders
    lines.append("---\n")
    lines.append("### 人格：angry（吵架）\n")
    lines.append("- Layer 0：在被冷落或感到不被重视时，可能采取已读不回/短句反驳。\n")
    lines.append("\n### 人格：drunk（醉酒）\n")
    lines.append("- Layer 0：醉酒时更容易表达真实感受，话多、情绪化。\n")

    lines.append("---\n")
    lines.append("## 人格切换简要策略\n")
    lines.append("- 包含生气关键词或短句/连续问句 → angry\n")
    lines.append("- 包含酒精或醉相关词 → drunk\n")
    lines.append("- 其他默认 → normal\n")
    return "\n".join(lines)


def call_skill_writer(base_dir, role, slug, name, memories_path, persona_path):
    cmd = ["python3", "tools/skill_writer.py", "--action", "create", "--base-dir", str(base_dir), "--role", role, "--slug", slug, "--name", name, "--memories", str(memories_path), "--persona", str(persona_path)]
    print("Calling:", " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--role", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--analysis-dir", required=True, help="directory containing memories.json and persona.json")
    p.add_argument("--base-dir", default="./personalities")
    args = p.parse_args()
    ad = Path(args.analysis_dir)
    memj = ad / "memories.json"
    perj = ad / "persona.json"
    if not memj.exists() or not perj.exists():
        print("analysis files missing. Run tools/simple_analyzer.py first to produce memories.json and persona.json")
        return
    mem_obj = json.loads(memj.read_text(encoding="utf-8"))
    per_obj = json.loads(perj.read_text(encoding="utf-8"))
    memories_md = render_memories(args.name, mem_obj)
    persona_md = render_persona(args.name, per_obj)
    outdir = Path(args.base_dir) / args.role / args.slug
    outdir.mkdir(parents=True, exist_ok=True)
    mem_path = outdir / "memories.md"
    per_path = outdir / "persona.md"
    mem_path.write_text(memories_md, encoding="utf-8")
    per_path.write_text(persona_md, encoding="utf-8")
    print("Wrote", mem_path, per_path)
    # call skill_writer to generate meta and SKILL.md
    call_skill_writer(Path(args.base_dir), args.role, args.slug, args.name, mem_path, per_path)

if __name__ == "__main__":
    main()
