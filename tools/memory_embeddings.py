#!/usr/bin/env python3
"""
记忆向量化（接口示例，依赖外部 embedding 选择）
实现建议：
- parse memories.md -> blocks
- embed blocks via chosen API -> save to memory_embeddings.json
- provide semantic_search(query, top_k)
"""
# 这里只写接口与示例函数签名，具体实现按你接入的 embedding 服务改写
from pathlib import Path
import json

def parse_memories(skill_dir: Path):
    """返回分块的记忆列表：[{"id":..., "section":..., "content":...}, ...]"""
    memories_file = Path(skill_dir) / "memories.md"
    if not memories_file.exists():
        return []
    content = memories_file.read_text(encoding="utf-8")
    blocks = []
    cur_section = None
    for line in content.splitlines():
        if line.startswith('## '):
            cur_section = line.replace('## ', '').strip()
        elif line.strip():
            blocks.append({"id": f"blk_{len(blocks)}", "section": cur_section or "general", "content": line.strip()})
    return blocks

def build_embeddings(skill_dir: Path, api_client=None):
    """对所有块进行向量化并保存 memory_embeddings.json（示例只保存文本）"""
    blocks = parse_memories(skill_dir)
    out = {"version":1, "blocks": blocks}
    (Path(skill_dir)/"memory_embeddings.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built embeddings placeholder for {len(blocks)} blocks")

def semantic_search(skill_dir: Path, query: str, top_k=3):
    """示例：加载 memory_embeddings.json 并返回 top_k 文本块（按简单包含优先）"""
    emb_file = Path(skill_dir)/"memory_embeddings.json"
    if not emb_file.exists():
        return []
    data = json.loads(emb_file.read_text(encoding="utf-8"))
    blocks = data.get("blocks", [])
    # very naive ranking: substring match score
    scored = []
    for b in blocks:
        score = 1.0 if query in b.get("content","") else 0.0
        scored.append((score, b))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [b for s,b in scored[:top_k]]
