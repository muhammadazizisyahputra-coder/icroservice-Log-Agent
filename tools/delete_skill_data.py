#!/usr/bin/env python3
"""
Delete skill data and related inputs safely.

This script helps comply with data deletion obligations (PIPL). It can delete:
- a specific skill directory (personalities/{role}/{slug})
- all skills under personalities/ (use with --all and --yes)
- input directory (e.g., input/) if present
- a specific user memory file under a skill's user_memories

Usage examples:
  # Delete a skill (requires confirmation)
  python3 tools/delete_skill_data.py --role ex --slug xiaomei --yes --reason "user requested deletion"

  # Delete a user's memory for a skill
  python3 tools/delete_skill_data.py --role ex --slug xiaomei --user-id user123 --yes

  # Delete everything (DANGEROUS)
  python3 tools/delete_skill_data.py --all --yes --reason "test cleanup"

Note: This script logs deletions to deletions.log in the project root.
"""
import argparse
from pathlib import Path
import shutil
from datetime import datetime
import json

LOG_FILE = Path("deletions.log")
PROJECT_ROOT = Path('.')
PERSONALITIES_DIR = Path('personalities')
INPUT_DIR = Path('input')


def log_deletion(entry: dict):
    entry['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    s = json.dumps(entry, ensure_ascii=False)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(s + '\n')


def delete_skill(role: str, slug: str):
    path = PERSONALITIES_DIR / role / slug
    if not path.exists():
        print('Skill not found:', path)
        return False
    shutil.rmtree(path)
    print('Deleted', path)
    return True


def delete_user_memory(role: str, slug: str, user_id: str):
    path = PERSONALITIES_DIR / role / slug / 'user_memories' / f'{user_id}.json'
    if not path.exists():
        print('User memory not found:', path)
        return False
    path.unlink()
    print('Deleted user memory', path)
    return True


def delete_input_dir():
    if INPUT_DIR.exists():
        shutil.rmtree(INPUT_DIR)
        print('Deleted input dir', INPUT_DIR)
        return True
    print('Input dir not found')
    return False


def delete_all_personalities():
    if PERSONALITIES_DIR.exists():
        shutil.rmtree(PERSONALITIES_DIR)
        print('Deleted all personalities')
        return True
    print('No personalities directory')
    return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--role')
    p.add_argument('--slug')
    p.add_argument('--user-id')
    p.add_argument('--all', action='store_true')
    p.add_argument('--yes', action='store_true', help='Confirm deletion')
    p.add_argument('--reason', help='Reason for deletion (optional)')
    args = p.parse_args()

    if not args.yes:
        print('Danger: deletion requires --yes to confirm')
        return

    entry = {
        'action': None,
        'role': args.role,
        'slug': args.slug,
        'user_id': args.user_id,
        'reason': args.reason,
    }

    try:
        if args.all:
            entry['action'] = 'delete_all'
            ok = delete_all_personalities()
            input_ok = delete_input_dir()
            entry['result'] = {'skills_deleted': ok, 'input_deleted': input_ok}
            log_deletion(entry)
            return

        if args.role and args.slug and args.user_id:
            entry['action'] = 'delete_user_memory'
            ok = delete_user_memory(args.role, args.slug, args.user_id)
            entry['result'] = {'user_memory_deleted': ok}
            log_deletion(entry)
            return

        if args.role and args.slug:
            entry['action'] = 'delete_skill'
            ok = delete_skill(args.role, args.slug)
            entry['result'] = {'skill_deleted': ok}
            log_deletion(entry)
            return

        # fallback: delete input dir only if exists
        if INPUT_DIR.exists():
            entry['action'] = 'delete_input_dir'
            ok = delete_input_dir()
            entry['result'] = {'input_deleted': ok}
            log_deletion(entry)
            return

        print('No valid deletion target provided')
    except Exception as e:
        entry['error'] = str(e)
        log_deletion(entry)
        raise

if __name__ == '__main__':
    main()
