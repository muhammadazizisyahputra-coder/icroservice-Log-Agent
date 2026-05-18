#!/usr/bin/env python3
"""
LLM Renderer for Persona and Memories using Mimo (OpenAI-compatible) API.

- Reads analysis JSON (memories.json & persona.json) or raw parsed messages JSON,
  applies basic sanitization (phone, id, email, url, addresses),
  constructs prompts from templates under prompts/, and calls the LLM to render
  high-quality memories.md and persona.md outputs.

Usage examples:
  # Use analysis outputs
  python3 tools/llm_renderer.py --analysis-dir ./tmp --prompts-dir ./prompts --out-dir ./tmp --model mimo-v2.5-pro

  # Use raw parsed messages
  python3 tools/llm_renderer.py --input ./tmp/parsed.json --prompts-dir ./prompts --out-dir ./tmp --model mimo-v2.5-pro

Environment:
  Provide API key in env var MIMO_API_KEY (or OPENAI_API_KEY fallback).

Note: This is a convenience wrapper. It performs basic local redaction before sending
content to the LLM. For production use, enhance redaction and implement privacy review.
"""
import argparse
import json
import os
import re
from pathlib import Path
from typing import List

try:
    import openai
except Exception:
    openai = None

REDACT_PHONE = "[PHONE_REDACTED]"
REDACT_ID = "[ID_REDACTED]"
REDACT_EMAIL = "[EMAIL_REDACTED]"
REDACT_URL = "[URL_REDACTED]"
REDACT_ADDRESS = "[ADDRESS_REDACTED]"

PHONE_RE = re.compile(r"(?:(?:\+?86)?1[3-9]\d{9})")
ID_RE = re.compile(r"\b\d{17}[0-9Xx]|\d{15}\b")
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+")
URL_RE = re.compile(r"https?://[\w\./%-]+")
# crude address pattern: contains province/city/district/road/street/号/楼
ADDR_KEYWORDS = ["省", "市", "区", "县", "镇", "路", "街", "巷", "号", "栋", "楼", "乡", "街道"]
ADDR_RE = re.compile(r"[\u4e00-\u9fff0-9a-zA-Z\-]{2,50}(?:省|市|区|县|路|街|巷|号|栋|楼|乡|街道)")


def sanitize_text(text: str) -> str:
    if not text:
        return text
    s = str(text)
    # phone
    s = PHONE_RE.sub(REDACT_PHONE, s)
    # id
    s = ID_RE.sub(REDACT_ID, s)
    # email
    s = EMAIL_RE.sub(REDACT_EMAIL, s)
    # url
    s = URL_RE.sub(REDACT_URL, s)
    # address heuristics
    s = ADDR_RE.sub(REDACT_ADDRESS, s)
    return s


def sanitize_messages(messages: List[dict]) -> List[dict]:
    out = []
    for m in messages:
        nm = dict(m)
        nm["content"] = sanitize_text(m.get("content", ""))
        # also sanitize sender if needed
        nm["sender"] = sanitize_text(m.get("sender", ""))
        out.append(nm)
    return out


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_prompts(prompts_dir: Path):
    # load memories_builder and persona_builder as text
    pb = {}
    for name in ["memories_builder.md", "persona_builder.md", "personality_selector.md"]:
        p = prompts_dir / name
        if p.exists():
            pb[name] = p.read_text(encoding="utf-8")
        else:
            pb[name] = ""
    return pb


def build_system_prompt(prompts: dict) -> str:
    # Combine core instructions; keep concise
    parts = ["You are a persona distillation assistant. Follow the templates strictly."]
    if prompts.get("memories_builder.md"):
        parts.append("Memories template:\n" + prompts["memories_builder.md"][:2000])
    if prompts.get("persona_builder.md"):
        parts.append("Persona template:\n" + prompts["persona_builder.md"][:2000])
    return "\n\n".join(parts)


def call_llm(prompt_messages: List[dict], model: str, api_key: str, temperature: float = 0.3) -> str:
    if openai is None:
        raise RuntimeError("openai package is not installed. Please install openai in your environment.")
    openai.api_key = api_key
    # Use ChatCompletion API
    try:
        resp = openai.ChatCompletion.create(model=model, messages=prompt_messages, temperature=temperature)
        content = resp["choices"][0]["message"]["content"]
        return content
    except Exception as e:
        raise


def construct_prompt_from_analysis(mem_obj: dict, per_obj: dict, prompts: dict, messages_sample: List[dict]) -> List[dict]:
    system = build_system_prompt(prompts)
    user_parts = []
    user_parts.append("Here are analysis results (JSON). Use the templates to generate two sections: start the memories section with the marker --MEMORIES-- on its own line, and start the persona section with the marker --PERSONA-- on its own line. Respond ONLY with those two sections separated by the markers.")
    user_parts.append("Analysis JSON for memories:\n" + json.dumps(mem_obj, ensure_ascii=False, indent=2)[:4000])
    user_parts.append("Analysis JSON for persona:\n" + json.dumps(per_obj, ensure_ascii=False, indent=2)[:4000])
    # include a small sample of sanitized messages for context (up to 10 messages)
    sample_texts = []
    for m in messages_sample[:10]:
        sample_texts.append(f"[{m.get('timestamp','')}] {m.get('sender','')}: {m.get('content','')}")
    user_parts.append("Recent messages (sanitized):\n" + "\n".join(sample_texts))
    user_message = "\n\n".join(user_parts)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message}
    ]
    return messages


def split_llm_output(output: str):
    # Expect markers --MEMORIES-- and --PERSONA--
    mem_marker = "--MEMORIES--"
    per_marker = "--PERSONA--"
    mem = ""
    per = ""
    if mem_marker in output and per_marker in output:
        try:
            mem_part = output.split(mem_marker,1)[1]
            per_part = mem_part.split(per_marker,1)
            mem = per_part[0].strip()
            per = per_part[1].strip() if len(per_part)>1 else ""
        except Exception:
            mem = output
            per = ""
    else:
        # fallback: try to split by headings or return entire as memories
        mem = output
        per = ""
    return mem, per


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--analysis-dir", help="directory with memories.json and persona.json")
    p.add_argument("--input", help="raw parsed messages json (list of {sender,content,timestamp})")
    p.add_argument("--prompts-dir", default="./prompts")
    p.add_argument("--out-dir", default="./tmp")
    p.add_argument("--model", default="mimo-v2.5-pro")
    p.add_argument("--api-key-env", default="MIMO_API_KEY")
    p.add_argument("--temperature", type=float, default=0.3)
    args = p.parse_args()

    api_key = os.getenv(args.api_key_env) or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print(f"Error: API key not found in env {args.api_key_env} or OPENAI_API_KEY")
        return

    prompts_dir = Path(args.prompts_dir)
    prompts = load_prompts(prompts_dir)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mem_obj = {}
    per_obj = {}
    messages_sample = []

    if args.analysis_dir:
        ad = Path(args.analysis_dir)
        mem_obj = load_json(ad / "memories.json") or {}
        per_obj = load_json(ad / "persona.json") or {}
        # try to load parsed messages
        parsed = ad / "parsed.json"
        if parsed.exists():
            messages = load_json(parsed) or []
            messages_sample = sanitize_messages(messages)
    elif args.input:
        inp = Path(args.input)
        messages = load_json(inp) or []
        messages_sample = sanitize_messages(messages)
        # minimal analysis: include the sanitized messages as context
        mem_obj = {"notes":"Generated from input messages (sanitized)", "important_dates":[]}
        per_obj = {"notes":"Generated from input messages (sanitized)"}
    else:
        print("Either --analysis-dir or --input must be provided")
        return

    # sanitize any text inside mem_obj and per_obj
    mem_json_text = json.dumps(mem_obj, ensure_ascii=False)
    per_json_text = json.dumps(per_obj, ensure_ascii=False)
    mem_json_text = sanitize_text(mem_json_text)
    per_json_text = sanitize_text(per_json_text)
    # reload sanitized objects
    try:
        mem_obj = json.loads(mem_json_text)
        per_obj = json.loads(per_json_text)
    except Exception:
        # if JSON fails, keep original
        pass

    # prepare prompt
    prompt_messages = construct_prompt_from_analysis(mem_obj, per_obj, prompts, messages_sample)

    print("Calling LLM model", args.model)
    try:
        output = call_llm(prompt_messages, model=args.model, api_key=api_key, temperature=args.temperature)
    except Exception as e:
        print("LLM call failed:", e)
        print("Falling back to local builder is recommended.")
        return

    mem_text, per_text = split_llm_output(output)

    # if outputs empty, fallback to local building
    if not mem_text.strip() or not per_text.strip():
        print("Warning: LLM did not return both sections. Saving raw output to out_dir/raw_llm.txt")
        (out_dir / "raw_llm.txt").write_text(output, encoding="utf-8")

    if mem_text.strip():
        (out_dir / "memories.md").write_text(mem_text, encoding="utf-8")
        print("Wrote", out_dir / "memories.md")
    if per_text.strip():
        (out_dir / "persona.md").write_text(per_text, encoding="utf-8")
        print("Wrote", out_dir / "persona.md")

    # also save sanitized sample and analysis to out_dir
    if messages_sample:
        (out_dir / "sanitized_messages.json").write_text(json.dumps(messages_sample, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "sanitized_analysis.json").write_text(json.dumps({"memories": mem_obj, "persona": per_obj}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("LLM rendering complete. You can review and then run tools/skill_writer.py to create the skill.")

if __name__ == "__main__":
    main()
