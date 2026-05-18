#!/usr/bin/env python3
"""
最简微信解析器（支持 WechatExporter txt）
用法：
  python tools/wechat_parser.py --file chat.txt --target "小美" --output /tmp/wechat_out.json
"""
import argparse, json, re
from pathlib import Path


def parse_txt(path, target=None):
    msgs = []
    pattern = re.compile(r"^(?P<time>\d{4}[-/]\d{1,2}[-/]\d{1,2}[\s\d:]+)\s+(?P<sender>.+?)[:：]\s*(?P<content>.+)$")
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = pattern.match(line.strip())
        if m:
            sender = m.group("sender").strip()
            content = m.group("content").strip()
            time = m.group("time").strip()
            if target and target not in sender:
                continue
            msgs.append({"sender": sender, "content": content, "timestamp": time})
    return msgs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--target")
    p.add_argument("--output")
    args = p.parse_args()
    msgs = parse_txt(args.file, args.target)
    out = args.output or "/tmp/wechat_out.json"
    Path(out).write_text(json.dumps(msgs, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", out)

if __name__ == "__main__":
    main()
