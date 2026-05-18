#!/usr/bin/env python3
"""
demo.py
演示脚本：一键从聊天文本生成人格 Skill。
流程：
  1) 解析聊天文本（wechat_parser）
  2) 运行简单分析器（simple_analyzer）
  3) 运行 builder 生成 memories.md / persona.md 并创建 Skill

用法：
  python demo.py --file tests/_sample_chat.txt --target "小美" --role ex --slug xiaomei --name "小美"

结果：personalities/ex/xiaomei/ 下生成 Skill
"""
import argparse
from pathlib import Path
import subprocess
import json


def run_parser(file, target, out_json):
    cmd = ["python3", "tools/wechat_parser.py", "--file", str(file), "--target", target, "--output", str(out_json)]
    print("Parser:", " ".join(cmd))
    subprocess.check_call(cmd)

def run_analyzer(in_json, out_dir):
    cmd = ["python3", "tools/simple_analyzer.py", "--input", str(in_json), "--out-dir", str(out_dir)]
    print("Analyzer:", " ".join(cmd))
    subprocess.check_call(cmd)

def run_builder(role, slug, name, analysis_dir, base_dir):
    cmd = ["python3", "tools/builder.py", "--role", role, "--slug", slug, "--name", name, "--analysis-dir", str(analysis_dir), "--base-dir", base_dir]
    print("Builder:", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--role", default="ex")
    p.add_argument("--slug", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--work-dir", default="./tmp")
    p.add_argument("--base-dir", default="./personalities")
    args = p.parse_args()
    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    parsed = work / "parsed.json"
    run_parser(args.file, args.target, parsed)
    run_analyzer(parsed, work)
    run_builder(args.role, args.slug, args.name, work, args.base_dir)
    print("Demo complete. Check", Path(args.base_dir)/args.role/args.slug)
