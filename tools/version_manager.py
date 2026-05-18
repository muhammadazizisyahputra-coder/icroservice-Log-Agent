#!/usr/bin/env python3
"""
版本管理（最小实现）
Usage:
  python tools/version_manager.py --action backup --base-dir ./personalities --role ex --slug xiaomei
  python tools/version_manager.py --action list --base-dir ./personalities --role ex --slug xiaomei
  python tools/version_manager.py --action rollback --base-dir ./personalities --role ex --slug xiaomei --version v1
"""
import argparse
from pathlib import Path
import shutil
from datetime import datetime

def backup_skill(base_dir: Path, role: str, slug: str):
    skill_dir = base_dir / role / slug
    if not skill_dir.exists():
        print("Skill not found:", skill_dir)
        return
    versions_dir = skill_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    version_name = "v" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
    dst = versions_dir / version_name
    shutil.copytree(skill_dir, dst, ignore=shutil.ignore_patterns("versions"))
    print("Backed up to", dst.name)

def list_versions(base_dir: Path, role: str, slug: str):
    versions_dir = base_dir / role / slug / "versions"
    if not versions_dir.exists():
        print("No versions")
        return
    for v in sorted(versions_dir.iterdir()):
        print(v.name)

def rollback(base_dir: Path, role: str, slug: str, version: str):
    skill_dir = base_dir / role / slug
    version_dir = skill_dir / "versions" / version
    if not version_dir.exists():
        print("Version not found")
        return
    # backup current
    backup_skill(base_dir, role, slug)
    # copy files from version to current (exclude versions/)
    for item in version_dir.iterdir():
        if item.name == "versions": continue
        dst = skill_dir / item.name
        if dst.exists():
            if dst.is_dir(): shutil.rmtree(dst)
            else: dst.unlink()
        if item.is_dir():
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)
    print("Rolled back to", version)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--action", choices=["backup","list","rollback"], required=True)
    p.add_argument("--base-dir", default="./personalities")
    p.add_argument("--role", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--version")
    args = p.parse_args()
    base_dir = Path(args.base_dir)
    if args.action == "backup":
        backup_skill(base_dir, args.role, args.slug)
    elif args.action == "list":
        list_versions(base_dir, args.role, args.slug)
    elif args.action == "rollback":
        if not args.version:
            print("need --version")
            return
        rollback(base_dir, args.role, args.slug, args.version)

if __name__ == "__main__":
    main()
