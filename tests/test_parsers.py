from tools.wechat_parser import parse_txt

def test_parse_txt(tmp_path):
    sample = "2026-05-01 12:00 小美: 你好\n"
    p = tmp_path / "sample.txt"
    p.write_text(sample, encoding="utf-8")
    msgs = parse_txt(str(p), "小美")
    assert isinstance(msgs, list)
    assert msgs and "小美" in msgs[0]["sender"]
