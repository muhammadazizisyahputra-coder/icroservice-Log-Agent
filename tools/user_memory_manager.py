#!/usr/bin/env python3
"""
用户长期记忆管理（最小）
Usage:
  python tools/user_memory_manager.py --action get --skill-dir ./personalities/ex/xiaomei --user-id user123
  python tools/user_memory_manager.py --action record --skill-dir ./personalities/ex/xiaomei --user-id user123 --user-msg "我刚下班" --ai-resp "欢迎回家"
"""
import argparse, json
from pathlib import Path
from datetime import datetime

def get_memory(skill_dir: Path, user_id: str):
    d = Path(skill_dir) / "user_memories"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{user_id}.json"
    if not f.exists():
        return {}
    return json.loads(f.read_text(encoding="utf-8"))

def record_interaction(skill_dir: Path, user_id: str, user_msg: str, ai_resp: str):
    d = Path(skill_dir) / "user_memories"
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{user_id}.json"
    mem = get_memory(skill_dir, user_id) or {"user_id": user_id, "created_at": datetime.utcnow().isoformat()+"Z", "conversation": []}
    mem["conversation"].append({"ts": datetime.utcnow().isoformat()+"Z", "user": user_msg, "ai": ai_resp})
    # keep last 200
    mem["conversation"] = mem["conversation"][-200:]
    f.write_text(json.dumps(mem, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Recorded interaction")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--action", choices=["get","record"], required=True)
    p.add_argument("--skill-dir", required=True)
    p.add_argument("--user-id", required=True)
    p.add_argument("--user-msg")
    p.add_argument("--ai-resp")
    args = p.parse_args()
    if args.action == "get":
        print(json.dumps(get_memory(Path(args.skill_dir), args.user_id), ensure_ascii=False, indent=2))
    else:
        record_interaction(Path(args.skill_dir), args.user_id, args.user_msg or "", args.ai_resp or "")

if __name__ == "__main__":
    main()
