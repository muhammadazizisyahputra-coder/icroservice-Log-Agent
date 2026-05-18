#!/usr/bin/env python3
"""
简易 Skill 写入器（最小实现）
用法：
  python tools/skill_writer.py --action create --base-dir ./personalities --role ex --slug xiaomei \
    --name "小美" --memories ./tmp/memories.md --persona ./tmp/persona.md
  python tools/skill_writer.py --action list --base-dir ./personalities
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

SKILL_MD_TEMPLATE = """---
name: {role}_{slug}
description: {name}，{identity}
user-invocable: true
---

# {name}

{identity}

---

## PART A：共同记忆

{memories}

---

## PART B：人物性格

{persona}

---
"""


def slugify(s: str) -> str:
    return s.strip().replace(" ", "-").lower()

def write_files(base_dir: Path, role: str, slug: str, name: str, memories_path: Path, persona_path: Path):
    dest = base_dir / role / slug
    dest.mkdir(parents=True, exist_ok=True)
    # copy memories and persona
    memories_text = memories_path.read_text(encoding="utf-8") if memories_path.exists() else ""
    persona_text = persona_path.read_text(encoding="utf-8") if persona_path.exists() else ""
    (dest / "memories.md").write_text(memories_text, encoding="utf-8")
    (dest / "persona.md").write_text(persona_text, encoding="utf-8")
    # meta.json
    meta = {
        "name": name,
        "slug": slug,
        "role_type": role,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "version": "v1",
    }
    (dest / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    # SKILL.md
    identity = meta.get("role_type", "") + " " + name
    skill_md = SKILL_MD_TEMPLATE.format(role=role, slug=slug, name=name, identity=identity, memories=memories_text, persona=persona_text)
    (dest / "SKILL.md").write_text(skill_md, encoding="utf-8")
    print(f"Created skill at: {dest}")

def list_skills(base_dir: Path):
    if not base_dir.exists():
        print("No skills found.")
        return
    for role_dir in base_dir.iterdir():
        if not role_dir.is_dir(): continue
        for slug_dir in role_dir.iterdir():
            if not slug_dir.is_dir(): continue
            meta = slug_dir / "meta.json"
            name = slug_dir.name
            if meta.exists():
                try:
                    import json
                    data = json.loads(meta.read_text(encoding="utf-8"))
                    name = data.get("name", name)
                except Exception:
                    pass
            print(f"{role_dir.name}/{slug_dir.name} - {name}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--action", choices=["create", "list"], required=True)
    p.add_argument("--base-dir", default="./personalities")
    p.add_argument("--role")
    p.add_argument("--slug")
    p.add_argument("--name")
    p.add_argument("--memories")
    p.add_argument("--persona")
    args = p.parse_args()

    base_dir = Path(args.base_dir)
    if args.action == "create":
        if not args.role or not args.slug or not args.name:
            print("create requires --role --slug --name")
            return
        write_files(base_dir, args.role, args.slug, args.name, Path(args.memories or ""), Path(args.persona or ""))
    elif args.action == "list":
        list_skills(base_dir)

if __name__ == "__main__":
    main()
