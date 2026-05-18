#!/usr/bin/env python3
"""
简单规则分析器（最小实现）
输入：wechat_parser 输出的 JSON 文件（列表 of {sender, content, timestamp}）
输出：memories.json, persona.json（结构化）

注意：这是一个最小的启蒙版分析器，旨在在没有 LLM 的情况下生成可用的草稿。
真实项目建议用 LLM prompt（prompts/*.md）进行语义分析。
"""
from pathlib import Path
import json
import re
from collections import Counter, defaultdict

try:
    import jieba
except Exception:
    jieba = None

FOOD_KEYWORDS = ["吃", "火锅", "面", "饭", "早餐", "午饭", "晚饭", "奶茶", "甜点", "喜欢"]
ANGER_KEYWORDS = ["生气", "哼", "讨厌", "滚", "不理", "哎"]
LOVE_KEYWORDS = ["想你", "想见", "爱你", "喜欢你", "爱" ]


def load_messages(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return data


def top_words(messages, top_k=10):
    texts = "\n".join(m.get("content","") for m in messages)
    if jieba:
        words = [w for w in jieba.cut_for_search(texts) if len(w.strip())>1]
    else:
        # fallback simple split on non-chinese/letters
        words = re.findall(r"[\u4e00-\u9fff\w]{2,}", texts)
    cnt = Counter(words)
    return [w for w,_ in cnt.most_common(top_k)]


def extract_dates(messages):
    dates = set()
    date_re = re.compile(r"\d{4}[-/]\d{1,2}[-/]\d{1,2}")
    for m in messages:
        t = m.get("timestamp","")
        if t:
            m = date_re.search(t)
            if m:
                dates.add(m.group(0))
    return sorted(dates)


def extract_preferences(messages):
    foods = Counter()
    for m in messages:
        c = m.get("content","")
        for kw in FOOD_KEYWORDS:
            if kw in c:
                foods[kw]+=1
    return [k for k,_ in foods.most_common(5)]


def detect_conflict_patterns(messages):
    patterns = Counter()
    for m in messages:
        c = m.get("content","")
        for kw in ANGER_KEYWORDS:
            if kw in c:
                patterns[kw]+=1
    return [k for k,_ in patterns.most_common(5)]


def detect_expression_style(messages):
    # simple heuristics
    avg_len = 0
    cnt = 0
    emoji_like = 0
    exclam = 0
    for m in messages:
        c = m.get("content","")
        avg_len += len(c)
        cnt += 1
        if re.search(r"[\U0001F300-\U0001F6FF\u2600-\u26FF\u2700-\u27BF]", c):
            emoji_like += 1
        if "!" in c or "！" in c:
            exclam += 1
    avg_len = int(avg_len/cnt) if cnt else 0
    style = {
        "avg_len": avg_len,
        "emoji_freq": emoji_like,
        "exclaim_freq": exclam,
    }
    return style


def analyze(messages):
    # messages: list of dict
    mem = {}
    persona = {}
    mem["important_dates"] = extract_dates(messages)
    mem["daily_habits"] = []
    mem["special_moments"] = []
    mem["preferences"] = extract_preferences(messages)
    mem["conflict_signals"] = detect_conflict_patterns(messages)

    persona["top_words"] = top_words(messages, top_k=20)
    persona["expression_style"] = detect_expression_style(messages)
    # detect attachment / mood hints
    persona["love_signals"] = [kw for kw in LOVE_KEYWORDS if any(kw in m.get("content","") for m in messages)]
    persona["anger_signals"] = [kw for kw in ANGER_KEYWORDS if any(kw in m.get("content","") for m in messages)]

    # naive: count messages per sender to find who speaks more
    senders = Counter(m.get("sender","") for m in messages)
    persona["top_senders"] = [s for s,_ in senders.most_common(5)]

    # simple timeline: list first and last timestamps
    timestamps = [m.get("timestamp") for m in messages if m.get("timestamp")]
    if timestamps:
        mem["first_seen"] = timestamps[0]
        mem["last_seen"] = timestamps[-1]
    else:
        mem["first_seen"] = mem["last_seen"] = ""

    return mem, persona


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="wechat json produced by tools/wechat_parser.py")
    p.add_argument("--out-dir", default="./tmp")
    args = p.parse_args()
    inp = Path(args.input)
    msgs = load_messages(inp)
    mem, persona = analyze(msgs)
    outd = Path(args.out_dir)
    outd.mkdir(parents=True, exist_ok=True)
    (outd / "memories.json").write_text(json.dumps(mem, ensure_ascii=False, indent=2), encoding="utf-8")
    (outd / "persona.json").write_text(json.dumps(persona, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote memories.json and persona.json to", outd)
